"""Reusable experiment framework (Part B; Ali and Rayyan can use it too).

    scenarios = make_scenarios(30)                       # 30 seeded variations of OUR map
    df = run_experiment([Variant("A*", "astar", "h_ours"), ...], n=30, name="my_exp")
    summary = summarise(df)                              # mean [95% bootstrap CI] per variant

1. SCENARIOS. One scenario = our real map with the 5 delivery stops re-drawn: free cells that
   are reachable from the depot and are not a station, a tunnel end or the start. All twists
   stay as they are (fuel, stations, tunnels, hills). Scenario i uses
   numpy.random.default_rng(BASE_SEED + SCENARIO_OFFSET + i), so the same seed always gives
   the same scenarios. A draw for which the default planner finds no plan with the default
   planning reserve of 20 (e.g. the fuel limit makes a stop unreachable) is redrawn with the
   same rng, so the same 30 scenarios work for reserve 0 and reserve 20. vary_start=True also moves the
   start (= the depot, which recharges) to a random free reachable cell.
2. RUNS. A Variant names a planner and heuristic from the registries (by NAME, so the worker
   processes can look them up) plus keyword options. Every (scenario, variant) pair is one
   run, done in a process pool and stored as one row of a tidy DataFrame. The optimal cost of
   each scenario comes from the reference planner (A* + h_ours + fuel pruning, proven optimal
   and tested against UCS), so every row also has gap_pct = how much worse than optimal.
3. CACHE. Each row is stored in oel/experiments/cache/<name>.json under a hash of (scenario,
   variant, planning config, FRAMEWORK_VERSION). A rerun with the same settings is instant;
   a live change (e.g. --no-hills) gives new keys and is computed. Bump FRAMEWORK_VERSION if
   the planners change in a way that changes their results. (The cache is not under results/,
   because every file there must carry the stamp.)
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from oel.config import BASE_SEED, load_config
from oel.experiments.routes import route_facts
from oel.experiments.stats import bootstrap_mean_ci, wilson_ci
from oel.search import registry
from oel.search.heuristics import ALL_HEURISTICS
from oel.world.problem import TUNNEL, DeliveryProblem

CACHE_DIR = Path(__file__).resolve().parent / "cache"
FRAMEWORK_VERSION = 1
SCENARIO_OFFSET = 5000            # scenario seeds: BASE_SEED + 5000 + i (small instances use + 1000)
WORKERS = 4                       # one full-map UCS needs ~400 MB, so 4 at once is safe on 16 GB
FEASIBILITY_STATES = 2_000_000    # memory cap for the feasibility check of a drawn scenario
FEASIBILITY_RESERVE = 20          # a drawn scenario must be feasible with this planning reserve


# ---------------------------------------------------------------- variants
@dataclasses.dataclass(frozen=True)
class Variant:
    """One planner setting. planner / heuristic are registry names; options are extra keyword
    arguments, e.g. (("prune_dominated", True),). slow=True: only run in full mode (in --quick
    it is read from the cache if it is there, else left out)."""
    label: str
    planner: str
    heuristic: str | None = None
    options: tuple = ()
    slow: bool = False
    count_distinct: bool = False     # also count DIFFERENT states expanded (measurement only)

    def kwargs(self) -> dict:
        out = dict(self.options)
        if self.heuristic:
            out["heuristic"] = ALL_HEURISTICS[self.heuristic]
        return out

    def key(self) -> dict:
        return {"planner": self.planner, "heuristic": self.heuristic, "options": list(self.options),
                "count_distinct": self.count_distinct}


REFERENCE = Variant(registry.DEFAULT_LABEL, registry.DEFAULT_PLANNER, registry.DEFAULT_HEURISTIC)


# ---------------------------------------------------------------- scenarios
def planning_fingerprint(cfg) -> dict:
    """Everything that changes a plan: the plan cache's fingerprint + the planning reserve."""
    from oel.llm.plans import config_fingerprint     # local import: keeps worker start-up light
    return {**config_fingerprint(cfg), "reserve": cfg.fuel_reserve if cfg.use_fuel else 0}


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def candidate_cells(cfg) -> list:
    """Cells a stop (or a moved start) may use: free, reachable from the depot by normal moves,
    and not a station, a tunnel end or the start."""
    reach = cfg.reachable_from_start()
    banned = {tuple(cfg.start)} | {tuple(s) for s in cfg.stations}
    for a, b in cfg.tunnels:
        banned |= {tuple(a), tuple(b)}
    return [(int(r), int(c)) for r, c in np.argwhere(reach) if (int(r), int(c)) not in banned]


