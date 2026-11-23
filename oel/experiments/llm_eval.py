"""Part D evaluation: 20 English requests, three ways of answering them.

  direct           our planner run on the GOLD constraints (the reference; no LLM)
  llm              the LLM dispatcher with validation OFF
  llm_validation   the LLM dispatcher with validation ON

Grading is OUTCOME-based:
  plan requests      success = the LLM's final plan passes verify_plan against the GOLD
                     constraints AND costs at most 1% more than the direct plan (+ any required
                     tool was called, + any required number appears in the answer)
  infeasible/invalid success = the LLM's RESULT line says the same word as the gold
The argument diff vs gold only assigns labels: exact_args / equivalent_args (success),
ignored_constraint, invented_argument, false_infeasible, wrong_tool, other (failures), and
ambiguous_reading (a defensible alternative reading of a vague request: reported separately).

    python -m oel.experiments.llm_eval --gold-only   # plan the gold answers, write the gold table
    python -m oel.experiments.llm_eval --live        # run the LLM (fills the cache)
    python -m oel.experiments.llm_eval               # replay from the caches only
"""
from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from oel.config import ROOT
from oel.experiments.stats import wilson_ci
from oel.llm import plans, tools
from oel.llm.agent import LLMClient, run_agent
from oel.stamp import save_table, stamp
from oel.world.constraints import PlanConstraints, verify_plan

REQUESTS = ROOT / "oel" / "llm" / "requests.json"
GOLD_DOC = ROOT / "docs" / "llm_gold_answers.md"
TRACE_DOC = ROOT / "report" / "sections" / "part_d_traces.md"
COST_TOLERANCE = 0.01
FIELDS = ["stop_order", "avoid_terrain", "avoid_cells", "use_tunnels", "fuel_reserve", "max_cost"]
SUCCESS_LABELS = {"exact_args", "equivalent_args"}


