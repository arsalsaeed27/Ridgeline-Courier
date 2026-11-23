"""Validation layer between the LLM and the tools.

Two kinds of checks before a tool runs:
  1. shape (pydantic): the right argument names and types, nothing invented (extra="forbid");
  2. instance: the values make sense ON OUR MAP (stop exists, cell is on the grid and not a
     wall, terrain name is real, algorithm exists, numbers in sane ranges, no duplicate stops).
If anything fails the tool is NOT executed; the error text goes back to the LLM as its
Observation so it can fix the call (or tell the user the request is invalid).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, ValidationError

from oel.config import TERRAINS
from oel.llm import plans

MAX_COST_LIMIT = 100_000


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")   # an argument name we don't know = an error


class InstanceInfoArgs(_Strict):
    pass


class PlanRouteArgs(_Strict):
    algorithm: str
    stop_order: list[int] | None = None
    avoid_terrain: list[str] | None = None
    avoid_cells: list[list[int]] | None = None
    use_tunnels: bool | None = None
    fuel_reserve: int | None = None
    max_cost: float | None = None


class SimulateArgs(_Strict):
    plan_id: str
    seed: int | None = None


class FuelReportArgs(_Strict):
    plan_id: str


MODELS = {"get_instance_info": InstanceInfoArgs, "plan_route": PlanRouteArgs,
          "simulate": SimulateArgs, "fuel_report": FuelReportArgs}


def _instance_errors(cfg, name: str, a: BaseModel) -> list:
    """Checks that need our map/config. Returns a list of problems ([] = fine)."""
    errors = []
    n_stops = len(cfg.stops)
    if name == "plan_route":
        if a.algorithm not in plans.PLANNERS:
            errors.append(f"algorithm {a.algorithm!r} does not exist; available: {sorted(plans.PLANNERS)}")
        for s in a.stop_order or []:
            if not 0 <= s < n_stops:
                errors.append(f"stop {s} does not exist (valid stops are 0-{n_stops - 1})")
        if a.stop_order and len(set(a.stop_order)) != len(a.stop_order):
            errors.append(f"stop_order {a.stop_order} lists a stop twice")
        for t in a.avoid_terrain or []:
            if t not in TERRAINS:
                errors.append(f"terrain {t!r} does not exist; valid terrains: {TERRAINS}")
        for cell in a.avoid_cells or []:
            if len(cell) != 2:
                errors.append(f"cell {cell} must be [row, col]")
            elif not (0 <= cell[0] < cfg.n and 0 <= cell[1] < cfg.n):
                errors.append(f"cell {cell} is outside the {cfg.n}x{cfg.n} grid")
            elif cfg.grid[cell[0], cell[1]] == -1:
                errors.append(f"cell {cell} is already blocked (a wall), avoiding it means nothing")
        if a.fuel_reserve is not None and not 0 <= a.fuel_reserve < cfg.fuel_capacity:
            errors.append(f"fuel_reserve must be in 0..{cfg.fuel_capacity - 1}")
        if a.max_cost is not None and not 0 < a.max_cost <= MAX_COST_LIMIT:
            errors.append(f"max_cost must be in (0, {MAX_COST_LIMIT}]")
    elif name in ("simulate", "fuel_report"):
        if plans.load_plan(a.plan_id) is None:
            errors.append(f"plan_id {a.plan_id!r} does not exist; call plan_route first")
        if name == "simulate" and a.seed is not None and a.seed < 0:
            errors.append("seed must be >= 0")
    return errors


def _contradictions(cfg, a: PlanRouteArgs) -> list:
    """Well-formed arguments that can never be satisfied: a stop that must be delivered lies on
    an avoided cell or an avoided terrain. Caught up front so no search is wasted on them."""
    found = []
    avoided_cells = {tuple(c) for c in (a.avoid_cells or [])}
    for i, stop in enumerate(cfg.stops):
        stop = tuple(stop)
        terrain = TERRAINS[cfg.grid[stop]]
        if stop in avoided_cells:
            found.append(f"stop {i} is at {list(stop)}, which avoid_cells forbids, so it can never be delivered")
        elif terrain in (a.avoid_terrain or []):
            found.append(f"stop {i} at {list(stop)} is on {terrain}, which avoid_terrain forbids, "
                         f"so it can never be delivered")
    return found


def validate(cfg, name: str, args: dict):
    """Return (clean_args, None) if the call is OK, or (None, error_message) if not."""
    if name not in MODELS:
        return None, f"unknown tool {name!r}; available tools: {sorted(MODELS)}"
    try:
        model = MODELS[name].model_validate(args)
    except ValidationError as err:
        problems = [f"{'.'.join(map(str, e['loc'])) or 'arguments'}: {e['msg']}" for e in err.errors()]
        return None, f"invalid arguments for {name}: " + "; ".join(problems)
    problems = _instance_errors(cfg, name, model)
    if problems:
        return None, f"invalid arguments for {name}: " + "; ".join(problems)
    if name == "plan_route":
        clash = _contradictions(cfg, model)
        if clash:
            # not invalid input (everything exists), but the request contradicts itself
            return None, ("infeasible request (contradiction, nothing was planned): " + "; ".join(clash)
                          + ". If this is what the user asked for, the request is infeasible.")
    return model.model_dump(exclude_none=True), None