def make_scenario(index: int, base_cfg=None, vary_start: bool = False, seed: int = BASE_SEED):
    """Scenario number `index`: a copy of the config with new stops (and maybe a new start)."""
    base = base_cfg if base_cfg is not None else load_config()
    rng = np.random.default_rng(seed + SCENARIO_OFFSET + index)
    cells = candidate_cells(base)
    k = len(base.stops)
    for _attempt in range(50):
        scen = dataclasses.replace(base, stops=list(base.stops), overrides=list(base.overrides))
        picks = rng.choice(len(cells), size=k + (1 if vary_start else 0), replace=False)
        chosen = [cells[i] for i in picks]
        if vary_start:
            scen.start = chosen.pop()
        scen.stops = chosen
        # feasible even with the default planning reserve (stricter than reserve 0), so the
        # SAME scenarios serve every reserve setting
        strict = max(int(scen.fuel_reserve), FEASIBILITY_RESERVE)
        res = registry.default_planner(DeliveryProblem(scen, fuel_reserve=strict),
                                       max_states=FEASIBILITY_STATES)
        if res.solved:
            scen.instance_id = f"{base.instance_id}-scen{index}"
            return scen
    raise RuntimeError(f"no feasible scenario for index {index}")


def make_scenarios(n: int = 30, base_cfg=None, vary_start: bool = False, seed: int = BASE_SEED) -> list:
    """n scenarios (deterministic). The stop lists are cached, because checking feasibility
    plans each draw once."""
    base = base_cfg if base_cfg is not None else load_config()
    # stops are re-drawn and the reserve doesn't change the draws, so neither is in the key
    key = _hash({"v": FRAMEWORK_VERSION, "n": n, "vary_start": vary_start, "seed": seed,
                 "base": {k: v for k, v in planning_fingerprint(base).items() if k not in ("stops", "reserve")}})
    path = CACHE_DIR / "scenario_sets.json"     # (separate from the row caches)
    store = json.loads(path.read_text()) if path.exists() else {}
    if key in store:
        out = []
        for i, entry in enumerate(store[key]):
            scen = dataclasses.replace(base, stops=[tuple(s) for s in entry["stops"]],
                                       start=tuple(entry["start"]), overrides=list(base.overrides))
            scen.instance_id = f"{base.instance_id}-scen{i}"
            out.append(scen)
        return out
    out = [make_scenario(i, base, vary_start, seed) for i in range(n)]
    store[key] = [{"start": list(s.start), "stops": [list(c) for c in s.stops]} for s in out]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=1))
    return out


# ---------------------------------------------------------------- one run
def encode_actions(actions) -> str:
    """'NNEW T S...' -> compact string (T = tunnel jump), so cached rows can redraw routes."""
    return "".join("T" if a == TUNNEL else a for a in actions)


def decode_actions(text: str) -> list:
    return [TUNNEL if ch == "T" else ch for ch in text]


class DistinctCounter:
    """Wraps a problem and remembers every state whose successors are asked for, i.e. every
    state that gets EXPANDED. nodes_expanded / len(seen) = how often a state was expanded on
    average: 1 for UCS, about 1 for A* (+ reopenings), much more for IDS / IDA*.
    This set is only for MEASURING; it is not part of any algorithm's memory."""

    def __init__(self, problem):
        self._problem = problem
        self.seen = set()

    def __getattr__(self, name):          # everything else behaves like the real problem
        return getattr(self._problem, name)

    def successors(self, state):
        self.seen.add(state)
        return self._problem.successors(state)


