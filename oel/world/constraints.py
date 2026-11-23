"""PlanConstraints: extra rules a user (or the LLM dispatcher) can put on a plan.

  stop_order     stops that must be delivered in this order BEFORE any others ([3] = stop 3 first).
                 Entering a stop too early does NOT deliver it (you may drive through it).
  avoid_terrain  terrain names treated as walls, e.g. ["mud"]
  avoid_cells    cells treated as walls, e.g. [(12, 20)]
  use_tunnels    False = no TUNNEL jumps
  fuel_reserve   planning fuel margin (None = the config default)
  max_cost       plans costing more are "infeasible under constraints" (checked after planning)

PlanConstraints() (all defaults) = no constraints = exactly the normal problem.
verify_plan() checks a finished plan INDEPENDENTLY: it replays the moves on the plain,
unconstrained map and checks every rule from the visited cells, without reusing the planner's
own delivery logic, so a bug in that logic can't hide itself.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from oel.config import TERRAINS


@dataclass(frozen=True)
class PlanConstraints:
    stop_order: tuple = ()
    avoid_terrain: tuple = ()
    avoid_cells: tuple = ()
    use_tunnels: bool = True
    fuel_reserve: int | None = None
    max_cost: float | None = None

    @classmethod
    def build(cls, stop_order=None, avoid_terrain=None, avoid_cells=None, use_tunnels=None,
              fuel_reserve=None, max_cost=None) -> "PlanConstraints":
        """Make constraints from loose inputs (lists, None = default). No validation here:
        that is the validator's job (oel/llm/validator.py)."""
        return cls(
            stop_order=tuple(int(s) for s in (stop_order or ())),
            avoid_terrain=tuple(sorted(str(t) for t in (avoid_terrain or ()))),
            avoid_cells=tuple(sorted((int(r), int(c)) for r, c in (avoid_cells or ()))),
            use_tunnels=True if use_tunnels is None else bool(use_tunnels),
            fuel_reserve=None if fuel_reserve is None else int(fuel_reserve),
            max_cost=None if max_cost is None else float(max_cost),
        )

    @classmethod
    def from_dict(cls, d: dict) -> "PlanConstraints":
        return cls.build(**d)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["stop_order"] = list(self.stop_order)
        d["avoid_terrain"] = list(self.avoid_terrain)
        d["avoid_cells"] = [list(c) for c in self.avoid_cells]
        return d

    def resolved(self, cfg) -> "PlanConstraints":
        """Same constraints with the defaults filled in from the config (reserve, tunnels flag),
        so two ways of writing the same request compare equal."""
        reserve = cfg.fuel_reserve if self.fuel_reserve is None else self.fuel_reserve
        if not cfg.use_fuel:
            reserve = 0
        return PlanConstraints(self.stop_order, self.avoid_terrain, self.avoid_cells,
                               self.use_tunnels and cfg.use_tunnels, int(reserve), self.max_cost)

    def blocked_cells(self, cfg) -> set:
        """Cells that become walls: the avoided cells plus every cell of an avoided terrain."""
        cells = set(self.avoid_cells)
        codes = [TERRAINS.index(t) for t in self.avoid_terrain]   # ValueError for an unknown name
        for r in range(cfg.n):
            for c in range(cfg.n):
                if cfg.grid[r, c] in codes:
                    cells.add((r, c))
        return cells

    def prerequisites(self, n_stops: int) -> list:
        """need[i] = bitmask of the stops that must already be delivered before stop i counts.
        Stops listed in stop_order need the ones listed before them; every other stop needs
        the whole stop_order list. Unconstrained: all zeros (deliver anything any time)."""
        need = [0] * n_stops
        all_listed = 0
        for pos, stop in enumerate(self.stop_order):
            need[stop] = all_listed          # the stops listed before this one
            all_listed |= 1 << stop
        for i in range(n_stops):
            if i not in self.stop_order:
                need[i] = all_listed
        return need


def verify_plan(actions, constraints: PlanConstraints, cfg) -> list:
    """Replay `actions` from the depot on the PLAIN map (no constraints, real fuel limit 0)
    and return a list of human-readable violations ([] = the plan is fine)."""
    from oel.world.problem import TUNNEL, DeliveryProblem   # local import: avoid a cycle

    c = constraints.resolved(cfg)
    base = DeliveryProblem(cfg, constraints=PlanConstraints(), fuel_reserve=0)
    state = base.initial_state()
    visits = [state[:2]]            # every cell entered, in order (the depot first)
    cost = 0.0
    problems = []
    for step, action in enumerate(actions):
        if action not in base.actions(state):
            return problems + [f"step {step}: {action} is not a legal move from {state[:2]}"]
        nxt_cell, _cost, use = base.transition(state[:2], action)
        if cfg.use_fuel and state[3] - use < c.fuel_reserve:
            problems.append(f"step {step}: fuel {state[3] - use} after the move is below the "
                            f"reserve {c.fuel_reserve}")
        if action == TUNNEL and not c.use_tunnels:
            problems.append(f"step {step}: uses a tunnel but tunnels are not allowed")
        nxt = base.result(state, action)
        cost += base.step_cost(state, action, nxt)
        state = nxt
        visits.append(state[:2])

    entered = visits[1:]            # the depot itself is where we start, not "entered"
    for cell in sorted(set(entered) & set(c.avoid_cells)):
        problems.append(f"enters avoided cell {cell}")
    for t in c.avoid_terrain:
        code = TERRAINS.index(t)
        bad = sorted({cell for cell in entered if cfg.grid[cell] == code})
        if bad:
            problems.append(f"enters {len(bad)} {t} cell(s), e.g. {bad[0]}")

    # Delivery order, checked from the visits only: the ordered stops must be visited one after
    # the other, and every other stop must be visited after the last ordered one. (Driving
    # through a stop earlier is allowed; it just doesn't count.)
    stops = [tuple(s) for s in cfg.stops]
    pos = 0   # index in `visits` where the previous ordered stop was reached
    for stop in c.stop_order:
        later = visits[pos:]
        if stops[stop] not in later:
            problems.append(f"stop {stop} is not delivered in the required order")
            break
        pos = pos + later.index(stops[stop])
    for i, cell in enumerate(stops):
        if i in c.stop_order:
            continue
        if cell not in visits:
            problems.append(f"stop {i} is never visited")
        elif cell not in visits[pos:]:
            problems.append(f"stop {i} is only visited before the ordered stops are delivered")
    if c.max_cost is not None and cost > c.max_cost + 1e-9:
        problems.append(f"cost {cost:.0f} is above max_cost {c.max_cost:.0f}")
    return problems