def load_requests() -> list:
    return json.loads(REQUESTS.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- direct baseline (gold plans)
def _plan_worker(cfg, constraints_dict):
    rec = plans.plan(cfg, PlanConstraints.from_dict(constraints_dict), "ucs")
    return rec["plan_id"]


def gold_constraint_sets(requests) -> list:
    """Every distinct constraint set the grading needs: gold + alternative readings."""
    sets = []
    for req in requests:
        for c in [req["gold"].get("constraints")] + req["alternatives"]:
            if c is not None and c not in sets:
                sets.append(c)
    return sets


def fill_plan_cache(cfg, requests, log, workers: int = 3) -> None:
    """Plan every gold/alternative constraint set (3 in parallel; cached ones are instant)."""
    todo = [c for c in gold_constraint_sets(requests)
            if plans.load_plan(plans.plan_key(cfg, PlanConstraints.from_dict(c), "ucs")) is None]
    log.info("gold plans: %d constraint sets, %d not cached yet", len(gold_constraint_sets(requests)), len(todo))
    if todo:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(workers) as pool:
            list(pool.map(_plan_worker, [cfg] * len(todo), todo))
        log.info("gold plans done in %.0f s", time.perf_counter() - t0)


def direct_record(cfg, constraints_dict) -> dict:
    return plans.plan(cfg, PlanConstraints.from_dict(constraints_dict), "ucs")


def describe(constraints_dict) -> str:
    if not constraints_dict:
        return "no constraints"
    return ", ".join(f"{k}={v}" for k, v in constraints_dict.items())


def write_gold_doc(cfg, requests) -> str:
    rows = ["| id | tier | request | gold answer | reason |", "|---|---|---|---|---|"]
    for req in requests:
        g = req["gold"]
        if g["kind"] == "plan":
            rec = direct_record(cfg, g["constraints"])
            answer = f"plan: {describe(g['constraints'])}"
            answer += f" -> cost {rec['cost']:.0f}" if rec["feasible"] else f" -> **INFEASIBLE?** {rec['reason']}"
        elif g["kind"] == "infeasible":
            rec = direct_record(cfg, g["constraints"])
            answer = f"infeasible ({describe(g['constraints'])})"
            answer += f" -> planner: {rec['reason']}" if not rec["feasible"] else " -> **planner found a plan!**"
        else:
            answer = "invalid"
        reason = req["reason"]
        for alt in req["alternatives"]:
            rec = direct_record(cfg, alt)
            alt_cost = f"cost {rec['cost']:.0f}" if rec["feasible"] else "infeasible"
            reason += f"; alt reading {describe(alt)} -> {alt_cost}"
        rows.append(f"| {req['id']} | {req['tier']} | {req['text']} | {answer} | {reason} |")
    text = (f"_{stamp()}_\n\n# Part D: gold answers for the 20 LLM requests\n\n"
            "Written by us, not by the LLM. Costs are the direct (stand-in UCS) plans on the gold "
            f"constraints, with the default planning fuel reserve {cfg.fuel_reserve}.\n\n" + "\n".join(rows) + "\n")
    GOLD_DOC.write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------- grading
def _resolved(cfg, constraints_dict):
    return PlanConstraints.from_dict(constraints_dict).resolved(cfg).to_dict()


def _plan_ok(cfg, plan_rec, constraints_dict) -> bool:
    """Does this plan satisfy `constraints_dict` at (near) the direct planner's cost?"""
    direct = direct_record(cfg, constraints_dict)
    if not direct["feasible"] or not plan_rec or not plan_rec["feasible"]:
        return False
    if verify_plan(plan_rec["actions"], PlanConstraints.from_dict(constraints_dict), cfg):
        return False
    return plan_rec["cost"] <= direct["cost"] * (1 + COST_TOLERANCE) + 1e-9


def _final_args(cfg, run) -> dict | None:
    """The plan_route arguments that produced the final plan (else the last plan_route call)."""
    calls = run["plan_calls"]
    if not calls:
        return None
    for args in reversed(calls):
        try:
            c = {k: v for k, v in args.items() if k in FIELDS}
            if plans.plan_key(cfg, PlanConstraints.from_dict(c), args.get("algorithm", "ucs")) == run["result"]["plan_id"]:
                return args
        except Exception:
            continue
    return calls[-1]


def _diff_labels(cfg, args, gold_constraints) -> set:
    """Compare the LLM's arguments with the gold, field by field (defaults filled in)."""
    try:
        llm = _resolved(cfg, {k: v for k, v in args.items() if k in FIELDS})
    except Exception:
        return {"other"}
    gold = _resolved(cfg, gold_constraints)
    default = _resolved(cfg, {})
    labels = set()
    for field in FIELDS:
        if llm[field] != gold[field]:
            labels.add("ignored_constraint" if gold[field] != default[field] else "invented_argument")
    return labels


def _answer_has(cfg, run, plan_rec, check) -> bool:
    """For questions: the number the user asked for appears in the final answer."""
    if check is None:
        return True
    if check == "cost":
        value = plan_rec["cost"]
    else:
        value = tools.fuel_report(cfg, plan_rec["plan_id"])[check]
    numbers = {float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", run["final_text"])}
    return float(value) in numbers


def grade(cfg, req, run) -> dict:
    gold = req["gold"]
    result = run["result"]
    used = [s["action"]["tool"] for s in run["steps"] if s.get("action")]
    out = {"success": False, "labels": set(), "cost": None, "ambiguous": False}
    if run["error"] and run["error"].startswith(("api_failure", "cache_miss")):
        out["labels"] = {run["error"].split(":")[0]}
        return out

    plan_rec = plans.load_plan(result["plan_id"]) if result["kind"] == "plan" else None
    if plan_rec and plan_rec["feasible"]:
        out["cost"] = plan_rec["cost"]

    if gold["kind"] == "plan":
        if result["kind"] in ("infeasible", "invalid"):
            out["labels"] = {"false_infeasible"}
        elif result["kind"] == "none" or not plan_rec:
            out["labels"] = {"wrong_tool"} if "plan_route" not in used else {"other"}
        elif _plan_ok(cfg, plan_rec, gold["constraints"]):
            missing = [t for t in req["needs_tools"] if t not in used]
            if missing:
                out["labels"] = {"wrong_tool"}
            elif not _answer_has(cfg, run, plan_rec, req["answer_check"]):
                out["labels"] = {"other"}          # right plan, but the asked number is missing/wrong
            else:
                out["success"] = True
                args = _final_args(cfg, run) or {}
                exact = not _diff_labels(cfg, args, gold["constraints"])
                out["labels"] = {"exact_args" if exact else "equivalent_args"}
        elif any(_plan_ok(cfg, plan_rec, alt) for alt in req["alternatives"]):
            out["ambiguous"] = True
            out["labels"] = {"ambiguous_reading"}
        else:
            args = _final_args(cfg, run) or {}
            out["labels"] = _diff_labels(cfg, args, gold["constraints"]) or {"other"}
    else:   # gold infeasible / invalid
        if result["kind"] == gold["kind"]:
            out["success"] = True
            out["labels"] = {"exact_args"}
        elif result["kind"] == "plan" and plan_rec and any(_plan_ok(cfg, plan_rec, alt) for alt in req["alternatives"]):
            out["ambiguous"] = True
            out["labels"] = {"ambiguous_reading"}
        elif result["kind"] == "plan":
            out["labels"] = {"ignored_constraint"}   # it planned around the impossible part
        elif result["kind"] == "none" and not used:
            out["labels"] = {"wrong_tool"}
        else:
            out["labels"] = {"other"}                # e.g. said infeasible for an invalid request
    return out


# ---------------------------------------------------------------- the three modes
def run_direct(cfg, requests) -> list:
    rows = []
    for req in requests:
        g = req["gold"]
        row = {"id": req["id"], "tier": req["tier"], "mode": "direct", "gold": g["kind"],
               "result": "", "success": None, "labels": "", "cost": None, "direct_cost": None,
               "cost_gap_pct": None, "tool_calls": 0, "rejected_calls": 0}
        if g["kind"] == "invalid":
            row.update(result="n/a (no constraints to plan)")
        else:
            rec = direct_record(cfg, g["constraints"])
            row["result"] = "plan" if rec["feasible"] else "infeasible"
            row["success"] = row["result"] == g["kind"]
            row["cost"] = row["direct_cost"] = rec["cost"] if rec["feasible"] else None
            row["cost_gap_pct"] = 0.0 if rec["feasible"] else None
        rows.append(row)
    return rows


def run_llm_mode(cfg, requests, validation: bool, log) -> tuple:
    client = LLMClient(cfg)
    rows = []
    mode = "llm_validation" if validation else "llm"
    for req in requests:
        t0 = time.perf_counter()
        run = run_agent(cfg, req["id"], req["text"], client, validation)
        g = grade(cfg, req, run)
        direct_cost = None
        if req["gold"]["kind"] == "plan":
            direct_cost = direct_record(cfg, req["gold"]["constraints"])["cost"]
        gap = None
        if g["cost"] is not None and direct_cost:
            gap = round(100 * (g["cost"] - direct_cost) / direct_cost, 2)
        rows.append({"id": req["id"], "tier": req["tier"], "mode": mode, "gold": req["gold"]["kind"],
                     "result": run["result"]["kind"], "success": g["success"],
                     "labels": ",".join(sorted(g["labels"])), "cost": g["cost"],
                     "direct_cost": direct_cost, "cost_gap_pct": gap, "tool_calls": run["tool_calls"],
                     "rejected_calls": sum(1 for s in run["steps"] if s.get("validation") == "rejected"),
                     "error": run["error"] or ""})
        log.info("%s %-3s %-10s -> %-10s %s [%s] (%d tool calls, %.0f s)", mode, req["id"],
                 req["gold"]["kind"], run["result"]["kind"], "OK " if g["success"] else "BAD",
                 rows[-1]["labels"], run["tool_calls"], time.perf_counter() - t0)
    return rows, client.api_failures


def summarise(rows: list, api_failures: dict) -> tuple:
    df = pd.DataFrame(rows)
    summary, errors = [], []
    for mode, grp in df.groupby("mode", sort=False):
        graded = grp[grp.success.notna()]
        amb = graded[graded.labels.str.contains("ambiguous_reading", na=False)]
        counted = graded.drop(amb.index)
        wins = int(counted.success.sum())
        n = len(counted)
        lo, hi = wilson_ci(wins, n)
        gaps = counted.cost_gap_pct.dropna()
        summary.append({"mode": mode, "graded": n, "successes": wins,
                        "success_rate": round(wins / n, 3) if n else None,
                        "ci_low": round(lo, 3), "ci_high": round(hi, 3),
                        "ambiguous_readings": len(amb),
                        "mean_cost_gap_pct": round(gaps.mean(), 2) if len(gaps) else None,
                        "mean_tool_calls": round(grp.tool_calls.mean(), 2) if mode != "direct" else None,
                        "validator_rejections": int(grp.rejected_calls.sum()),
                        "api_failures": api_failures.get(mode, 0)})
        if mode != "direct":
            counts = {}
            for labels in grp.labels:
                for label in filter(None, labels.split(",")):
                    counts[label] = counts.get(label, 0) + 1
            errors.append({"mode": mode, **counts})
    order = ["exact_args", "equivalent_args", "ambiguous_reading", "wrong_tool", "invented_argument",
             "ignored_constraint", "false_infeasible", "other", "api_failure", "cache_miss"]
    err_df = pd.DataFrame(errors).reindex(columns=["mode"] + order).fillna(0)
    for col in order:
        err_df[col] = err_df[col].astype(int)
    return pd.DataFrame(summary), err_df


# ---------------------------------------------------------------- trace write-up
def write_trace_doc(rows) -> str | None:
    """One success (validation ON) and one failure that validation fixed, labelled with
    Sense / Reason / Act."""
    df = pd.DataFrame(rows)
    on = df[df["mode"] == "llm_validation"].set_index("id")
    off = df[df["mode"] == "llm"].set_index("id")
    fixed = [i for i in on.index if on.loc[i, "success"] and not off.loc[i, "success"]
             and on.loc[i, "rejected_calls"] > 0]
    fixed = fixed or [i for i in on.index if on.loc[i, "success"] and not off.loc[i, "success"]]
    good = [i for i in on.index if on.loc[i, "success"] and on.loc[i, "tier"] == "hard"] or \
           [i for i in on.index if on.loc[i, "success"]]
    if not good:
        return None
    parts = [f"_{stamp()}_", "", "# Part D: two annotated traces", "",
             "Each ReAct step maps onto the agent cycle: **Observation = Sense** (what the agent "
             "perceives from a tool), **Thought = Reason** (the model's reasoning), "
             "**Action = Act** (one tool call).", ""]
    picks = [("A successful run (validation ON)", "llm_validation", good[0])]
    if fixed:
        picks.append(("A failure WITHOUT validation ...", "llm", fixed[0]))
        picks.append(("... that validation fixed", "llm_validation", fixed[0]))
    for title, mode, rid in picks:
        trace = json.loads((ROOT / "results" / "logs" / "llm_traces" / mode / f"{rid}.json").read_text(encoding="utf-8"))
        parts += [f"## {title}: {rid}", "", f"**Request:** {trace['request']}", ""]
        for k, s in enumerate(trace["steps"], 1):
            if s.get("thought"):
                parts.append(f"{k}. **Reason (Thought):** {s['thought'].strip()[:500]}")
            if s.get("action"):
                parts.append(f"   **Act (Action):** `{s['action']['tool']}({json.dumps(s['action']['arguments'])})`")
                obs = json.dumps(s["observation"])
                parts.append(f"   **Sense (Observation):** `{obs[:400]}{' ...' if len(obs) > 400 else ''}`")
            if s.get("answer"):
                parts.append(f"   **Final answer:** {s['answer'].strip()[:500]}")
        parts += ["", f"Result: {trace['result']}; grade: "
                  f"{(on if mode == 'llm_validation' else off).loc[rid, 'labels']}", ""]
    TRACE_DOC.parent.mkdir(parents=True, exist_ok=True)
    TRACE_DOC.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return str(TRACE_DOC)


# ---------------------------------------------------------------- entry points
def run(cfg, log, gold_only: bool = False):
    requests = load_requests()
    missing = [c for c in gold_constraint_sets(requests)
               if plans.load_plan(plans.plan_key(cfg, PlanConstraints.from_dict(c), "ucs")) is None]
    if cfg.quick and missing and not cfg.llm_live:
        # e.g. a viva live change (--no-hills, --stop ...): every plan would be new (~5 min) and
        # the cached LLM replies no longer match the new tool outputs
        log.info("Part D skipped in --quick: %d gold plans are not cached for this config "
                 "(run python -m oel.experiments.llm_eval --live with the same flags)", len(missing))
        return None
    fill_plan_cache(cfg, requests, log)
    write_gold_doc(cfg, requests)
    log.info("gold answers written to %s", GOLD_DOC.relative_to(ROOT))
    if gold_only:
        return None
    rows = run_direct(cfg, requests)
    api_failures = {}
    for validation in (False, True):
        mode_rows, fails = run_llm_mode(cfg, requests, validation, log)
        rows += mode_rows
        api_failures["llm_validation" if validation else "llm"] = fails
    summary, errors = summarise(rows, api_failures)
    save_table(pd.DataFrame(rows), "llm_eval_requests")
    save_table(summary, "llm_eval_summary")
    save_table(errors, "llm_eval_errors")
    doc = write_trace_doc(rows)
    log.info("LLM evaluation summary:\n%s", summary.to_string(index=False))
    log.info("error labels:\n%s", errors.to_string(index=False))
    if doc:
        log.info("trace write-up: %s", Path(doc).relative_to(ROOT))
    return summary


if __name__ == "__main__":
    from oel.config import parse_cli
    from oel.stamp import get_logger

    argv = [a for a in sys.argv[1:] if a != "--gold-only"]
    run(parse_cli(argv), get_logger("llm_eval"), gold_only="--gold-only" in sys.argv)
