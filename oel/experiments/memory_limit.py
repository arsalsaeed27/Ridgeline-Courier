"""Part B: search under a MEMORY limit: A* vs IDS vs IDA*.

Question: what if the planner may only hold a fixed number of states in memory?
  - A* + h_ours with max_states in MEMORY_CAPS: it keeps every state it generates (frontier +
    expanded), so below some cap it simply stops ("memory_limit"). UCS (= A* without a
    heuristic) gets the same caps: it needs far more memory, so the cap hurts it much earlier.
    (The caps are small because h_ours is so accurate on these windows that A* rarely holds
    more than a few hundred states; caps of 10k or more never bite here.)
  - IDS: stores only the current path, so it never runs out of memory, but it re-expands the
    same states over and over (every iteration starts again, and different branches reach the
    same state). It finds the FEWEST MOVES, which is usually not the cheapest route.
  - IDA* + h_ours: also stores only the current path, but deepens on f = g + h instead of on
    depth, so the heuristic cuts most branches: memory like IDS, far fewer nodes, optimal cost.
IDS and IDA* get the same node/time budget (BUDGET).

Instance sets (both: our real map masked to a window around the depot, see small_instances.py):
  small  : 30 instances, 7x7 window, 1-3 stops, fuel OFF (session 1's set)
  medium : 30 instances, 15x15 window, 2-3 stops, fuel ON (tank MEDIUM_CAPACITY)
Measured per run: solved, cost (and whether it is optimal: A* without a cap gives the optimum),
nodes expanded, DISTINCT states expanded (so nodes / distinct = how often each state was
expanded on average), peak stored states (= the memory: all generated states for A*, the
longest path for IDS / IDA*), runtime.

Outputs (stamped): results/tables/memory_limit, memory_limit_runs, results/figures/memory_limit.png
Runs are cached in oel/experiments/cache/memory_limit.json.

    python -m oel.experiments.memory_limit
"""
from __future__ import annotations

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.config import BASE_SEED
from oel.experiments.framework import Variant, run_cached
from oel.experiments.small_instances import small_instances
from oel.experiments.stats import bootstrap_mean_ci, wilson_ci
from oel.stamp import save_fig, save_table

N_INSTANCES = 30
MEMORY_CAPS = [25, 50, 100, 250, 1_000, 10_000, None]        # None = unlimited
BUDGET = (("node_limit", 500_000), ("time_limit", 20.0))     # the same for IDS and IDA*
MEDIUM_RADIUS, MEDIUM_STOPS, MEDIUM_CAPACITY, MEDIUM_SEED_OFFSET = 7, (2, 3), 30, 3000
A_STAR, IDS, IDA, UCS = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"   # categorical slots 1-4
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"


def cap_label(cap, name="A*") -> str:
    return f"{name} (no cap)" if cap is None else f"{name} (cap {cap:,})"


def variants() -> list:
    out = [Variant(cap_label(cap), "astar", "h_ours",
                   () if cap is None else (("max_states", cap),), count_distinct=True)
           for cap in MEMORY_CAPS]
    out += [Variant(cap_label(cap, "UCS"), "ucs", None,
                    () if cap is None else (("max_states", cap),), count_distinct=True)
            for cap in MEMORY_CAPS]
    out.append(Variant("IDS", "ids", None, (("max_depth", 100),) + BUDGET, count_distinct=True))
    out.append(Variant("IDA*", "ida_star", "h_ours", BUDGET, count_distinct=True))
    return out


def instance_sets(cfg) -> dict:
    flags = dict(use_hills=cfg.use_hills, use_tunnels=cfg.use_tunnels)
    small = small_instances(N_INSTANCES, radius=3, use_fuel=False, **flags)
    medium = small_instances(N_INSTANCES, radius=MEDIUM_RADIUS, n_stops=MEDIUM_STOPS, use_fuel=cfg.use_fuel,
                             capacity=MEDIUM_CAPACITY, seed_offset=MEDIUM_SEED_OFFSET, **flags)
    for i, m in enumerate(medium):
        m.instance_id = f"{cfg.instance_id}-medium{i}"
    return {"small (7x7, fuel off)": small,
            f"medium (15x15, fuel {'on' if cfg.use_fuel else 'off'})": medium}