def run_variant(cfg, variant: Variant) -> dict:
    """Run one planner setting on one config and return the measured row (no cost gap yet)."""
    problem = DeliveryProblem(cfg)
    planner = registry.PLANNERS[variant.planner]
    kwargs = variant.kwargs()
    h_start = kwargs["heuristic"](problem.initial_state(), problem) if "heuristic" in kwargs else None
    searched = DistinctCounter(problem) if variant.count_distinct else problem
    t0 = time.perf_counter()
    res = planner(searched, **kwargs)
    runtime = time.perf_counter() - t0
    row = {"variant": variant.label, "solved": res.solved, "reason": res.stats.get("reason", "solved"),
           "cost": res.cost if res.solved else None, "nodes": res.nodes_expanded,
           "max_frontier": res.max_frontier,
           "stored_states": res.stats.get("stored_states", res.max_frontier),
           "reopened": res.stats.get("reopened"), "pruned": res.stats.get("pruned"),
           "runtime_s": round(runtime, 4), "h_start": h_start,
           "actions": encode_actions(res.actions) if res.solved else ""}
    if variant.count_distinct:
        row["distinct_expanded"] = len(searched.seen)
        if "re_expansions" in res.stats:
            row["re_expansions"] = res.stats["re_expansions"]
    if res.solved:
        facts = route_facts(problem, res.path, res.actions)
        facts.pop("refuel_cells")
        facts["delivery_order"] = "-".join(map(str, facts["delivery_order"]))
        row.update(facts)
    return row


def _job(cfg, variant):            # top level, so worker processes can import it
    return run_variant(cfg, variant)


# ---------------------------------------------------------------- the cache
class RowCache:
    """{key: row} stored in oel/experiments/cache/<name>.json. Only the parent process writes."""

    def __init__(self, name: str):
        self.path = CACHE_DIR / f"{name}.json"
        self.rows = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.dirty = False

    def get(self, key):
        return self.rows.get(key)

    def put(self, key, row):
        self.rows[key] = row
        self.dirty = True

    def save(self):
        if self.dirty:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.rows, indent=0, sort_keys=True))
            self.dirty = False


def row_key(cfg, variant: Variant) -> str:
    return _hash({"v": FRAMEWORK_VERSION, "cfg": planning_fingerprint(cfg), "variant": variant.key()})


def run_cached(jobs, name: str, compute_slow: bool = True, workers: int = WORKERS, log=None) -> list:
    """jobs: list of (tag dict, cfg, variant). Returns one row per job that was computed or
    found in the cache (tag fields first). Missing slow jobs are skipped if compute_slow is False."""
    cache = RowCache(name)
    rows, todo = [None] * len(jobs), []
    for k, (tag, cfg, variant) in enumerate(jobs):
        key = row_key(cfg, variant)
        hit = cache.get(key)
        if hit is not None:
            # the same settings may be cached under another experiment's label: use ours
            rows[k] = {**tag, **hit, "variant": variant.label, "from_cache": True}
        elif variant.slow and not compute_slow:
            continue
        else:
            todo.append((k, key))
    if todo:
        t0 = time.perf_counter()
        n_workers = min(workers, len(todo), os.cpu_count() or 1)
        with ProcessPoolExecutor(n_workers) as pool:
            futures = [(k, key, pool.submit(_job, jobs[k][1], jobs[k][2])) for k, key in todo]
            for done, (k, key, fut) in enumerate(futures, 1):
                row = fut.result()
                cache.put(key, row)
                rows[k] = {**jobs[k][0], **row, "variant": jobs[k][2].label, "from_cache": False}
                if done % 20 == 0:
                    cache.save()           # keep progress if a long run is interrupted
                    if log:
                        log.info("%s: %d/%d runs (%.0f s)", name, done, len(todo), time.perf_counter() - t0)
        cache.save()
    skipped = sum(r is None for r in rows)
    if todo and log:
        log.info("%s: computed %d runs in %.0f s, %d from the cache", name, len(todo),
                 time.perf_counter() - t0, len(jobs) - len(todo) - skipped)
    if skipped and log:
        log.info("%s: %d slow runs not in the cache were skipped (run without --quick)", name, skipped)
    return [r for r in rows if r is not None]


