"""Part B heuristic evaluation: admissibility, consistency, main comparison, ablation.

1. Admissibility: h(s) <= h*(s) on sampled states, where h*(s) is the TRUE cost-to-go computed by
   UCS from s (fuel-dominance pruning on the full map, which keeps UCS exact and makes it fast).
   Settings: 30 small instances with fuel OFF, 30 with fuel ON, and the full map (random walks
   from the depot + states next to every tunnel entrance, where h_manhattan_raw goes wrong).
2. Consistency: along every edge s -> s' that A* generates, check h(s) <= c(s, s') + h(s').
3. Main comparison on the full map (hills ON, all twists; planning reserve 0 and 20).
4. Ablation of h_ours on the full map (reserve 0).
Outputs (stamped): results/tables/heuristic_{admissibility,consistency,comparison,ablation}
and results/figures/heuristic_nodes.png
"""
from __future__ import annotations

import dataclasses
import math
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.config import BASE_SEED, parse_cli
from oel.experiments.small_instances import small_instances
from oel.search.heuristics import (h_farthest, h_manhattan, h_manhattan_raw, h_mst, h_ours,
                                   h_ours_no_hills, h_ours_no_tunnels)
from oel.search.informed import astar, greedy
from oel.search.result import run_timed
from oel.search.uninformed import ucs
from oel.stamp import save_fig, save_table
from oel.world.problem import DeliveryProblem

# ablation variants (h_ours_no_tunnels, h_ours_no_hills) live in heuristics.py

CHECKED = {"h_manhattan_raw": h_manhattan_raw, "h_manhattan": h_manhattan, "h_farthest": h_farthest,
           "h_mst": h_mst, "h_ours": h_ours, "h_ours_no_tunnels": h_ours_no_tunnels,
           "h_ours_no_hills": h_ours_no_hills}
SERIES = "#2a78d6"
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"


# ---------------------------------------------------------------- 1. admissibility
def _random_walk_states(problem, rng, k: int, max_len: int) -> list:
    """k reachable states: random legal moves from the start (the start itself is always included)."""
    states = [problem.initial_state()]
    for _ in range(k):
        state = problem.initial_state()
        for _step in range(int(rng.integers(1, max_len + 1))):
            moves = problem.actions(state)
            if not moves or problem.is_goal(state):
                break
            state = problem.result(state, moves[int(rng.integers(len(moves)))])
        if not problem.is_goal(state):
            states.append(state)
    return states


def _tunnel_states(problem) -> list:
    """States right next to each tunnel entrance where the ONLY undelivered stop is the one nearest
    to the tunnel's far end (full tank): there the tunnel is a huge shortcut, which is exactly
    where ignoring tunnels makes a Manhattan estimate overshoot."""
    out = []
    everything = (1 << len(problem.stops)) - 1
    for end, far_end in problem._tunnel_exit.items():
        near_far = min(range(len(problem.stops)),
                       key=lambda i: abs(problem.stops[i][0] - far_end[0]) + abs(problem.stops[i][1] - far_end[1]))
        mask = everything & ~(1 << near_far)          # all delivered except that stop
        for action in ("N", "S", "E", "W"):
            t = problem.transition(end, action)
            if t is not None and t[0] not in problem.stops:
                out.append((t[0][0], t[0][1], mask, problem.capacity))
                break
    return out


def _true_cost(problem, state, prune: bool) -> float:
    return ucs(problem.replan_from(state), prune_dominated=prune).cost


