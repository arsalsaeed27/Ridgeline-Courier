"""The tools the LLM dispatcher can call. Each tool = a JSON schema (what the LLM sees) +
a Python function (what actually runs). The LLM never plans routes itself: it only picks
arguments; our own planner and simulator do the work.

    get_instance_info()   facts about the map (stops, stations, tunnels, costs, algorithms)
    plan_route(...)       plan with constraints -> plan_id, cost, feasible/infeasible + reason
    simulate(plan_id)     run a plan in the slippery world with the rival
    fuel_report(plan_id)  OUR TWIST TOOL: fuel along the route, refuels, downhill regen, climb
"""
from __future__ import annotations

import dataclasses

from oel.config import TERRAINS
from oel.search.standin import ucs
from oel.world.constraints import PlanConstraints
from oel.world.problem import TUNNEL, DeliveryProblem

from oel.llm import plans

DEFAULT_SIM_SEED = 0

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_instance_info",
        "description": "Facts about the city: delivery stops (index -> cell, terrain, height, "
                       "distance from the depot), charging stations, tunnels, fuel capacity, "
                       "terrain costs and the available planning algorithms. Call this instead "
                       "of guessing.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "plan_route",
        "description": "Plan a route that delivers all 5 parcels, starting at the depot with a "
                       "full tank. Optional constraints; leave out any the user did not ask for. "
                       "Returns plan_id, cost, length, refuels, tunnels used, and feasible or "
                       "infeasible with a reason.",
        "parameters": {"type": "object", "properties": {
            "algorithm": {"type": "string", "description": "planner name, e.g. 'ucs'"},
            "stop_order": {"type": "array", "items": {"type": "integer"},
                           "description": "stop indices to deliver first, in this order, "
                                          "before all other stops (e.g. [3] = stop 3 first)"},
            "avoid_terrain": {"type": "array", "items": {"type": "string"},
                              "description": "terrain types to never enter: road, grass, mud, ford"},
            "avoid_cells": {"type": "array", "items": {"type": "array", "items": {"type": "integer"},
                                                        "minItems": 2, "maxItems": 2},
                            "description": "cells [row, col] to never enter"},
            "use_tunnels": {"type": "boolean", "description": "false = never use tunnels"},
            "fuel_reserve": {"type": "integer",
                             "description": "minimum fuel to keep in the tank at all times "
                                            "(default: the configured reserve)"},
            "max_cost": {"type": "number", "description": "maximum allowed total path cost"}},
            "required": ["algorithm"]}}},
    {"type": "function", "function": {
        "name": "simulate",
        "description": "Execute a planned route in the real world (moves slip 25% of the time, "
                       "a rival blocker moves around, the agent replans). Returns the outcome "
                       "(win/loss/draw), the real cost, slips and replans.",
        "parameters": {"type": "object", "properties": {
            "plan_id": {"type": "string"},
            "seed": {"type": "integer", "description": "random seed (default 0)"}},
            "required": ["plan_id"]}}},
    {"type": "function", "function": {
        "name": "fuel_report",
        "description": "Fuel and hills along a planned route: fuel level after every move, where "
                       "it refuels, where downhill regenerative braking recovers fuel, the "
                       "minimum fuel reached, and the total height climbed.",
        "parameters": {"type": "object", "properties": {
            "plan_id": {"type": "string"}}, "required": ["plan_id"]}}},
]
TOOL_NAMES = [t["function"]["name"] for t in TOOL_SCHEMAS]


# ---------------------------------------------------------------- tool functions
_info_cache = {}


def get_instance_info(cfg) -> dict:
    key = id(cfg)
    if key not in _info_cache:
        # true path cost from the depot to each stop (all twists except the fuel limit), using
        # our own UCS with "reach this cell" as the goal
        no_fuel = _no_fuel_problem(cfg)
        stops = []
        for i, cell in enumerate(cfg.stops):
            cell = tuple(cell)
            res = ucs(no_fuel, is_goal=lambda s, cell=cell: s[:2] == cell)
            stops.append({"index": i, "cell": list(cell), "terrain": TERRAINS[cfg.grid[cell]],
                          "height": int(cfg.elevation[cell]),
                          "manhattan_from_depot": abs(cell[0] - cfg.start[0]) + abs(cell[1] - cfg.start[1]),
                          "path_cost_from_depot": res.cost})
        _info_cache[key] = {
            "grid_size": cfg.n, "depot": list(cfg.start), "stops": stops,
            "charging_stations": [list(s) for s in cfg.stations], "depot_recharges": cfg.depot_recharges,
            "tunnels": [[list(a), list(b)] for a, b in cfg.tunnels] if cfg.use_tunnels else [],
            "tunnel_cost": cfg.tunnel_cost, "tunnel_fuel": cfg.tunnel_fuel,
            "terrain_types": TERRAINS, "terrain_cost": cfg.terrain_cost, "fuel_burn": cfg.fuel_burn,
            "fuel_capacity": cfg.fuel_capacity, "default_fuel_reserve": cfg.fuel_reserve,
            "hills": {"up_cost_per_level": cfg.up_cost, "up_fuel_per_level": cfg.up_fuel,
                      "regen_per_level_down": cfg.regen, "enabled": cfg.use_hills},
            "algorithms": sorted(plans.PLANNERS),
            "notes": "Stops are numbered 0-4 (stop 0 is the first stop; there is no stop 5). "
                     "Cells are [row, col], row 0 at the top; "
                     "path_cost_from_depot ignores the fuel limit",
        }
    return _info_cache[key]


