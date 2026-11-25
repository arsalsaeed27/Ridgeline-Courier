"""First comparison of the search algorithms on 30 small instances (where all of them finish).

Instances: oel/experiments/small_instances.py, a 7x7 window around the depot (radius 3), 1-3 stops,
hills ON, fuel OFF (with fuel ON or a 9x9 window IDS runs out of its 500k-node budget on some
instances; see the viva notes). Per instance we run:
  bfs, ucs, dls(limit = d*), dls(limit = d* - 1), ids(max_depth 30), greedy(h_zero), astar(h_zero)
where d* = the fewest moves, found by BFS. DLS at d* must succeed and at d* - 1 must report "cutoff".

Note on node counts: BFS tests the goal when a state is GENERATED, UCS / Greedy / A* when it is
POPPED, DLS / IDS when it is visited. So "nodes expanded" is not measured at exactly the same moment
for every algorithm (BFS stops one layer early); the table's goal_test column says which.
Means are reported with a 95% percentile-bootstrap CI (seeded): node counts are very skewed, so
a t interval would even go below 0.
Outputs: results/tables/search_uninformed_small{,_runs}.{csv,md}
"""
from __future__ import annotations

import time

import pandas as pd

from oel.experiments.small_instances import small_instances
from oel.config import BASE_SEED
from oel.experiments.stats import bootstrap_mean_ci, wilson_ci
from oel.search.heuristics import h_zero
from oel.search.informed import astar, greedy
from oel.search.result import run_timed
from oel.search.uninformed import bfs, dls, ids, ucs
from oel.stamp import save_table
from oel.world.constraints import PlanConstraints, verify_plan
from oel.world.problem import DeliveryProblem

N_INSTANCES = 30
BUDGET = {"node_limit": 500_000, "time_limit": 20.0}
ORDER = ["bfs", "ucs", "dls(d*)", "dls(d*-1)", "ids", "greedy(h_zero)", "astar(h_zero)"]


def run_instance(i, cfg) -> list:
    problem = DeliveryProblem(cfg)
    b = run_timed(bfs, problem, measure_memory=False)
    d_star = b.stats["steps"]
    runs = {
        "bfs": b,
        "ucs": run_timed(ucs, problem, measure_memory=False),
        "dls(d*)": run_timed(dls, problem, measure_memory=False, limit=d_star, **BUDGET),
        "dls(d*-1)": run_timed(dls, problem, measure_memory=False, limit=d_star - 1, **BUDGET),
        "ids": run_timed(ids, problem, measure_memory=False, max_depth=30, **BUDGET),
        "greedy(h_zero)": run_timed(greedy, problem, measure_memory=False, heuristic=h_zero),
        "astar(h_zero)": run_timed(astar, problem, measure_memory=False, heuristic=h_zero),
    }
    optimum = runs["ucs"].cost
    rows = []
    for name, r in runs.items():
        valid = r.solved and not verify_plan(r.actions, PlanConstraints(), cfg)
        rows.append({"instance": i, "stops": len(cfg.stops), "d_star": d_star, "algorithm": name,
                     "solved": r.solved, "valid_plan": valid if r.solved else None,
                     "reason": r.stats.get("reason", "solved"), "goal_test": r.stats.get("goal_test"),
                     "nodes": r.nodes_expanded, "runtime_ms": 1000 * r.runtime_s,
                     "max_frontier": r.max_frontier,
                     "cost": r.cost if r.solved else None,
                     "steps": len(r.actions) if r.solved else None,
                     "cost_over_optimal": r.cost / optimum if r.solved else None})
    return rows


def summarise(runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in ORDER:
        g = runs[runs.algorithm == name]
        solved = g[g.solved]
        lo, hi = wilson_ci(len(solved), len(g))

        def fmt(values, digits=1):
            mean, low, high = bootstrap_mean_ci(values, seed=BASE_SEED)
            return f"{mean:.{digits}f} [{low:.{digits}f}, {high:.{digits}f}]" if len(values) else "-"
        reasons = g.reason.value_counts().to_dict()
        rows.append({
            "algorithm": name, "goal_test": g.goal_test.iloc[0], "runs": len(g),
            "solved_pct": f"{100 * len(solved) / len(g):.0f} [{100 * lo:.0f}, {100 * hi:.0f}]",
            "mean_nodes": fmt(g.nodes), "mean_runtime_ms": fmt(g.runtime_ms, 2),
            "mean_max_frontier": fmt(g.max_frontier), "mean_cost_solved": fmt(solved.cost),
            "mean_cost_over_optimal": fmt(solved.cost_over_optimal, 3),
            "outcomes": ", ".join(f"{k}: {v}" for k, v in reasons.items()),
        })
    return pd.DataFrame(rows)


def run(cfg, log):
    t0 = time.perf_counter()
    instances = small_instances(N_INSTANCES, radius=3, use_fuel=False, use_hills=cfg.use_hills,
                                use_tunnels=cfg.use_tunnels)
    rows = []
    for i, inst in enumerate(instances):
        rows += run_instance(i, inst)
    runs = pd.DataFrame(rows)
    summary = summarise(runs)
    save_table(summary, "search_uninformed_small")
    save_table(runs, "search_uninformed_small_runs")
    log.info("search on %d small instances (%.0f s); values are mean [95%% CI]:\n%s",
             N_INSTANCES, time.perf_counter() - t0, summary.to_string(index=False))
    bad = runs[(runs.solved) & (runs.valid_plan == False)]   # noqa: E712 (pandas)
    if len(bad):
        log.warning("%d returned plans FAILED verify_plan", len(bad))
    return summary


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("search_small"))
