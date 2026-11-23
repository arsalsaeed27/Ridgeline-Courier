"""Experiment: how big should the planner's fuel reserve be?

The optimal plan has zero fuel slack, so slips (which burn extra fuel) can strand the agent.
For each reserve in RESERVES: plan once with the stand-in UCS (the plan doesn't depend on the
seed), then simulate it with slip + rival + rejoin/full replanning for N seeds
(BASE_SEED + i). Record win/draw/loss, the mean cost of won runs and replans.

Outputs: results/tables/fuel_reserve.{csv,md}, results/figures/fuel_reserve.png
Runs in a small process pool (3 workers: one UCS needs ~360 MB of RAM).

    python -m oel.experiments.fuel_reserve            # 30 seeds per reserve
    python -m oel.experiments.fuel_reserve --quick    # 10 seeds per reserve
"""
import dataclasses
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.experiments.stats import wilson_ci
from oel.search.standin import ucs
from oel.stamp import save_fig, save_table
from oel.world.problem import DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator

RESERVES = [0, 5, 10, 15, 20]
SEEDS_FULL = 30
SEEDS_QUICK = 10
WORKERS = 3
TARGET_WIN_RATE = 0.80

# chart colours (single series per panel; recessive text/grid)
SERIES = "#2a78d6"
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"


# ---------------------------------------------------------------- work done in the pool
# These are top-level functions so the worker processes can import them.
def _plan(cfg, reserve):
    """Stand-in UCS plan with this reserve (the planned, no-slip cost)."""
    problem = DeliveryProblem(dataclasses.replace(cfg, fuel_reserve=reserve))
    t0 = time.perf_counter()
    res = ucs(problem)
    return reserve, res.actions if res.solved else None, res.cost, time.perf_counter() - t0


def _simulate(cfg, reserve, seed, actions):
    """One seeded run of the plan in the real world, with replanning."""
    run_cfg = dataclasses.replace(cfg, fuel_reserve=reserve, seed=seed)
    problem = DeliveryProblem(run_cfg)
    sim = Simulator(run_cfg, problem, np.random.default_rng(seed))
    replanner = RejoinReplanner(full_planner=ucs, rejoin_planner=ucs, radius=run_cfg.rejoin_radius)
    t0 = time.perf_counter()
    rep = sim.run_plan(actions, replan_fn=replanner)
    return {
        "reserve": reserve, "seed": seed, "outcome": rep.outcome, "end_reason": rep.end_reason,
        "cost": rep.total_cost, "steps": rep.steps, "slips": rep.slips,
        "replans": len(rep.replans), "full_replans": rep.n_full, "waits": rep.waits,
        "runtime_s": time.perf_counter() - t0,
    }


# ---------------------------------------------------------------- summary
def summarise(runs: pd.DataFrame, planned: dict) -> pd.DataFrame:
    rows = []
    for reserve, grp in runs.groupby("reserve"):
        n = len(grp)
        wins = int((grp.outcome == "win").sum())
        lo, hi = wilson_ci(wins, n)
        won = grp[grp.outcome == "win"]
        rows.append({
            "reserve": reserve,
            "planned_cost": planned[reserve],
            "runs": n,
            "wins": wins,
            "draws": int((grp.outcome == "draw").sum()),
            "losses": int((grp.outcome == "loss").sum()),
            "win_rate": round(wins / n, 3),
            "win_ci_low": round(lo, 3),
            "win_ci_high": round(hi, 3),
            "mean_cost_won": round(won.cost.mean(), 1) if len(won) else float("nan"),
            "mean_replans": round(grp.replans.mean(), 1),
            "mean_full_replans": round(grp.full_replans.mean(), 2),
            "mean_waits": round(grp.waits.mean(), 1),
            "mean_slips": round(grp.slips.mean(), 1),
            "mean_sim_runtime_s": round(grp.runtime_s.mean(), 1),
        })
    return pd.DataFrame(rows)


