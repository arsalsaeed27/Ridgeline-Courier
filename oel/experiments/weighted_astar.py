"""Part B: inadmissible / weighted A* on the full map (hills ON, all twists; reserve 0 and 20).

Variants: A* + h_ours with f = g + w*h for w in WEIGHTS, and plain A* with h_manhattan_raw (our
inadmissible heuristic). Each runs WITHOUT fuel pruning (so the node savings of w are clearly
visible) and WITH pruning (the practical setting).

Columns: cost, gap % vs the optimum, nodes, stored states, runtime, and whether
cost <= w * optimum (the weighted-A* guarantee; it needs an admissible h, so h_manhattan_raw
gets "no guarantee").

Outputs (stamped): results/tables/weighted_astar, results/figures/weighted_astar_pareto.png,
results/figures/weighted_astar_route.png (the clearest "faster but worse" case vs the optimum),
results/figures/weighted_astar_route_worst.png (the most expensive weighted route), and
results/tables/weighted_astar_case{,_worst}{,_segments} (their route facts and differing segments). Runs are cached
(oel/experiments/cache/weighted_astar.json), so a rerun with the same settings is instant.

    python -m oel.experiments.weighted_astar
"""
from __future__ import annotations

import dataclasses
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.experiments.framework import REFERENCE, Variant, decode_actions, run_cached
from oel.experiments.routes import differing_segments, route_facts
from oel.stamp import save_fig, save_table
from oel.world.plots import plot_route_comparison
from oel.world.problem import DeliveryProblem

WEIGHTS = [1.0, 1.2, 1.5, 2.0, 3.0, 5.0]
RESERVES = [0, 20]
OFF, ON = "#2a78d6", "#eb6834"          # categorical slots 1 and 2 (validated palette)
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"


def variants() -> list:
    out = []
    for prune in (False, True):
        opts = (("prune_dominated", True),) if prune else ()
        for w in WEIGHTS:
            out.append(Variant(f"w={w:g}", "weighted_astar", "h_ours", (("w", w),) + opts))
        out.append(Variant("h_manhattan_raw", "astar", "h_manhattan_raw", opts))
    return out


def run_all_variants(cfg, log) -> pd.DataFrame:
    jobs = []
    for reserve in RESERVES:
        rcfg = dataclasses.replace(cfg, fuel_reserve=reserve, overrides=list(cfg.overrides))
        jobs.append(({"reserve": reserve, "role": "reference"}, rcfg, REFERENCE))
        for v in variants():
            pruning = dict(v.options).get("prune_dominated", False)
            jobs.append(({"reserve": reserve, "role": "variant", "pruning": "on" if pruning else "off",
                          "w": dict(v.options).get("w", 1.0)}, rcfg, v))
    rows = pd.DataFrame(run_cached(jobs, "weighted_astar", log=log))
    ref = rows[rows.role == "reference"].set_index("reserve").cost
    df = rows[rows.role == "variant"].copy()
    df["optimal_cost"] = df.reserve.map(ref)
    df["gap_pct"] = (100 * (df.cost - df.optimal_cost) / df.optimal_cost).round(2)
    df["bound_w_x_opt"] = (df.w * df.optimal_cost).round(1)

    def guarantee(r):
        if r.variant == "h_manhattan_raw":
            return "no guarantee (h inadmissible)"
        return "yes" if r.cost <= r.w * r.optimal_cost + 1e-9 else "VIOLATED"

    df["cost_le_w_opt"] = df.apply(guarantee, axis=1)
    return df


def table(df: pd.DataFrame) -> pd.DataFrame:
    base = df[(df.variant == "w=1")].set_index(["reserve", "pruning"]).nodes
    out = df.assign(nodes_vs_w1=[f"{n / base[(r, p)]:.2f}x" for n, r, p in zip(df.nodes, df.reserve, df.pruning)])
    cols = ["reserve", "pruning", "variant", "cost", "optimal_cost", "gap_pct", "nodes", "nodes_vs_w1",
            "stored_states", "reopened", "runtime_s", "bound_w_x_opt", "cost_le_w_opt"]
    return out[cols].sort_values(["reserve", "pruning", "variant"], kind="stable").reset_index(drop=True)


