"""What does the validation layer prevent, independent of any LLM?

Take the GOLD plan_route call of every request (18: the two "invalid" requests have none),
corrupt it in 10 ways, and run every corrupted call
  (a) straight into the tool, without validation -> what happens?
  (b) through the validator                     -> is it caught before anything runs?

Outcomes for (a):
  crash                  the tool raised an exception
  silent_ignore          a plan came back, identical in effect to the uncorrupted call: the
                         nonsense was ignored and nobody was told
  silent_wrong_plan      a plan came back that differs from the uncorrupted call's plan (wrong
                         answer, no warning), e.g. a negative fuel reserve lets fuel go below 0
  wasted_search          "infeasible" after a long (>= 5 s) search caused by a bad argument
  misleading_infeasible  "infeasible" quickly, but the reason doesn't name the real problem
  correct_error          the tool itself reported the real problem
No API calls. The results are cached in oel/llm/cache/fault_injection.json, so run_all.py
--quick can reuse them; run this module directly to recompute (about 15-25 min, 3 workers).
"""
from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from oel.experiments.llm_eval import load_requests
from oel.llm import plans, tools, validator
from oel.stamp import save_table
from oel.world.constraints import PlanConstraints, verify_plan

CACHE = Path(__file__).resolve().parents[1] / "llm" / "cache" / "fault_injection.json"
CACHE_VERSION = 1
WASTED_SECONDS = 5.0
WORKERS = 3
OUTCOMES = ["crash", "silent_ignore", "silent_wrong_plan", "wasted_search",
            "misleading_infeasible", "correct_error"]


# ---------------------------------------------------------------- the corruptions
def _blocked_cell(cfg) -> list:
    r, c = np.argwhere(cfg.grid == -1)[0]
    return [int(r), int(c)]


def corrupt(fault: str, args: dict, cfg) -> dict:
    """A copy of a gold plan_route call with one kind of mistake an LLM could make."""
    a = json.loads(json.dumps(args))   # deep copy
    order = a.get("stop_order", [])
    if fault == "nonexistent_stop":
        a["stop_order"] = [7] + order
    elif fault == "out_of_bounds_cell":
        a["avoid_cells"] = a.get("avoid_cells", []) + [[45, 3]]
    elif fault == "blocked_cell":
        a["avoid_cells"] = a.get("avoid_cells", []) + [_blocked_cell(cfg)]
    elif fault == "unknown_terrain":
        a["avoid_terrain"] = a.get("avoid_terrain", []) + ["lava"]
    elif fault == "unknown_algorithm":
        a["algorithm"] = "astar9000"
    elif fault == "negative_reserve":
        a["fuel_reserve"] = -5
    elif fault == "absurd_reserve":
        a["fuel_reserve"] = 500
    elif fault == "negative_max_cost":
        a["max_cost"] = -10
    elif fault == "duplicate_stops":
        a["stop_order"] = order + [order[0]] if order else [3, 3]
    elif fault == "stop_cell_contradiction":
        a["avoid_cells"] = a.get("avoid_cells", []) + [list(cfg.stops[0])]
    else:
        raise ValueError(fault)
    return a


FAULTS = ["nonexistent_stop", "out_of_bounds_cell", "blocked_cell", "unknown_terrain",
          "unknown_algorithm", "negative_reserve", "absurd_reserve", "negative_max_cost",
          "duplicate_stops", "stop_cell_contradiction"]


# ---------------------------------------------------------------- running one corrupted call
def _without_validation(cfg, args: dict) -> dict:
    """(a): call the tool directly. Runs in a worker process."""
    t0 = time.perf_counter()
    try:
        out = tools.plan_route(cfg, **args)
    except Exception as err:
        return {"status": "crash", "error": f"{type(err).__name__}: {err}"[:200],
                "seconds": time.perf_counter() - t0}
    rec = plans.load_plan(out["plan_id"])
    # planning time from the plan record (true even when the plan came from the cache)
    return {"status": "plan" if out["feasible"] else "infeasible", "plan_id": out["plan_id"],
            "cost": out.get("cost"), "reason": out.get("reason", ""), "seconds": rec["runtime_s"]}