def admissibility(quick: bool, log) -> pd.DataFrame:
    rng = np.random.default_rng(BASE_SEED + 2000)
    settings = []
    for fuel in (False, True):
        for cfg in small_instances(30, radius=3, use_fuel=fuel):
            p = DeliveryProblem(cfg)
            settings.append((f"small, fuel {'ON' if fuel else 'OFF'}", p,
                             _random_walk_states(p, rng, 10, 15), False))
    full = DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))
    n_full = 10 if quick else 30
    settings.append(("full map", full, _random_walk_states(full, rng, n_full, 60) + _tunnel_states(full), True))

    counts = {}   # (setting, heuristic) -> [states, violations, max_over, sum_ratio, n_ratio]
    for setting, p, states, prune in settings:
        for s in states:
            h_star = _true_cost(p, s, prune)
            if math.isinf(h_star):
                continue                       # dead state: any h is <= infinity
            for name, h in CHECKED.items():
                value = h(s, p)
                c = counts.setdefault((setting, name), [0, 0, 0.0, 0.0, 0])
                c[0] += 1
                if value > h_star + 1e-9:
                    c[1] += 1
                    c[2] = max(c[2], value - h_star)
                if h_star > 0:
                    c[3] += value / h_star
                    c[4] += 1
    rows = [{"setting": setting, "heuristic": name, "states": c[0], "violations": c[1],
             "violation_pct": round(100 * c[1] / c[0], 1) if c[0] else 0.0,
             "max_overestimate": round(c[2], 1), "mean_h_over_hstar": round(c[3] / c[4], 3) if c[4] else None}
            for (setting, name), c in counts.items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 2. consistency
class EdgeChecker:
    """Wraps a problem; every time A* asks for successors it checks h(s) <= c(s,s') + h(s')."""

    def __init__(self, problem, heuristic):
        self.problem, self.h = problem, heuristic
        self.edges = self.violations = 0
        self.worst = 0.0

    def __getattr__(self, name):          # everything else behaves like the real problem
        return getattr(self.problem, name)

    def successors(self, state):
        out = self.problem.successors(state)
        h_s = self.h(state, self.problem)
        for _action, nxt, cost in out:
            self.edges += 1
            gap = h_s - (cost + self.h(nxt, self.problem))
            if gap > 1e-9:
                self.violations += 1
                self.worst = max(self.worst, gap)
        return out


def consistency(quick: bool) -> pd.DataFrame:
    scopes = [("small, fuel ON (30)", [DeliveryProblem(c) for c in small_instances(30, radius=3, use_fuel=True)])]
    full_names = ["h_mst", "h_ours"] if quick else ["h_manhattan_raw", "h_manhattan", "h_farthest", "h_mst", "h_ours"]
    rows = []
    for name in ["h_manhattan_raw", "h_manhattan", "h_farthest", "h_mst", "h_ours"]:
        h = CHECKED[name]
        problems = list(scopes[0][1])
        groups = [(scopes[0][0], problems)]
        if name in full_names:
            groups.append(("full map, reserve 0", [DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))]))
        for scope, probs in groups:
            edges = violations = 0
            worst = 0.0
            for p in probs:
                checker = EdgeChecker(p, h)
                astar(checker, heuristic=h)
                edges += checker.edges
                violations += checker.violations
                worst = max(worst, checker.worst)
            rows.append({"heuristic": name, "scope": scope, "edges_checked": edges,
                         "violations": violations, "violation_pct": round(100 * violations / edges, 3) if edges else 0.0,
                         "largest_violation": round(worst, 1)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 3. main comparison
PLANNERS = [
    ("UCS", ucs, {}),
    ("A* + h_manhattan", astar, {"heuristic": h_manhattan}),
    ("A* + h_farthest", astar, {"heuristic": h_farthest}),
    ("A* + h_mst", astar, {"heuristic": h_mst}),
    ("A* + h_ours", astar, {"heuristic": h_ours}),
    ("Greedy + h_ours", greedy, {"heuristic": h_ours}),
    ("A* + h_ours + fuel pruning", astar, {"heuristic": h_ours, "prune_dominated": True}),
]


def comparison(quick: bool, log) -> pd.DataFrame:
    rows = []
    for reserve in (0, 20):
        cfg = parse_cli(["--fuel-reserve", str(reserve)])
        optimum = None
        for name, planner, kwargs in PLANNERS:
            res = run_timed(planner, DeliveryProblem(cfg), measure_memory=not quick, **kwargs)
            if name == "UCS":
                optimum = res.cost
            rows.append({"reserve": reserve, "planner": name, "cost": res.cost,
                         "optimal": "yes" if res.cost == optimum else "no",
                         "nodes_expanded": res.nodes_expanded, "max_frontier": res.max_frontier,
                         "reopenings": res.stats.get("reopened", "-"),
                         "pruned": res.stats.get("pruned", "-"),
                         "runtime_s": round(res.runtime_s, 2),
                         "peak_mem_mb": round(res.peak_mem_kb / 1024, 1) if not quick else "not measured (--quick)"})
            log.info("reserve %d %-28s cost %.0f nodes %d (%.1f s)", reserve, name, res.cost,
                     res.nodes_expanded, res.runtime_s)
    return pd.DataFrame(rows)


def plot_nodes(df: pd.DataFrame):
    """Nodes expanded per planner, log scale, one panel per reserve (shared axis, no dual axis)."""
    reserves = sorted(df.reserve.unique())
    fig, axes = plt.subplots(1, len(reserves), figsize=(12, 4.6), sharey=True)
    for ax, reserve in zip(np.atleast_1d(axes), reserves):
        sub = df[df.reserve == reserve]
        x = np.arange(len(sub))
        ax.bar(x, sub.nodes_expanded, color=SERIES, width=0.6)
        for xi, (n, cost, opt) in enumerate(zip(sub.nodes_expanded, sub.cost, sub.optimal)):
            ax.annotate(f"{n:,}\ncost {cost:.0f}{'' if opt == 'yes' else ' (not optimal)'}",
                        (xi, n), textcoords="offset points", xytext=(0, 3), ha="center",
                        fontsize=7, color=TEXT_MUTED)
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels(sub.planner, rotation=30, ha="right", fontsize=8)
        ax.set_title(f"planning reserve {reserve}", fontsize=10)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    np.atleast_1d(axes)[0].set_ylabel("nodes expanded (log scale)")
    fig.tight_layout()
    path = save_fig(fig, "heuristic_nodes")
    plt.close(fig)
    return path


# ---------------------------------------------------------------- 4. ablation
ABLATION = [
    ("h_ours (full)", h_ours),
    ("- tunnel edges in the fields", h_ours_no_tunnels),
    ("- hill costs in the fields", h_ours_no_hills),
    ("- MST term (= h_farthest)", h_farthest),
    ("- farthest term (= h_mst)", h_mst),
]


def ablation(adm: pd.DataFrame) -> pd.DataFrame:
    cfg = parse_cli(["--fuel-reserve", "0"])
    optimum = ucs(DeliveryProblem(cfg), prune_dominated=True).cost
    rows = []
    for label, h in ABLATION:
        res = astar(DeliveryProblem(cfg), heuristic=h)
        checks = adm[adm.heuristic == h.__name__]
        rows.append({"variant": label, "heuristic": h.__name__,
                     "h_at_start": h(DeliveryProblem(cfg).initial_state(), DeliveryProblem(cfg)),
                     "cost": res.cost, "optimal": "yes" if res.cost == optimum else "NO",
                     "nodes_expanded": res.nodes_expanded, "reopenings": res.stats.get("reopened"),
                     "admissibility_violations": int(checks.violations.sum()),
                     "states_checked": int(checks.states.sum())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- entry point
def run(cfg, log):
    t0 = time.perf_counter()
    adm = admissibility(cfg.quick, log)
    save_table(adm, "heuristic_admissibility")
    log.info("admissibility (h <= true cost-to-go):\n%s", adm.to_string(index=False))
    con = consistency(cfg.quick)
    save_table(con, "heuristic_consistency")
    log.info("consistency (h(s) <= c + h(s')):\n%s", con.to_string(index=False))
    comp = comparison(cfg.quick, log)
    save_table(comp, "heuristic_comparison")
    plot_nodes(comp)
    log.info("main comparison:\n%s", comp.to_string(index=False))
    abl = ablation(adm)
    save_table(abl, "heuristic_ablation")
    log.info("ablation:\n%s", abl.to_string(index=False))
    log.info("heuristic evaluation done in %.0f s", time.perf_counter() - t0)


if __name__ == "__main__":
    import sys

    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("heuristic_eval"))