def collect(cfg, log) -> pd.DataFrame:
    jobs = []
    for set_name, instances in instance_sets(cfg).items():
        for i, inst in enumerate(instances):
            for v in variants():
                jobs.append(({"set": set_name, "instance": i, "stops": len(inst.stops)}, inst, v))
    df = pd.DataFrame(run_cached(jobs, "memory_limit", log=log))
    best = df[df.variant == cap_label(None)].set_index(["set", "instance"]).cost
    df["optimal_cost"] = [best[(s, i)] for s, i in zip(df["set"], df.instance)]
    df["optimal"] = df.solved & np.isclose(df.cost.astype(float), df.optimal_cost.astype(float))
    df["expansions_per_state"] = df.nodes / df.distinct_expanded.replace(0, np.nan)
    return df


def _ci(values, digits=0) -> str:
    values = pd.Series(values).dropna().astype(float)
    if not len(values):
        return "-"
    mean, lo, hi = bootstrap_mean_ci(values, seed=BASE_SEED)
    return f"{mean:,.{digits}f} [{lo:,.{digits}f}, {hi:,.{digits}f}]"


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (set, algorithm). Nodes, stored states and runtime are over ALL runs (a run
    stopped by its memory cap or budget still did that work); cost over solved runs."""
    rows = []
    labels = [v.label for v in variants()]
    for set_name in df["set"].unique():
        for label in labels:
            g = df[(df["set"] == set_name) & (df.variant == label)]
            solved = g[g.solved]
            lo, hi = wilson_ci(len(solved), len(g))
            reasons = g.reason.value_counts().to_dict()
            rows.append({
                "set": set_name, "algorithm": label, "runs": len(g),
                "solved_pct": round(100 * len(solved) / len(g), 1),
                "solved % [95% CI]": f"{100 * len(solved) / len(g):.0f} [{100 * lo:.0f}, {100 * hi:.0f}]",
                "optimal % of solved": round(100 * solved.optimal.mean(), 0) if len(solved) else None,
                "peak stored states": _ci(g.stored_states),
                "nodes expanded": _ci(g.nodes),
                "distinct states expanded": _ci(g.distinct_expanded),
                "expansions per state": _ci(g.expansions_per_state, 1),
                "runtime ms": _ci(1000 * g.runtime_s, 1),
                "outcomes": ", ".join(f"{k}: {v}" for k, v in reasons.items()),
                # numeric copies for the figure
                "_stored_mean": g.stored_states.mean(), "_nodes": list(g.nodes),
                "_solved_lo": 100 * lo, "_solved_hi": 100 * hi,
            })
    return pd.DataFrame(rows)


def plot(summary: pd.DataFrame):
    """Row per instance set. Left: solved % vs peak stored states (A* along its caps; IDS and
    IDA* as single points). Right: nodes expanded, mean with 95% CI, log scale."""
    sets = list(summary["set"].unique())
    fig, axes = plt.subplots(len(sets), 2, figsize=(12, 4.2 * len(sets)))
    for row, set_name in zip(np.atleast_2d(axes), sets):
        s = summary[summary["set"] == set_name]
        ax = row[0]
        for name, colour, label in (("A*", A_STAR, "A* + h_ours with a memory cap"),
                                    ("UCS", UCS, "UCS with a memory cap")):
            a = s[s.algorithm.str.startswith(name + " (")]
            capped = a.iloc[:-1]                    # the caps, in increasing order
            x = [c for c in MEMORY_CAPS if c is not None]
            ax.errorbar(x, capped.solved_pct, yerr=[capped.solved_pct - capped._solved_lo,
                                                    capped._solved_hi - capped.solved_pct],
                        color=colour, lw=2, marker="o", ms=7, capsize=3, label=label)
            # without a cap: a hollow marker at the number of states it really needed
            free = a.iloc[-1]
            ax.plot([free._stored_mean], [free.solved_pct], marker="o", ms=11, mfc="white", mec=colour,
                    mew=2, ls="", zorder=4)
            ax.annotate(f"{name}, no cap:\nneeds {free._stored_mean:,.0f}", (free._stored_mean, free.solved_pct),
                        textcoords="offset points", xytext=(0, 9), ha="center", fontsize=7, color=TEXT_MUTED)
        for label, colour, marker in (("IDS", IDS, "s"), ("IDA*", IDA, "D")):
            r = s[s.algorithm == label].iloc[0]
            ax.errorbar([r._stored_mean], [r.solved_pct],
                        yerr=[[r.solved_pct - r._solved_lo], [r._solved_hi - r.solved_pct]],
                        color=colour, marker=marker, ms=9, capsize=3, ls="", label=f"{label} (stores one path)")
        ax.set_xscale("log")
        ax.set_ylim(-5, 120)
        ax.set_xlabel("states held in memory (A*/UCS: the cap, or the states needed without one;\n"
                      "IDS / IDA*: mean peak = the longest path)")
        ax.set_ylabel("solved % (95% Wilson CI)")
        ax.set_title(f"{set_name}: solved vs memory", fontsize=10)
        handles, labels = ax.get_legend_handles_labels()

        ax = row[1]
        pick = [(cap_label(None, "UCS"), UCS), (cap_label(None), A_STAR), ("IDS", IDS), ("IDA*", IDA)]
        for k, (label, colour) in enumerate(pick):
            r = s[s.algorithm == label].iloc[0]
            mean, lo, hi = bootstrap_mean_ci(r._nodes, seed=BASE_SEED)
            ax.bar(k, mean, color=colour, width=0.55)
            ax.errorbar(k, mean, yerr=[[mean - lo], [hi - mean]], color="#212121", capsize=4, lw=1)
            ax.annotate(f"{mean:,.0f}\nsolved {r.solved_pct:.0f}%", (k, hi), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8, color=TEXT_MUTED)
        ax.set_yscale("log")
        ax.set_ylim(top=ax.get_ylim()[1] * 12)     # room for the value labels
        ax.set_xticks(range(len(pick)))
        ax.set_xticklabels(["UCS (no cap)", "A* (no cap)", "IDS", "IDA*"])
        ax.set_ylabel("nodes expanded, mean (95% CI), log scale")
        ax.set_title(f"{set_name}: work done", fontsize=10)
        for a_ in row:
            a_.grid(color=GRID, lw=0.8)
            a_.set_axisbelow(True)
            for side in ("top", "right"):
                a_.spines[side].set_visible(False)
    # one legend for the whole figure, under the plots (it would hide points inside a panel)
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))      # room for the legend and the stamp line
    path = save_fig(fig, "memory_limit")
    plt.close(fig)
    return path


def run(cfg, log):
    t0 = time.perf_counter()
    df = collect(cfg, log)
    summary = summarise(df)
    save_table(summary[[c for c in summary.columns if not c.startswith("_") and c != "solved_pct"]],
               "memory_limit")
    cols = ["set", "instance", "stops", "variant", "solved", "reason", "cost", "optimal_cost", "optimal",
            "nodes", "distinct_expanded", "expansions_per_state", "stored_states", "runtime_s"]
    save_table(df[cols], "memory_limit_runs")
    plot(summary)
    log.info("memory limit (%.0f s):\n%s", time.perf_counter() - t0,
             summary[[c for c in summary.columns if not c.startswith("_")]].to_string(index=False))
    return summary


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("memory_limit"))
