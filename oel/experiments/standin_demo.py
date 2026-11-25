"""End-to-end pipeline demo: plan with the default planner (A* + h_ours + fuel pruning; UCS until
Turn 2 session 3), then simulate. (File name kept from Turn 1.)

plan (perfect model) -> execute in the simulator (slip + rival) with rejoin/full replanning
-> results/figures/standin_route.png and results/tables/standin_summary.{csv,md}
"""
import numpy as np
import pandas as pd

from oel.search.registry import DEFAULT_LABEL, default_planner
from oel.search.result import run_timed
from oel.search.uninformed import ucs
from oel.stamp import save_table
from oel.world.plots import plot_route
from oel.world.problem import DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator


def run(cfg, log):
    problem = DeliveryProblem(cfg)

    # tracemalloc makes search ~2-3x slower, so the quick run skips the memory measurement
    plan = run_timed(default_planner, problem, measure_memory=not cfg.quick)
    if not plan.solved:
        log.warning("%s found no plan", DEFAULT_LABEL)
        return None
    log.info("%s: cost %.0f, %d actions, %d nodes, %.2f s", DEFAULT_LABEL,
             plan.cost, len(plan.actions), plan.nodes_expanded, plan.runtime_s)

    sim = Simulator(cfg, problem, np.random.default_rng(cfg.seed))
    # full replans: the default planner. Rejoin stays UCS: its goal is "back on the plan", for
    # which h_ours (an estimate of delivering everything) is not a valid heuristic.
    replanner = RejoinReplanner(full_planner=default_planner, rejoin_planner=ucs, radius=cfg.rejoin_radius)
    report = sim.run_plan(plan.actions, replan_fn=replanner)
    for r in report.replans:
        log.info("replan at step %d: %s (%d nodes, %.2f s)", r["step"], r["kind"], r["nodes"], r["runtime_s"])
    log.info("simulation: %s (%s), cost %.0f (planned %.0f, extra %s), %d steps, %d slips",
             report.outcome, report.end_reason, report.total_cost, report.planned_cost,
             report.extra_cost_text(), report.steps, report.slips)

    planned_cells = [s[:2] for s in plan.path]
    title = (f"{DEFAULT_LABEL} route: planned cost {plan.cost:.0f}; simulated (slip {cfg.slip}) "
             f"{report.outcome}, cost {report.total_cost:.0f}")
    fig_path = plot_route(cfg, report.agent_path, report.rival_path, planned_cells, title)

    row = {
        "planner": DEFAULT_LABEL,
        "hills": cfg.use_hills, "fuel": cfg.use_fuel, "tunnels": cfg.use_tunnels,
        "slip": cfg.slip, "seed": cfg.seed, "fuel_reserve": cfg.fuel_reserve,
        "planned_cost": plan.cost, "nodes_expanded": plan.nodes_expanded,
        "max_frontier": plan.max_frontier, "plan_runtime_s": round(plan.runtime_s, 2),
        "peak_mem_kb": round(plan.peak_mem_kb) if not cfg.quick else "not measured (--quick)",
        "outcome": report.outcome, "end_reason": report.end_reason,
        "actual_cost": report.total_cost, "extra_cost": report.extra_cost_text(),
        "steps": report.steps, "slips": report.slips, "failed_moves": report.failed_moves,
        "waits": report.waits, "replans_rejoin": report.n_rejoin, "replans_full": report.n_full,
    }
    table = pd.DataFrame([row])
    csv_path, _md_path = save_table(table, "standin_summary")
    log.info("saved %s and %s", fig_path.name, csv_path.name)
    return report
