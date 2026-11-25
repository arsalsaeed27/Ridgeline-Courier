"""Part B: the heuristic comparison and the ablation over 30 SCENARIOS (not just our default map),
with 95% bootstrap CIs, plus a failure analysis. Uses oel/experiments/framework.py.

Scenarios: our map with the 5 stops re-drawn (framework.make_scenarios), all twists ON.
1. Main comparison (reserve 0 and 20): UCS, A* + h_manhattan / h_farthest / h_mst / h_ours,
   Greedy + h_ours, A* + h_ours + fuel pruning (the reference = the optimum).
   UCS, A* + h_manhattan and A* + h_farthest take 5-20 s per run: they are "slow" variants, run
   in the full mode only (--quick uses their cached rows if present). UCS and A* get a memory cap
   of MAX_STATES stored states, so one unlucky scenario can't eat all the RAM; a hit is reported.
2. Ablation of h_ours (reserve 0): - tunnel edges, - hill costs, - MST term, - farthest term.
3. Failure analysis: hardest scenarios for A* + h_ours and why, limit hits, greedy's worst
   cases, where reopenings pile up. Figures of the worst cases.

Outputs (stamped): results/tables/scenarios_{comparison,ablation,hardest,greedy_worst,runs}
results/figures/scenarios_{comparison,ablation,hardness,greedy_worst,hardest_route}.png

    python -m oel.experiments.heuristic_scenarios           # full (computes the slow variants)
    python -m oel.experiments.heuristic_scenarios --quick   # fast variants only (+ cache)
"""
from __future__ import annotations

import dataclasses
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from oel.experiments.framework import (REFERENCE, Variant, decode_actions, make_scenarios, readable,
                                       run_experiment, summarise)
from oel.experiments.routes import cells_of, differing_segments
from oel.stamp import save_fig, save_table
from oel.world.plots import plot_route_comparison
from oel.world.problem import DeliveryProblem

N = 30
MAX_STATES = (("max_states", 4_000_000),)
MAIN = [
    Variant("UCS", "ucs", None, MAX_STATES, slow=True),
    Variant("A* + h_manhattan", "astar", "h_manhattan", MAX_STATES, slow=True),
    Variant("A* + h_farthest", "astar", "h_farthest", MAX_STATES, slow=True),
    Variant("A* + h_mst", "astar", "h_mst"),
    Variant("A* + h_ours", "astar", "h_ours"),
    Variant("Greedy + h_ours", "greedy", "h_ours"),
    REFERENCE,
]
ABLATION = [
    Variant("h_ours (full)", "astar", "h_ours"),
    Variant("- tunnel edges (inadmissible)", "astar", "h_ours_no_tunnels"),
    Variant("- hill costs", "astar", "h_ours_no_hills"),
    Variant("- MST term (= h_farthest)", "astar", "h_farthest", MAX_STATES, slow=True),
    Variant("- farthest term (= h_mst)", "astar", "h_mst"),
]
SERIES, SECOND = "#2a78d6", "#eb6834"
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"