def plot_pareto(df: pd.DataFrame):
    """Nodes expanded (log x) vs cost gap % (y). One panel per reserve; pruning off/on = two series."""
    fig, axes = plt.subplots(1, len(RESERVES), figsize=(12, 4.8), sharey=True)
    for ax, reserve in zip(axes, RESERVES):
        placed = []                     # (log10 x, y) of labels already drawn in this panel
        for pruning, colour, marker, face in (("off", OFF, "o", OFF), ("on", ON, "s", "white")):
            sub = df[(df.reserve == reserve) & (df.pruning == pruning)].sort_values("nodes")
            ax.scatter(sub.nodes, sub.gap_pct, s=64, marker=marker, facecolor=face, edgecolor=colour,
                       linewidth=2, zorder=3, label=f"fuel pruning {pruning}")
            for x, y, label in zip(sub.nodes, sub.gap_pct, sub.variant):
                lx = np.log10(x)
                # a label close to one already drawn goes below its point instead of above
                crowded = sum(abs(lx - px) < 0.3 and abs(y - py) < 2.5 for px, py in placed)
                dy = 5 - 13 * (crowded % 2) - 9 * (crowded // 2)
                ax.annotate(label.replace("h_manhattan_raw", "Manhattan raw"), (x, y),
                            textcoords="offset points", xytext=(6, dy), fontsize=7, color=TEXT_MUTED)
                placed.append((lx, y))
        ax.set_xscale("log")
        ax.set_xlabel("nodes expanded (log scale)")
        ax.set_title(f"planning reserve {reserve} (optimum {df[df.reserve == reserve].optimal_cost.iloc[0]:.0f})",
                     fontsize=10)
        ax.grid(color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel("cost above the optimum (%)")
    axes[0].legend(fontsize=8, frameon=False, loc="upper left")
    fig.suptitle("Weighted A* (h_ours, f = g + w*h) and inadmissible A*: work vs route quality", y=0.94, fontsize=10)
    fig.tight_layout()
    path = save_fig(fig, "weighted_astar_pareto")
    plt.close(fig)
    return path


def pick_case(df: pd.DataFrame) -> pd.Series:
    """The clearest 'faster but worse' case: pruning OFF (savings visible), w > 1, a worse route,
    and the largest share of nodes saved per % of extra cost."""
    base = df[(df.variant == "w=1") & (df.pruning == "off")].set_index("reserve").nodes
    cand = df[(df.pruning == "off") & (df.variant.str.startswith("w=")) & (df.variant != "w=1")
              & (df.gap_pct > 0)].copy()
    cand["saved"] = 1 - cand.nodes / cand.reserve.map(base)
    cand = cand[cand.saved > 0]
    cand["score"] = cand.saved / cand.gap_pct
    return cand.sort_values("score", ascending=False).iloc[0]


def describe_case(cfg, df: pd.DataFrame, case: pd.Series, log, name: str = "weighted_astar_route"):
    rcfg = dataclasses.replace(cfg, fuel_reserve=int(case.reserve), overrides=list(cfg.overrides))
    problem = DeliveryProblem(rcfg)
    opt_row = df[(df.reserve == case.reserve) & (df.variant == "w=1") & (df.pruning == "off")].iloc[0]

    def replay(actions_text):
        state, path = problem.initial_state(), [problem.initial_state()]
        actions = decode_actions(actions_text)
        for a in actions:
            state = problem.result(state, a)
            path.append(state)
        return path, actions

    opt_path, opt_actions = replay(opt_row.actions)
    w_path, w_actions = replay(case.actions)
    opt_cells = [s[:2] for s in opt_path]
    w_cells = [s[:2] for s in w_path]
    only_w = differing_segments(w_cells, opt_cells)
    only_opt = differing_segments(opt_cells, w_cells)
    facts = []
    for label, path, actions, row in (("optimal (w=1)", opt_path, opt_actions, opt_row),
                                      (f"weighted ({case.variant})", w_path, w_actions, case)):
        f = route_facts(problem, path, actions)
        facts.append({"route": label, "cost": row.cost, "nodes": row.nodes,
                      "delivery_order": "-".join(map(str, f["delivery_order"])), "moves": f["moves"],
                      "refuels": f["refuels"], "refuel_cells": str(f["refuel_cells"]),
                      "tunnel_jumps": f["tunnel_jumps"], "mud_cells": f["mud_cells"],
                      "ford_cells": f["ford_cells"], "height_climbed": f["height_climbed"]})
    segments = pd.DataFrame(
        [{"only_on": "weighted route", "from": str(s[0]), "to": str(s[-1]), "cells": len(s)} for s in only_w]
        + [{"only_on": "optimal route", "from": str(s[0]), "to": str(s[-1]), "cells": len(s)} for s in only_opt])
    highlight = sorted({c for s in only_w for c in s})
    title = (f"Reserve {int(case.reserve)}: optimal route (cost {opt_row.cost:.0f}, {opt_row.nodes:,} nodes) vs "
             f"weighted A* {case.variant} (cost {case.cost:.0f}, {case.nodes:,} nodes)")
    plot_route_comparison(rcfg, [(opt_cells, f"optimal, w=1 (cost {opt_row.cost:.0f})", OFF, "-"),
                                 (w_cells, f"weighted {case.variant} (cost {case.cost:.0f})", ON, "--")],
                          highlight=highlight, highlight_label="cells only on the weighted route",
                          title=title, name=name)
    log.info("%s: reserve %d, %s: %d vs %d nodes (%.0f%% fewer), cost %.0f vs %.0f (+%.1f%%)",
             name, case.reserve, case.variant, case.nodes, opt_row.nodes, 100 * (1 - case.nodes / opt_row.nodes),
             case.cost, opt_row.cost, case.gap_pct)
    return pd.DataFrame(facts), segments


def run(cfg, log):
    t0 = time.perf_counter()
    df = run_all_variants(cfg, log)
    tab = table(df)
    save_table(tab, "weighted_astar")
    plot_pareto(df)
    # (1) the clearest "faster but worse" case, (2) the most expensive weighted route
    worst = df[(df.pruning == "off") & (df.variant != "w=1") & df.variant.str.startswith("w=")]
    worst = worst.sort_values("gap_pct", ascending=False).iloc[0]
    for case, name in ((pick_case(df), "weighted_astar_route"), (worst, "weighted_astar_route_worst")):
        facts, segments = describe_case(cfg, df, case, log, name=name)
        table_name = "weighted_astar_case" if name == "weighted_astar_route" else "weighted_astar_case_worst"
        save_table(facts, table_name)
        save_table(segments, table_name + "_segments")
        log.info("%s routes:\n%s\nwhere they differ:\n%s", name, facts.to_string(index=False),
                 segments.to_string(index=False))
    violated = (tab.cost_le_w_opt == "VIOLATED").sum()
    log.info("weighted A* (%.0f s):\n%s", time.perf_counter() - t0, tab.to_string(index=False))
    if violated:
        log.warning("%d runs broke the cost <= w * optimum guarantee", violated)
    return tab


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("weighted_astar"))
