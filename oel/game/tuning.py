"""Part C: tuning the evaluation weights by playing games (built in Turn 2, RUN by Ali in Turn 3).

You provide play_fn(weights, seed) -> "win" | "draw" | "loss": one full game of our agent
(Alpha-Beta with evaluate(state, weights)) against the blocker, with all randomness from `seed`.
It must be a TOP-LEVEL function (worker processes import it by name).

    df = grid_search(play_fn, {"interference": [1, 2, 4], "race": [0.5, 1.5, 3]}, n_games=30)
    best, history = coordinate_ascent(play_fn, DEFAULT_WEIGHTS, steps=3, n_games=30)
    plot_weight_heatmap(df, "interference", "race", name="tuning_heatmap")

How it is fair: every weight setting plays the SAME games (seeds seed, seed + 1, ...), so
differences between settings come from the weights, not from luckier slips or rival starts
("common random numbers"). Each setting's result is win / draw / loss rates with 95% Wilson CIs
(oel/experiments/stats.wilson_ci). Settings run in parallel processes and every finished setting
is cached (oel/experiments/cache/<cache_name>.json), keyed by play_fn's name, a version `tag`,
the weights and the seeds. Change `tag` whenever play_fn's behaviour changes.

Score used to compare settings: points = win rate + 0.5 x draw rate (a draw is half a win).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from oel.config import BASE_SEED
from oel.experiments.framework import RowCache
from oel.experiments.stats import wilson_ci
from oel.stamp import save_fig

OUTCOMES = ("win", "draw", "loss")
WORKERS = 4


# ---------------------------------------------------------------- playing one setting
def _play_setting(play_fn, weights: dict, seeds: list) -> list:
    """All games of one weight setting (runs inside a worker process)."""
    out = []
    for s in seeds:
        result = play_fn(dict(weights), int(s))
        if result not in OUTCOMES:
            raise ValueError(f"play_fn must return one of {OUTCOMES}, got {result!r}")
        out.append(result)
    return out


def _key(play_fn, tag: str, weights: dict, seeds: list) -> str:
    blob = {"fn": f"{play_fn.__module__}.{play_fn.__qualname__}", "tag": tag,
            "weights": {k: float(v) for k, v in sorted(weights.items())}, "seeds": list(map(int, seeds))}
    return hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()[:16]


def summarise_outcomes(outcomes: list) -> dict:
    """Counts, rates and 95% Wilson CIs of a list of 'win' / 'draw' / 'loss'."""
    n = len(outcomes)
    row = {"games": n}
    for o in OUTCOMES:
        k = outcomes.count(o)
        lo, hi = wilson_ci(k, n)
        row.update({f"{o}s": k, f"{o}_rate": k / n if n else float("nan"),
                    f"{o}_ci_low": lo, f"{o}_ci_high": hi})
    row["points"] = row["win_rate"] + 0.5 * row["draw_rate"]
    return row


def play_settings(play_fn, settings: list, n_games: int = 30, seed: int = BASE_SEED,
                  workers: int = WORKERS, cache_name: str = "tuning", tag: str = "", log=None) -> pd.DataFrame:
    """Play n_games for every weight setting (a list of dicts). One row per setting: the weights
    (one column each) + summarise_outcomes(). Cached; parallel when workers > 1."""
    seeds = [seed + i for i in range(n_games)]
    cache = RowCache(cache_name)
    results, todo = {}, []
    for k, w in enumerate(settings):
        key = _key(play_fn, tag, w, seeds)
        hit = cache.get(key)
        if hit is not None:
            results[k] = hit
        else:
            todo.append((k, key))
    t0 = time.perf_counter()
    if todo:
        n_workers = min(workers, len(todo), os.cpu_count() or 1)
        if n_workers <= 1:
            for k, key in todo:
                results[k] = _play_setting(play_fn, settings[k], seeds)
                cache.put(key, results[k])
        else:
            with ProcessPoolExecutor(n_workers) as pool:
                futures = [(k, key, pool.submit(_play_setting, play_fn, settings[k], seeds)) for k, key in todo]
                for k, key, fut in futures:
                    results[k] = fut.result()
                    cache.put(key, results[k])
        cache.save()
    if log:
        log.info("tuning: %d settings x %d games (%d played, %d cached) in %.0f s", len(settings), n_games,
                 len(todo), len(settings) - len(todo), time.perf_counter() - t0)
    rows = [{**{k: float(v) for k, v in w.items()}, **summarise_outcomes(results[i])}
            for i, w in enumerate(settings)]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- grid search
def grid_search(play_fn, weight_grid: dict, n_games: int = 30, seed: int = BASE_SEED, base_weights=None,
                workers: int = WORKERS, cache_name: str = "tuning", tag: str = "", log=None) -> pd.DataFrame:
    """Every combination of the values in weight_grid ({weight name: [values]}); weights not in
    the grid keep their base_weights value. Returns one row per combination, best first."""
    base = dict(base_weights or {})
    names = list(weight_grid)
    settings = [{**base, **dict(zip(names, combo))} for combo in itertools.product(*weight_grid.values())]
    df = play_settings(play_fn, settings, n_games, seed, workers, cache_name, tag, log)
    return df.sort_values(["points", "win_rate"], ascending=False, kind="stable").reset_index(drop=True)


# ---------------------------------------------------------------- coordinate ascent
def coordinate_ascent(play_fn, start_weights: dict, steps: int = 3, n_games: int = 30, seed: int = BASE_SEED,
                      factors=(0.5, 2.0), workers: int = WORKERS, cache_name: str = "tuning", tag: str = "",
                      log=None) -> tuple:
    """Improve one weight at a time. In each round, for every weight in turn: try it multiplied by
    each factor (e.g. halved and doubled) with the others fixed, and keep the best setting (by
    points; ties keep the current one, so it only moves for a real improvement). Stops early when
    a whole round changes nothing. Uses the same games for every setting.
    Returns (best weights, history DataFrame: one row per setting tried, with round and weight)."""
    current = dict(start_weights)
    history = []
    best_points = None
    for rnd in range(1, steps + 1):
        changed = False
        for name in list(current):
            settings = [dict(current)] + [{**current, name: current[name] * f} for f in factors]
            df = play_settings(play_fn, settings, n_games, seed, workers, cache_name, tag, log)
            df.insert(0, "round", rnd)
            df.insert(1, "tuned", name)
            df["kept"] = False
            best = int(df.points.values.argmax())          # first max = the current setting on a tie
            df.loc[best, "kept"] = True
            history.append(df)
            if best != 0:
                current = settings[best]
                changed = True
            best_points = float(df.points.iloc[best])
        if log:
            log.info("coordinate ascent round %d: points %.3f, weights %s", rnd, best_points, current)
        if not changed:
            break
    return current, pd.concat(history, ignore_index=True)


# ---------------------------------------------------------------- heatmap
def plot_weight_heatmap(df: pd.DataFrame, x: str, y: str, name: str = "tuning_heatmap", value: str = "win_rate",
                        title: str = ""):
    """Win rate (or another column) for every pair of two weights, as a stamped heatmap.
    One sequential hue (light = low, dark = high); every cell is labelled with its value and n."""
    table = df.pivot_table(index=y, columns=x, values=value, aggfunc="mean").sort_index(ascending=False)
    games = df.pivot_table(index=y, columns=x, values="games", aggfunc="sum").reindex_like(table)
    fig, ax = plt.subplots(figsize=(1.3 * len(table.columns) + 3, 1.0 * len(table.index) + 2))
    im = ax.imshow(table.values * 100 if value.endswith("rate") else table.values, cmap="Blues",
                   vmin=0, vmax=100 if value.endswith("rate") else None, aspect="auto")
    for i in range(len(table.index)):
        for j in range(len(table.columns)):
            v = table.values[i, j]
            if np.isnan(v):
                continue
            shown = f"{100 * v:.0f}%" if value.endswith("rate") else f"{v:.2f}"
            dark = (v if value.endswith("rate") else 0) > 0.6
            ax.text(j, i, f"{shown}\nn={int(games.values[i, j])}", ha="center", va="center", fontsize=8,
                    color="white" if dark else "#212121")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels([f"{c:g}" for c in table.columns])
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels([f"{r:g}" for r in table.index])
    ax.set_xlabel(f"weight: {x}")
    ax.set_ylabel(f"weight: {y}")
    ax.set_title(title or f"{value.replace('_', ' ')} per weight pair", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.05, label="win rate (%)" if value.endswith("rate") else value)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = save_fig(fig, name)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- a stand-in play_fn
def demo_play_fn(weights: dict, seed: int) -> str:
    """A STAND-IN for Ali's real play_fn, only to test the tool. It plays no game: the chance of
    a win is highest at interference = 2 and race = 1 and falls off away from them; the same seed
    gives the same random number u for every setting (like replaying the same game)."""
    u = np.random.default_rng(seed).random()
    gap = (np.log2(weights.get("interference", 2.0) / 2.0)) ** 2 + (np.log2(weights.get("race", 1.0) / 1.0)) ** 2
    p_win = 0.8 * np.exp(-gap / 2)
    if u < p_win:
        return "win"
    return "draw" if u < p_win + 0.1 else "loss"