def _style(ax):
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def _dot_ci(ax, summary, metric, colour=SERIES, log=True):
    """Mean (dot) with 95% CI (line), one row per variant, top to bottom."""
    y = np.arange(len(summary))[::-1]
    mean, lo, hi = summary[f"{metric}_mean"], summary[f"{metric}_lo"], summary[f"{metric}_hi"]
    ax.errorbar(mean, y, xerr=[mean - lo, hi - mean], fmt="o", color=colour, ms=7, capsize=3, lw=1.5)
    for yi, m in zip(y, mean):
        if not np.isnan(m):
            ax.annotate(f"{m:,.0f}" if metric == "nodes" else f"{m:.2f}", (m, yi), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=7, color=TEXT_MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels(summary.variant, fontsize=8)
    if log:
        ax.set_xscale("log")
    _style(ax)


# ---------------------------------------------------------------- 1. main comparison
def main_comparison(cfg, log, compute_slow):
    frames = []
    for reserve in (0, 20):
        rcfg = dataclasses.replace(cfg, fuel_reserve=reserve, overrides=list(cfg.overrides))
        df = run_experiment(MAIN, N, name="scenarios", base_cfg=rcfg, compute_slow=compute_slow, log=log)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    tables = []
    for reserve, g in df.groupby("reserve"):
        s = summarise(g)
        t = readable(s, metrics=("nodes", "runtime_s", "gap_pct"))
        t.insert(0, "reserve", reserve)
        t["limit hits"] = [int((g[g.variant == v].reason.isin(["memory_limit", "node_limit", "time_limit"])).sum())
                           for v in s.variant]
        t["mean reopenings"] = [round(float(g[g.variant == v].reopened.astype(float).mean()), 0) for v in s.variant]
        tables.append((reserve, s, t))
    return df, tables


def plot_comparison(tables):
    fig, axes = plt.subplots(1, len(tables), figsize=(13, 4.6), sharey=True)
    for ax, (reserve, s, _t) in zip(np.atleast_1d(axes), tables):
        _dot_ci(ax, s, "nodes")
        ax.set_xlabel("nodes expanded: mean and 95% bootstrap CI (log scale)")
        ax.set_title(f"30 scenarios, planning reserve {reserve}", fontsize=10)
    fig.tight_layout()
    path = save_fig(fig, "scenarios_comparison")
    plt.close(fig)
    return path


# ---------------------------------------------------------------- 2. ablation
def ablation(cfg, log, compute_slow):
    rcfg = dataclasses.replace(cfg, fuel_reserve=0, overrides=list(cfg.overrides))
    df = run_experiment(ABLATION, N, name="scenarios", base_cfg=rcfg, compute_slow=compute_slow, log=log)
    df = df[df.variant != REFERENCE.label]
    s = summarise(df, metrics=("nodes", "runtime_s", "gap_pct", "h_over_opt"))
    t = readable(s, metrics=("nodes", "gap_pct", "h_over_opt"), digits={"nodes": 0, "gap_pct": 2, "h_over_opt": 3})
    t["max gap %"] = [round(float(df[df.variant == v].gap_pct.max()), 2) for v in s.variant]
    t["mean reopenings"] = [round(float(df[df.variant == v].reopened.astype(float).mean()), 0) for v in s.variant]
    return df, s, t


def plot_ablation(s):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    _dot_ci(ax1, s, "nodes")
    ax1.set_xlabel("nodes expanded: mean and 95% CI (log scale)")
    ax1.set_title("Ablation of h_ours over 30 scenarios (reserve 0)", fontsize=10)
    _dot_ci(ax2, s, "h_over_opt", colour=SECOND, log=False)
    ax2.set_xlabel("h(start) / optimal cost: mean and 95% CI (above 1 = overestimates)")
    ax2.axvline(1.0, color=TEXT_MUTED, lw=0.8, ls="--")
    ax2.set_title("How tight the heuristic is at the start", fontsize=10)
    fig.tight_layout()
    path = save_fig(fig, "scenarios_ablation")
    plt.close(fig)
    return path


# ---------------------------------------------------------------- 3. failure analysis
def _replay(scen, actions_text):
    problem = DeliveryProblem(scen)
    state, path = problem.initial_state(), [problem.initial_state()]
    for a in decode_actions(actions_text):
        state = problem.result(state, a)
        path.append(state)
    return path


def failures(cfg, df: pd.DataFrame, log):
    """Per scenario (reserve 0): what makes A* + h_ours work hard, and where greedy goes wrong."""
    d = df[df.reserve == 0]
    ref = d[d.variant == REFERENCE.label].set_index("scenario")
    plain = d[d.variant == "A* + h_ours"].set_index("scenario")
    greedy = d[d.variant == "Greedy + h_ours"].set_index("scenario")
    per = pd.DataFrame({
        "stops": ref.stops, "optimal_cost": ref.cost, "astar_h_ours_nodes": plain.nodes,
        "pruned_nodes": ref.nodes, "reopenings": plain.reopened, "h_start_over_opt": plain.h_over_opt.round(3),
        "refuels": ref.refuels, "tunnel_jumps": ref.tunnel_jumps, "mud_cells": ref.mud_cells,
        "ford_cells": ref.ford_cells, "height_climbed": ref.height_climbed,
        "delivery_order": ref.delivery_order, "greedy_gap_pct": greedy.gap_pct.round(1),
    }).reset_index()
    ucs = d[d.variant == "UCS"].set_index("scenario")
    if len(ucs):
        per["ucs_nodes"] = per.scenario.map(ucs.nodes)
    corr = {}
    for col in ("h_start_over_opt", "refuels", "tunnel_jumps", "ford_cells", "mud_cells", "height_climbed", "optimal_cost"):
        rho, p = spearmanr(per[col], per.astar_h_ours_nodes)
        corr[col] = (round(float(rho), 2), round(float(p), 4))
    log.info("Spearman correlation of A*+h_ours nodes with each feature (rho, p): %s", corr)
    hardest = per.sort_values("astar_h_ours_nodes", ascending=False).reset_index(drop=True)
    greedy_worst = per.sort_values("greedy_gap_pct", ascending=False).reset_index(drop=True)
    limits = df[df.reason.isin(["memory_limit", "node_limit", "time_limit"])][["reserve", "scenario", "variant", "reason", "nodes"]]
    return per, hardest, greedy_worst, limits, corr


def plot_hardness(per: pd.DataFrame, corr: dict):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, col, label in ((ax1, "h_start_over_opt", "h_ours(start) / optimal cost (tightness)"),
                           (ax2, "refuels", "recharges on the optimal route")):
        x = per[col] + (np.random.default_rng(0).uniform(-0.08, 0.08, len(per)) if col == "refuels" else 0)
        ax.scatter(x, per.astar_h_ours_nodes, s=36, color=SERIES, zorder=3)
        for _, r in per.nlargest(3, "astar_h_ours_nodes").iterrows():
            xv = r[col]
            ax.annotate(f"scenario {r.scenario}", (xv, r.astar_h_ours_nodes), textcoords="offset points",
                        xytext=(6, 0), fontsize=7, color=TEXT_MUTED)
        rho, p = corr[col]
        ax.set_title(f"Spearman rho = {rho:+.2f} (p = {p:.3f})", fontsize=10)
        ax.set_xlabel(label)
        ax.set_yscale("log")
        _style(ax)
    ax1.set_ylabel("A* + h_ours nodes expanded (log)")
    fig.suptitle("What makes a scenario hard for A* + h_ours (30 scenarios, reserve 0)", y=0.94, fontsize=10)
    fig.tight_layout()
    path = save_fig(fig, "scenarios_hardness")
    plt.close(fig)
    return path


def plot_bad_cases(cfg, df, hardest, greedy_worst):
    scenarios = make_scenarios(N, dataclasses.replace(cfg, fuel_reserve=0, overrides=list(cfg.overrides)))
    d = df[df.reserve == 0]
    out = {}
    # (a) greedy's worst scenario: greedy route vs the optimal one
    k = int(greedy_worst.scenario.iloc[0])
    scen = scenarios[k]
    opt = cells_of(_replay(scen, d[(d.scenario == k) & (d.variant == REFERENCE.label)].actions.iloc[0]))
    g = cells_of(_replay(scen, d[(d.scenario == k) & (d.variant == "Greedy + h_ours")].actions.iloc[0]))
    only_g = differing_segments(g, opt)
    r = greedy_worst.iloc[0]
    plot_route_comparison(scen, [(opt, f"optimal (cost {r.optimal_cost:.0f})", SERIES, "-"),
                                 (g, f"greedy + h_ours (+{r.greedy_gap_pct:.0f}%)", SECOND, "--")],
                          highlight=sorted({c for s in only_g for c in s}),
                          highlight_label="cells only on the greedy route",
                          title=f"Scenario {k}: greedy's worst case (+{r.greedy_gap_pct:.0f}% over optimal)",
                          name="scenarios_greedy_worst")
    out["greedy_worst"] = {"scenario": k, "greedy_only_segments": [(s[0], s[-1], len(s)) for s in only_g[:4]]}
    # (b) the hardest scenario for A* + h_ours: its optimal route
    k = int(hardest.scenario.iloc[0])
    scen = scenarios[k]
    path = _replay(scen, d[(d.scenario == k) & (d.variant == REFERENCE.label)].actions.iloc[0])
    r = hardest.iloc[0]
    plot_route_comparison(scen, [(cells_of(path), f"optimal route (cost {r.optimal_cost:.0f})", SERIES, "-")],
                          title=(f"Scenario {k}: hardest for A* + h_ours ({r.astar_h_ours_nodes:,} nodes; "
                                 f"h(start)/opt {r.h_start_over_opt:.2f}, {r.refuels} recharges)"),
                          name="scenarios_hardest_route")
    out["hardest"] = {"scenario": k, "stops": scen.stops}
    return out


# ---------------------------------------------------------------- entry point
def run(cfg, log):
    t0 = time.perf_counter()
    compute_slow = not cfg.quick
    df, tables = main_comparison(cfg, log, compute_slow)
    comp = pd.concat([t for _r, _s, t in tables], ignore_index=True)
    save_table(comp, "scenarios_comparison")
    plot_comparison(tables)
    log.info("30-scenario comparison:\n%s", comp.to_string(index=False))

    abl_df, abl_s, abl_t = ablation(cfg, log, compute_slow)
    save_table(abl_t, "scenarios_ablation")
    plot_ablation(abl_s)
    log.info("30-scenario ablation:\n%s", abl_t.to_string(index=False))

    per, hardest, greedy_worst, limits, corr = failures(cfg, df, log)
    save_table(hardest.head(8), "scenarios_hardest")
    save_table(greedy_worst.head(5), "scenarios_greedy_worst")
    plot_hardness(per, corr)
    cases = plot_bad_cases(cfg, df, hardest, greedy_worst)
    runs = pd.concat([df, abl_df], ignore_index=True).drop(columns=["actions", "from_cache"])
    save_table(runs, "scenarios_runs")
    log.info("hardest scenarios:\n%s", hardest.head(8).to_string(index=False))
    log.info("greedy's worst:\n%s", greedy_worst.head(5).to_string(index=False))
    log.info("limit hits: %s", "none" if limits.empty else "\n" + limits.to_string(index=False))
    log.info("bad cases: %s", cases)
    log.info("scenario experiments done in %.0f s", time.perf_counter() - t0)
    return comp, abl_t


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("heuristic_scenarios"))