def choose_reserve(summary: pd.DataFrame) -> int:
    """Smallest reserve with win rate >= TARGET_WIN_RATE; else the one with the best win rate
    (ties -> the smaller reserve, i.e. the cheaper plan)."""
    good = summary[summary.win_rate >= TARGET_WIN_RATE]
    if len(good):
        return int(good.reserve.min())
    best = summary.sort_values(["win_rate", "reserve"], ascending=[False, True])
    return int(best.reserve.iloc[0])


def plot(summary: pd.DataFrame, n_seeds: int, chosen: int):
    """Two panels (no dual axis): win rate with 95% Wilson CI, and planned cost."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    x = summary.reserve.to_numpy()
    rate = summary.win_rate.to_numpy() * 100
    lo = rate - summary.win_ci_low.to_numpy() * 100
    hi = summary.win_ci_high.to_numpy() * 100 - rate

    ax1.errorbar(x, rate, yerr=[lo, hi], color=SERIES, lw=2, marker="o", ms=8,
                 capsize=4, elinewidth=1.2)
    ax1.axhline(TARGET_WIN_RATE * 100, color=TEXT_MUTED, ls="--", lw=1)
    ax1.text(x[0], TARGET_WIN_RATE * 100 + 2, f"target {TARGET_WIN_RATE:.0%}", color=TEXT_MUTED, fontsize=8)
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("win rate (%), 95% Wilson CI")
    ax1.set_title(f"Win rate ({n_seeds} seeded runs per reserve)", fontsize=10)

    ax2.plot(x, summary.planned_cost, color=SERIES, lw=2, marker="o", ms=8)
    for xi, yi in zip(x, summary.planned_cost):
        ax2.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points", xytext=(0, 7),
                     ha="center", fontsize=8, color=TEXT_MUTED)
    ax2.set_ylabel("planned (no-slip) cost")
    ax2.set_title("Price of the reserve: planned cost", fontsize=10)

    for ax in (ax1, ax2):
        ax.set_xlabel("planning fuel reserve")
        ax.set_xticks(x)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.axvline(chosen, color=TEXT_MUTED, lw=0.8, ls=":")
    ax1.text(chosen, 4, f" chosen: {chosen}", color=TEXT_MUTED, fontsize=8)
    fig.tight_layout()
    path = save_fig(fig, "fuel_reserve")
    plt.close(fig)
    return path


# ---------------------------------------------------------------- entry point
def run(cfg, log, reserves=RESERVES):
    n_seeds = SEEDS_QUICK if cfg.quick else SEEDS_FULL
    seeds = [cfg.seed + i for i in range(n_seeds)]   # derived from BASE_SEED (or --seed)
    t0 = time.perf_counter()
    with ProcessPoolExecutor(WORKERS) as pool:
        plans = {}
        planned = {}
        for reserve, actions, cost, secs in pool.map(_plan, [cfg] * len(reserves), reserves):
            log.info("reserve %2d: planned cost %.0f (%.0f s)", reserve, cost, secs)
            plans[reserve], planned[reserve] = actions, cost
        jobs = [(reserve, seed) for reserve in reserves if plans[reserve] for seed in seeds]
        futures = [pool.submit(_simulate, cfg, r, s, plans[r]) for r, s in jobs]
        runs = []
        for k, fut in enumerate(futures, 1):
            runs.append(fut.result())
            if k % 10 == 0 or k == len(futures):
                log.info("simulations done: %d/%d (%.0f s)", k, len(futures), time.perf_counter() - t0)

    runs = pd.DataFrame(runs)
    summary = summarise(runs, planned)
    chosen = choose_reserve(summary)
    save_table(summary, "fuel_reserve")
    save_table(runs, "fuel_reserve_runs")
    plot(summary, n_seeds, chosen)
    log.info("fuel reserve experiment: %d runs in %.0f s; best reserve by the rule: %d",
             len(runs), time.perf_counter() - t0, chosen)
    log.info("\n%s", summary.to_string(index=False))
    return summary, chosen


if __name__ == "__main__":
    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("fuel_reserve"))