def classify(cfg, result: dict, gold_args: dict) -> str:
    if result["status"] == "crash":
        return "crash"
    gold_c = {k: v for k, v in gold_args.items() if k != "algorithm"}
    gold_rec = plans.plan(cfg, PlanConstraints.from_dict(gold_c), "ucs")   # cached
    if result["status"] == "plan":
        rec = plans.load_plan(result["plan_id"])
        same = (gold_rec["feasible"] and rec["cost"] == gold_rec["cost"]
                and not verify_plan(rec["actions"], PlanConstraints.from_dict(gold_c), cfg))
        return "silent_ignore" if same else "silent_wrong_plan"
    if result["reason"].startswith("stop(s)"):
        return "correct_error"          # the planner's own contradiction pre-check
    return "wasted_search" if result["seconds"] >= WASTED_SECONDS else "misleading_infeasible"


def _fingerprint(cfg, calls) -> str:
    blob = json.dumps({"v": CACHE_VERSION, "config": plans.config_fingerprint(cfg),
                       "reserve": cfg.fuel_reserve, "calls": calls}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def gold_calls(requests) -> list:
    calls = []
    for req in requests:
        if "constraints" in req["gold"]:
            calls.append((req["id"], {"algorithm": "ucs", **req["gold"]["constraints"]}))
    return calls


# ---------------------------------------------------------------- entry point
def run(cfg, log, compute: bool = True):
    calls = gold_calls(load_requests())
    jobs = [(rid, fault, gold, corrupt(fault, gold, cfg)) for rid, gold in calls for fault in FAULTS]
    key = _fingerprint(cfg, [j[3] for j in jobs])
    cached = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    if cached.get("key") == key:
        log.info("fault injection: reusing %d cached results", len(cached["rows"]))
        rows = cached["rows"]
    elif not compute:
        log.info("fault injection skipped in --quick: no cached results for this config "
                 "(run python -m oel.experiments.validator_fault_injection)")
        return None
    else:
        log.info("fault injection: %d corrupted calls (%d gold calls x %d faults), %d workers",
                 len(jobs), len(calls), len(FAULTS), WORKERS)
        t0 = time.perf_counter()
        with ProcessPoolExecutor(WORKERS) as pool:
            results = list(pool.map(_without_validation, [cfg] * len(jobs), [j[3] for j in jobs]))
        rows = []
        for (rid, fault, gold, bad), res in zip(jobs, results):
            _clean, error = validator.validate(cfg, "plan_route", bad)
            rows.append({"request": rid, "fault": fault, "arguments": json.dumps(bad),
                         "without_validation": classify(cfg, res, gold),
                         "planning_seconds": round(res["seconds"], 2),
                         "detail": res.get("error") or res.get("reason") or f"cost {res.get('cost')}",
                         "caught_by_validator": error is not None, "validator_message": error or ""})
        log.info("fault injection computed in %.0f s", time.perf_counter() - t0)
        CACHE.write_text(json.dumps({"key": key, "rows": rows}, indent=1))

    df = pd.DataFrame(rows)
    table = []
    for fault in FAULTS + ["ALL"]:
        grp = df if fault == "ALL" else df[df.fault == fault]
        row = {"fault": fault, "calls": len(grp)}
        for outcome in OUTCOMES:
            row[f"no_val_{outcome}"] = int((grp.without_validation == outcome).sum())
        row["no_val_planning_s"] = round(grp.planning_seconds.sum(), 1)
        row["with_val_caught_pct"] = round(100 * grp.caught_by_validator.mean(), 1)
        table.append(row)
    summary = pd.DataFrame(table)
    save_table(summary, "validator_fault_injection")
    save_table(df, "validator_fault_injection_calls")
    log.info("fault injection:\n%s", summary.to_string(index=False))
    return summary


if __name__ == "__main__":
    import sys

    from oel.config import parse_cli
    from oel.stamp import get_logger

    run(parse_cli(sys.argv[1:]), get_logger("fault_injection"))