def _no_fuel_problem(cfg):
    """Same map without the fuel limit (for distances only)."""
    return DeliveryProblem(dataclasses.replace(cfg, use_fuel=False), constraints=PlanConstraints())


def plan_route(cfg, algorithm, stop_order=None, avoid_terrain=None, avoid_cells=None,
               use_tunnels=None, fuel_reserve=None, max_cost=None) -> dict:
    constraints = PlanConstraints.build(stop_order, avoid_terrain, avoid_cells, use_tunnels,
                                        fuel_reserve, max_cost)
    rec = plans.plan(cfg, constraints, algorithm)
    out = {"plan_id": rec["plan_id"], "feasible": rec["feasible"],
           "constraints_used": rec["resolved_constraints"]}
    if rec["cost"] is not None:
        out.update(cost=rec["cost"], length=rec["length"], refuels=len(rec["refuel_cells"]),
                   refuel_cells=rec["refuel_cells"], tunnels_used=rec["tunnels_used"],
                   delivery_order=rec["delivery_order"])
    if not rec["feasible"]:
        out["reason"] = rec["reason"]
    return out


def simulate(cfg, plan_id, seed=None) -> dict:
    rec = plans.load_plan(plan_id)
    if rec is None:
        return {"error": f"unknown plan_id {plan_id!r}"}
    if not rec["feasible"]:
        return {"error": f"plan {plan_id} is infeasible, nothing to simulate"}
    return plans.simulate(cfg, plan_id, DEFAULT_SIM_SEED if seed is None else int(seed))


def fuel_report(cfg, plan_id) -> dict:
    rec = plans.load_plan(plan_id)
    if rec is None:
        return {"error": f"unknown plan_id {plan_id!r}"}
    if not rec["actions"]:
        return {"error": f"plan {plan_id} has no route"}
    problem = DeliveryProblem(cfg, constraints=PlanConstraints.from_dict(rec["constraints"]))
    path = [tuple(s) for s in rec["path"]]
    profile = [path[0][3]]
    refuels, regen_steps = [], []
    lowest = (path[0][3], 0, list(path[0][:2]))   # (fuel, step, cell)
    climbed = descended = recovered = 0
    for step, (state, action, nxt) in enumerate(zip(path, rec["actions"], path[1:]), 1):
        _cell, _cost, use = problem.transition(state[:2], action)
        left = state[3] - use                     # tank level just after paying for the move
        if left < lowest[0]:
            lowest = (left, step, list(nxt[:2]))
        if problem.is_refuel_point(nxt[:2]):
            refuels.append({"step": step, "cell": list(nxt[:2]), "fuel_on_arrival": left})
        if action != TUNNEL and cfg.use_hills:
            dh = problem.height(nxt[:2]) - problem.height(state[:2])
            climbed += max(dh, 0)
            if dh < 0:
                descended -= dh
                recovered += cfg.regen * -dh
                regen_steps.append(step)
        profile.append(nxt[3])
    return {"plan_id": plan_id, "fuel_capacity": cfg.fuel_capacity,
            "planning_reserve": problem.reserve,
            "min_fuel": lowest[0], "min_fuel_step": lowest[1], "min_fuel_cell": lowest[2],
            "refuels": refuels, "height_climbed": climbed, "height_descended": descended,
            "fuel_recovered_by_regen": recovered, "regen_steps": regen_steps,
            "fuel_after_each_move": profile}


FUNCTIONS = {"get_instance_info": get_instance_info, "plan_route": plan_route,
             "simulate": simulate, "fuel_report": fuel_report}


def execute(cfg, name: str, args: dict) -> dict:
    """Run a tool with ALREADY-PARSED arguments. No validation here (see validator.py): with
    validation OFF, bad arguments reach the function and may crash; the agent reports that."""
    return FUNCTIONS[name](cfg, **args)
