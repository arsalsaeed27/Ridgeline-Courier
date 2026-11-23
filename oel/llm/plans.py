"""Planning service used by the LLM tools: a planner registry + an on-disk plan cache.

Every plan is stored as oel/llm/cache/plans/<plan_id>.json, where plan_id is a hash of
(algorithm, the resolved constraints, every config value that affects planning). So the same
request is never planned twice, tools can refer to a plan by its id, and the committed cache
lets run_all.py replay the LLM evaluation without re-planning. Simulations are cached the
same way in oel/llm/cache/sims/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from oel.search.result import run_timed
from oel.search.standin import ucs
from oel.stamp import get_logger
from oel.world.constraints import PlanConstraints
from oel.world.problem import TUNNEL, DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator

CACHE_DIR = Path(__file__).resolve().parent / "cache"
PLAN_DIR = CACHE_DIR / "plans"
SIM_DIR = CACHE_DIR / "sims"
CACHE_VERSION = 1   # bump if the planning rules change, so old cached plans are not reused

# name -> planner(problem) -> SearchResult. Laiba adds hers with register_planner("astar", astar).
PLANNERS = {"ucs": ucs}


def register_planner(name: str, planner) -> None:
    PLANNERS[name] = planner


def _log():
    return get_logger("plan_cache")


def _hash(obj) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(text.encode()).hexdigest()


def config_fingerprint(cfg) -> dict:
    """Every config value that changes what the planner returns (not slip/rival/seed)."""
    return {
        "grid": hashlib.sha256(np.ascontiguousarray(cfg.grid).tobytes()).hexdigest(),
        "elevation": hashlib.sha256(np.ascontiguousarray(cfg.elevation).tobytes()).hexdigest(),
        "start": list(cfg.start), "stops": [list(s) for s in cfg.stops],
        "terrain_cost": cfg.terrain_cost, "fuel_capacity": cfg.fuel_capacity,
        "fuel_burn": cfg.fuel_burn, "stations": [list(s) for s in cfg.stations],
        "depot_recharges": cfg.depot_recharges, "tunnels": [[list(a), list(b)] for a, b in cfg.tunnels],
        "tunnel_cost": cfg.tunnel_cost, "tunnel_fuel": cfg.tunnel_fuel,
        "hills": [cfg.up_cost, cfg.up_fuel, cfg.regen],
        "flags": [cfg.use_fuel, cfg.use_tunnels, cfg.use_hills],
    }


def plan_key(cfg, constraints: PlanConstraints, algorithm: str) -> str:
    resolved = constraints.resolved(cfg).to_dict()   # defaults filled in -> same request, same key
    return _hash({"v": CACHE_VERSION, "algorithm": algorithm, "constraints": resolved,
                  "config": config_fingerprint(cfg)})[:12]


def _summarise(problem, res) -> dict:
    """Facts about a solved plan that the tools report."""
    refuels = [list(s[:2]) for s in res.path[1:] if problem.is_refuel_point(s[:2])]
    order = []
    for before, after in zip(res.path, res.path[1:]):
        order += problem.delivered(after[2] & ~before[2])
    return {"length": len(res.actions), "refuel_cells": refuels,
            "tunnels_used": res.actions.count(TUNNEL), "delivery_order": order}


def plan(cfg, constraints: PlanConstraints, algorithm: str = "ucs") -> dict:
    """Plan (or load from the cache) and return the plan record. Raises KeyError for an
    unknown algorithm: the validator should catch that first."""
    planner = PLANNERS[algorithm]
    plan_id = plan_key(cfg, constraints, algorithm)
    path = PLAN_DIR / f"{plan_id}.json"
    if path.exists():
        _log().info("plan cache HIT  %s (%s, %s)", plan_id, algorithm, constraints.to_dict())
        record = json.loads(path.read_text())
        record["from_cache"] = True
        return record

    _log().info("plan cache MISS %s (%s, %s): planning...", plan_id, algorithm, constraints.to_dict())
    resolved = constraints.resolved(cfg)
    record = {"plan_id": plan_id, "algorithm": algorithm, "constraints": constraints.to_dict(),
              "resolved_constraints": resolved.to_dict(), "feasible": False, "reason": "",
              "cost": None, "actions": [], "path": [], "nodes_expanded": 0, "runtime_s": 0.0}

    blocked = constraints.blocked_cells(cfg)
    on_wall = [i for i, s in enumerate(cfg.stops) if tuple(s) in blocked]
    if on_wall:
        # quick check: no search needed to see that an avoided stop can't be delivered
        record["reason"] = f"stop(s) {on_wall} lie on avoided cells/terrain, so they can't be delivered"
    else:
        problem = DeliveryProblem(cfg, constraints=constraints)
        res = run_timed(planner, problem, measure_memory=False)
        record.update(nodes_expanded=res.nodes_expanded, runtime_s=round(res.runtime_s, 2))
        if not res.solved:
            record["reason"] = "no route satisfies the constraints (search space exhausted)"
        else:
            record.update(cost=res.cost, actions=list(res.actions),
                          path=[list(s) for s in res.path], **_summarise(problem, res))
            if constraints.max_cost is not None and res.cost > constraints.max_cost:
                record["reason"] = (f"the cheapest plan under the other constraints costs "
                                    f"{res.cost:.0f}, above max_cost {constraints.max_cost:.0f}")
            else:
                record["feasible"] = True
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))
    _log().info("plan %s: feasible=%s cost=%s nodes=%d (%.1f s) %s", plan_id, record["feasible"],
                record["cost"], record["nodes_expanded"], record["runtime_s"], record["reason"])
    record["from_cache"] = False
    return record


def load_plan(plan_id: str):
    """The stored plan record, or None if there is no such plan id."""
    path = PLAN_DIR / f"{plan_id}.json"
    return json.loads(path.read_text()) if path.exists() else None


def simulate(cfg, plan_id: str, seed: int) -> dict:
    """Run a stored plan in the simulator (slip + rival + replanning), cached by
    (plan, seed, simulator settings)."""
    record = load_plan(plan_id)
    sim_id = _hash({"v": CACHE_VERSION, "plan": plan_id, "seed": seed, "slip": cfg.slip,
                    "max_steps": cfg.max_steps, "radius": cfg.rejoin_radius,
                    "failed": cfg.failed_move_cost, "rival": "greedy_blocker"})[:12]
    path = SIM_DIR / f"{sim_id}.json"
    if path.exists():
        _log().info("sim cache HIT  %s (plan %s, seed %d)", sim_id, plan_id, seed)
        return json.loads(path.read_text())
    _log().info("sim cache MISS %s (plan %s, seed %d): simulating...", sim_id, plan_id, seed)
    constraints = PlanConstraints.from_dict(record["constraints"])
    problem = DeliveryProblem(cfg, constraints=constraints)
    sim = Simulator(cfg, problem, np.random.default_rng(seed))
    rep = sim.run_plan(record["actions"], RejoinReplanner(ucs, ucs, cfg.rejoin_radius))
    out = {"plan_id": plan_id, "seed": seed, "outcome": rep.outcome, "end_reason": rep.end_reason,
           "real_cost": rep.total_cost, "planned_cost": rep.planned_cost,
           "extra_cost": rep.extra_cost_text(), "steps": rep.steps, "slips": rep.slips,
           "failed_moves": rep.failed_moves, "waits": rep.waits,
           "replans": len(rep.replans), "full_replans": rep.n_full}
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out))
    return out
