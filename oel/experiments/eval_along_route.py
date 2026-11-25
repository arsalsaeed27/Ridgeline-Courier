"""Part C sanity check (no Minimax needed): our evaluation function along two simulated runs.

Both runs use the default A* plan, slip, the placeholder rival and rejoin/full replanning
(exactly the run_all demo), and record a GameState after every step (Simulator on_step hook):
  - the default seed (cfg.seed): a LOSS (stranded) since session 3;
  - the first seed after it (cfg.seed + 1, + 2, ...) whose run is a WIN (a fixed rule).
For each step we plot evaluate(state) and every feature, mark deliveries, slips and the end.

Expected if the evaluation is sensible: the score mostly rises, dips on slips or when the rival
comes close, jumps at each delivery; in the losing run fuel_safety drops before the stranding.

Outputs (stamped): results/figures/eval_along_route.png, results/tables/eval_along_route
(one row per run: outcome, steps, deliveries, how the features behaved).
"""
from __future__ import annotations

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.game.evaluation import DEFAULT_WEIGHTS, FEATURES, evaluate, features
from oel.game.state import from_simulator, is_terminal
from oel.search.registry import default_planner
from oel.search.uninformed import ucs
from oel.stamp import save_fig, save_table
from oel.world.problem import DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator

SERIES = "#2a78d6"
DELIVERY = "#1baf7a"
SLIP = "#eb6834"
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"
MAX_SEEDS = 50


def simulate(cfg, seed, actions):
    """One run of the plan with replanning; returns (report, list of GameStates after each step)."""
    problem = DeliveryProblem(cfg)
    states = []
    sim = Simulator(cfg, problem, np.random.default_rng(seed), on_step=lambda s: states.append(from_simulator(s)))
    rep = sim.run_plan(actions, RejoinReplanner(default_planner, ucs, cfg.rejoin_radius))
    return rep, states


def run_table(rep, states) -> pd.DataFrame:
    rows = []
    for k, (s, snap) in enumerate(zip(states, rep.timeline[1:])):
        f = features(s)
        terminal = is_terminal(s)[0]
        rows.append({"step": s.step, "event": snap["event"], "delivered": bin(s.delivered_mask).count("1"),
                     "fuel": s.fuel, "terminal": terminal,
                     "score": np.nan if terminal else evaluate(s), **f})
    return pd.DataFrame(rows)


def describe(name, seed, rep, df) -> dict:
    deliveries = df.step[df.delivered.diff().fillna(df.delivered) > 0].tolist()
    jumps = [df.score.iloc[i] - df.score.iloc[i - 1] for i in df.index[1:]
             if df.delivered.iloc[i] > df.delivered.iloc[i - 1] and not np.isnan(df.score.iloc[i])]
    slips = df.event.isin(["slip", "slip_failed"])
    other = df.score.diff()[~slips & ~(df.delivered.diff() > 0)].dropna()
    out = {"run": name, "seed": seed, "outcome": rep.outcome, "end_reason": rep.end_reason, "steps": rep.steps,
           "slips": rep.slips, "deliveries_at_steps": str(deliveries),
           "score_start": round(df.score.iloc[0], 2), "score_end": round(df.score.dropna().iloc[-1], 2),
           "mean_jump_at_delivery": round(float(np.mean(jumps)), 2) if jumps else None,
           "mean_change_on_slip": round(float(df.score.diff()[slips].mean()), 3),
           "mean_change_other_steps": round(float(other.mean()), 3),
           "min_interference": round(df.interference.min(), 2),
           "min_fuel_safety": round(df.fuel_safety.min(), 2)}
    # the steps before the end: when did fuel_safety last stay above 0.1?
    low = df.index[df.fuel_safety < 0.1]
    out["first_step_fuel_safety_below_0.1"] = int(df.step[low[0]]) if len(low) else None
    out["fuel_safety_last_10_steps"] = str([round(v, 2) for v in df.fuel_safety.tail(10)])
    return out


def plot(runs):
    rows = ["score"] + FEATURES
    fig, axes = plt.subplots(len(rows), len(runs), figsize=(13, 2.0 * len(rows) + 1), sharex="col")
    for col, (title, df) in enumerate(runs):
        delivered = df.step[df.delivered.diff().fillna(0) > 0]
        slips = df.step[df.event.isin(["slip", "slip_failed"])]
        for row, name in enumerate(rows):
            ax = axes[row, col]
            ax.plot(df.step, df[name], color=SERIES, lw=1.6)
            for x in delivered:
                ax.axvline(x, color=DELIVERY, lw=1.0, ls="--", alpha=0.9)
            if row == 0:
                ax.plot(slips, df.score[df.step.isin(slips)], ls="", marker="v", ms=3.5, color=SLIP,
                        label="slip")
                ax.set_title(title, fontsize=10)
            label = "evaluate()\n(default weights)" if name == "score" else f"{name}\n(weight {DEFAULT_WEIGHTS[name]:g})"
            if col == 0:
                ax.set_ylabel(label, fontsize=8)
            ax.grid(color=GRID, lw=0.7)
            ax.set_axisbelow(True)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.tick_params(labelsize=7)
        axes[-1, col].set_xlabel("step")
    handles = [plt.Line2D([], [], color=SERIES, lw=1.6, label="value at each step"),
               plt.Line2D([], [], color=DELIVERY, lw=1.0, ls="--", label="a parcel delivered"),
               plt.Line2D([], [], color=SLIP, marker="v", ls="", label="slip (score panel)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.025, 1, 0.975))
    path = save_fig(fig, "eval_along_route")
    plt.close(fig)
    return path


def run(cfg, log):
    t0 = time.perf_counter()
    actions = default_planner(DeliveryProblem(cfg)).actions
    rep_loss, states_loss = simulate(cfg, cfg.seed, actions)
    win_seed, rep_win, states_win = None, None, None
    for i in range(1, MAX_SEEDS + 1):
        rep, states = simulate(cfg, cfg.seed + i, actions)
        if rep.outcome == "win":
            win_seed, rep_win, states_win = cfg.seed + i, rep, states
            break
    runs, rows = [], []
    first = (f"default seed {cfg.seed}: {rep_loss.outcome} ({rep_loss.end_reason})", run_table(rep_loss, states_loss))
    runs.append(first)
    rows.append(describe("default seed", cfg.seed, rep_loss, first[1]))
    if rep_win is not None:
        second = (f"seed {win_seed}: {rep_win.outcome} ({rep_win.steps} steps)", run_table(rep_win, states_win))
        runs.append(second)
        rows.append(describe("first winning seed", win_seed, rep_win, second[1]))
    else:
        log.warning("no winning seed among the next %d", MAX_SEEDS)
    plot(runs)
    table = pd.DataFrame(rows)
    save_table(table, "eval_along_route")
    log.info("evaluation along two runs (%.0f s):\n%s", time.perf_counter() - t0, table.T.to_string())
    return table


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("eval_along_route"))