# ---------------------------------------------------------------- the experiment
def run_experiment(variants, n: int = 30, name: str = "experiment", base_cfg=None,
                   vary_start: bool = False, compute_slow: bool = True, workers: int = WORKERS,
                   log=None) -> pd.DataFrame:
    """Run every variant on n scenarios. Returns a tidy DataFrame: one row per (scenario,
    variant) with cost, optimal_cost, gap_pct, nodes, stored_states, runtime_s, route facts..."""
    base = base_cfg if base_cfg is not None else load_config()
    scenarios = make_scenarios(n, base, vary_start)
    variants = list(variants)
    if REFERENCE not in variants:
        variants.append(REFERENCE)                  # always needed for the optimal cost
    jobs = [({"scenario": i, "reserve": base.fuel_reserve, "stops": str(s.stops), "start": str(s.start)}, s, v)
            for i, s in enumerate(scenarios) for v in variants]
    df = pd.DataFrame(run_cached(jobs, name, compute_slow, workers, log))
    best = df[df.variant == REFERENCE.label].set_index("scenario").cost
    df["optimal_cost"] = df.scenario.map(best)
    df["gap_pct"] = 100 * (df.cost - df.optimal_cost) / df.optimal_cost
    df["optimal"] = np.isclose(df.cost.astype(float), df.optimal_cost.astype(float))
    df["h_over_opt"] = df.h_start / df.optimal_cost
    order = {v.label: k for k, v in enumerate(variants)}
    return df.sort_values(["variant", "scenario"], key=lambda col: col.map(order) if col.name == "variant" else col)


def summarise(df: pd.DataFrame, metrics=("nodes", "runtime_s", "cost", "gap_pct", "stored_states"),
              by: str = "variant", seed: int = BASE_SEED) -> pd.DataFrame:
    """One row per group: runs, solved % [Wilson 95% CI], optimal %, and for each metric the
    mean with a 95% percentile-bootstrap CI (columns <metric>_mean, _lo, _hi; computed over the
    SOLVED runs). Bootstrap, not t: node counts are very skewed."""
    rows = []
    for group, g in df.groupby(by, sort=False):
        solved = g[g.solved]
        lo, hi = wilson_ci(len(solved), len(g))
        row = {by: group, "runs": len(g), "solved": len(solved),
               "solved_pct": 100 * len(solved) / len(g), "solved_lo": 100 * lo, "solved_hi": 100 * hi,
               "optimal_pct": 100 * float(solved.optimal.mean()) if len(solved) else math.nan}
        for m in metrics:
            values = solved[m].dropna().astype(float)
            mean, low, high = bootstrap_mean_ci(values, seed=seed) if len(values) else (math.nan,) * 3
            row.update({f"{m}_mean": mean, f"{m}_lo": low, f"{m}_hi": high})
        rows.append(row)
    return pd.DataFrame(rows)


def readable(summary: pd.DataFrame, metrics=("nodes", "runtime_s", "gap_pct"), by: str = "variant",
             digits=None) -> pd.DataFrame:
    """The summary as a report table: 'mean [low, high]' strings."""
    digits = digits or {"nodes": 0, "runtime_s": 2, "gap_pct": 1, "cost": 1, "stored_states": 0}
    out = pd.DataFrame({by: summary[by], "runs": summary.runs,
                        "solved % [95% CI]": [f"{p:.0f} [{lo:.0f}, {hi:.0f}]" for p, lo, hi in
                                             zip(summary.solved_pct, summary.solved_lo, summary.solved_hi)],
                        "optimal %": summary.optimal_pct.round(0)})
    for m in metrics:
        d = digits.get(m, 1)
        out[f"{m} mean [95% CI]"] = [
            "-" if math.isnan(a) else f"{a:,.{d}f} [{lo:,.{d}f}, {hi:,.{d}f}]"
            for a, lo, hi in zip(summary[f"{m}_mean"], summary[f"{m}_lo"], summary[f"{m}_hi"])]
    return out
