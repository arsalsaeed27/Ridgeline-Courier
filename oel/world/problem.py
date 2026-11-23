"""DeliveryProblem: the deterministic PLANNING model that every search algorithm uses.

State = (row, col, delivered_mask, fuel), a hashable tuple.
  delivered_mask: bit i is 1 once stop i has been delivered; goal = all 5 bits set.
  Elevation is a property of the cell, so it is NOT part of the state.

This model has no slip and no rival: planners assume the world does exactly what they say.
The Simulator (simulator.py) is the messy "real world"; it executes moves THROUGH this class
(result / transition), so the planning model and the real world use the same rules.
"""
from __future__ import annotations

import copy

import numpy as np

from oel.world.constraints import PlanConstraints
from oel.world.grid import build_cost_map, build_fuel_map

# action name -> (row change, col change). Row 0 is the top of the map, so N = row - 1.
MOVES = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
TUNNEL = "TUNNEL"


# ---------------------------------------------------------------- the fuel rules (one place only)
def move_fuel_use(base_burn: int, dh: int, up_fuel: int, regen: int) -> int:
    """NET fuel used by one normal move (negative = the move gives fuel back).

    Climbing dh > 0 units burns up_fuel per unit on top of the terrain burn (motor works harder).
    Descending recovers regen per unit (regenerative braking). Because regen < up_fuel, going up
    and back down always loses fuel overall, so there is no free-fuel loop.
    """
    climb = max(dh, 0)
    drop = max(-dh, 0)
    return base_burn + up_fuel * climb - regen * drop


def fuel_after(fuel: int, net_use: int, capacity: int, refuels: bool, reserve: int = 0):
    """THE fuel rule, used for every move by both the planner and the simulator.

    Returns the fuel after the move, or None if the move is illegal.
    1. Pay the net use of the move. If that would leave less than `reserve`, the move is
       illegal. The real world uses reserve 0 (the tank can't go negative). The PLANNER uses
       cfg.fuel_reserve > 0 as a safety margin, so a few slips can't strand the agent.
       (We check the NET use, so with an empty tank you can still coast downhill into a road
       cell: burn 1, regen 1, net 0.)
    2. Never above capacity: regen can't overfill the tank.
    3. Entering a charging station or the depot refills to capacity (AFTER paying for the move,
       so you must be able to reach the station first, with the reserve still in the tank).
    """
    left = fuel - net_use
    if left < reserve:
        return None
    if refuels:
        return capacity
    return min(left, capacity)


class DeliveryProblem:
    """Search problem for the delivery agent (see CLAUDE.md, "Shared interfaces")."""

    def __init__(self, config, extra_blocked=(), start_state=None, fuel_reserve=None,
                 constraints=None):
        self.cfg = config
        self.n = config.n
        self.capacity = int(config.fuel_capacity)
        # user constraints (stop order, avoided terrain/cells, tunnels, reserve, cost cap);
        # PlanConstraints() = none = the normal problem
        self.constraints = constraints if constraints is not None else PlanConstraints()
        # planning safety margin: never PLAN to drop below this much fuel (0 = the real limit).
        # Priority: explicit argument > constraint > config default. No fuel twist -> 0.
        if not config.use_fuel:
            self.reserve = 0
        elif fuel_reserve is not None:
            self.reserve = int(fuel_reserve)
        elif self.constraints.fuel_reserve is not None:
            self.reserve = int(self.constraints.fuel_reserve)
        else:
            self.reserve = int(config.fuel_reserve)
        self.start = tuple(config.start)
        self.stops = [tuple(s) for s in config.stops]
        self.goal_mask = (1 << len(self.stops)) - 1
        # cells that are temporarily walls (e.g. the rival's cell when the simulator replans)
        self.extra_blocked = frozenset(extra_blocked)
        # where search starts; None = the depot with a full tank (replans start mid-route)
        self._start_state = start_state

        # Precompute the maps ONCE so actions()/result() are cheap lookups during search.
        self.cost_map = build_cost_map(config.grid, config.terrain_cost)
        self.fuel_map = build_fuel_map(config.grid, config.fuel_burn)
        if config.use_hills:
            self.elevation = np.asarray(config.elevation, dtype=int)
        else:
            # hills OFF = a flat city: every dh is 0, so no climb cost and no regen
            self.elevation = np.zeros(config.grid.shape, dtype=int)

        self._stop_bit = {cell: 1 << i for i, cell in enumerate(self.stops)}
        # stop i only counts as delivered once the stops in _prereq[i] are delivered
        # (all zeros without a stop_order, i.e. deliver anything at any time)
        self._prereq = {cell: need for cell, need in
                        zip(self.stops, self.constraints.prerequisites(len(self.stops)))}
        # cells the constraints turn into walls (avoided terrain / avoided cells)
        self._avoid = frozenset(self.constraints.blocked_cells(config))
        self._stations = set(tuple(s) for s in config.stations)
        self._refuel = set(tuple(s) for s in config.refuel_cells())
        self._tunnel_exit = {}
        if config.use_tunnels and self.constraints.use_tunnels:
            for a, b in config.tunnels:  # tunnels work both ways
                self._tunnel_exit[tuple(a)] = tuple(b)
                self._tunnel_exit[tuple(b)] = tuple(a)

        # _trans[cell][action] = (next_cell, path_cost, net_fuel_use)
        self._trans = self._build_transitions()

    # ------------------------------------------------------------ precomputation
    def _build_transitions(self) -> dict:
        """For every free cell, list the moves that stay on the map and avoid walls.
        Fuel is NOT checked here because it depends on the state; actions() checks it."""
        cfg = self.cfg
        trans = {}
        for r, c in np.argwhere(cfg.grid != -1):
            cell = (int(r), int(c))
            options = {}
            for action, (dr, dc) in MOVES.items():
                nxt = (cell[0] + dr, cell[1] + dc)
                if not cfg.is_free(nxt) or nxt in self._avoid:
                    continue
                dh = int(self.elevation[nxt] - self.elevation[cell])
                # path cost = terrain of the cell ENTERED + extra for climbing (climbing is slower)
                cost = float(self.cost_map[nxt]) + cfg.up_cost * max(dh, 0)
                use = move_fuel_use(int(self.fuel_map[nxt]), dh, cfg.up_fuel, cfg.regen)
                options[action] = (nxt, cost, use if cfg.use_fuel else 0)
            if cell in self._tunnel_exit and self._tunnel_exit[cell] not in self._avoid:
                # a jump ignores elevation: you go through the tunnel, not over the hill
                use = int(cfg.tunnel_fuel) if cfg.use_fuel else 0
                options[TUNNEL] = (self._tunnel_exit[cell], float(cfg.tunnel_cost), use)
            trans[cell] = options
        return trans

    # ------------------------------------------------------------ the shared interface
    def initial_state(self) -> tuple:
        """Depot, nothing delivered, full tank (or the replan start state, if one was given)."""
        if self._start_state is not None:
            return self._start_state
        return (self.start[0], self.start[1], 0, self.capacity)

    def is_goal(self, state) -> bool:
        """All stops delivered. We do NOT have to return to the depot."""
        return state[2] == self.goal_mask

    def actions(self, state) -> list:
        """Legal actions: N/S/E/W into free in-bounds cells, TUNNEL on a tunnel end.
        An action is left out if it enters an extra-blocked cell or would make fuel negative."""
        r, c, _mask, fuel = state
        legal = []
        for action, (nxt, _cost, use) in self._trans[(r, c)].items():
            if nxt in self.extra_blocked:
                continue
            if fuel_after(fuel, use, self.capacity, nxt in self._refuel, self.reserve) is None:
                continue
            legal.append(action)
        return legal

    def result(self, state, action) -> tuple:
        """Deterministic next state. Raises ValueError for an illegal action."""
        r, c, mask, fuel = state
        if action not in self._trans[(r, c)]:
            raise ValueError(f"{action} is not possible from {(r, c)}")
        nxt, _cost, use = self._trans[(r, c)][action]
        new_fuel = fuel_after(fuel, use, self.capacity, nxt in self._refuel, self.reserve)
        if new_fuel is None or nxt in self.extra_blocked:
            raise ValueError(f"{action} from {(r, c)} is illegal (fuel {fuel}, needs {use})")
        # entering a stop delivers its parcel (OR keeps already-set bits set), but only if
        # the stops that must come first are already delivered; otherwise we just drive through
        new_mask = mask
        if nxt in self._stop_bit and mask & self._prereq[nxt] == self._prereq[nxt]:
            new_mask = mask | self._stop_bit[nxt]
        return (nxt[0], nxt[1], new_mask, new_fuel)

    def step_cost(self, state, action, next_state) -> float:
        """Terrain of the entered cell + UP_COST per unit climbed; tunnel_cost for a jump."""
        return self._trans[(state[0], state[1])][action][1]

    # ------------------------------------------------------------ helpers for everyone
    def successors(self, state):
        """Convenience: list of (action, next_state, cost), i.e. actions + result + step_cost
        in one call. Same rules, just fewer function calls in a tight search loop."""
        out = []
        for action in self.actions(state):
            nxt = self.result(state, action)
            out.append((action, nxt, self._trans[(state[0], state[1])][action][1]))
        return out

    def transition(self, cell, action):
        """(next_cell, path_cost, net_fuel_use) of an action from a cell, ignoring the state's
        fuel; None if the action doesn't exist there (wall, edge, not a tunnel end)."""
        return self._trans[tuple(cell)].get(action)

    def replan_from(self, state, extra_blocked=()):
        """Copy of this problem that starts at `state` and treats `extra_blocked` as walls.
        Keeps the same fuel reserve. Shares the precomputed tables, so it's cheap.
        Used by the simulator to replan."""
        clone = copy.copy(self)
        clone._start_state = tuple(state)
        clone.extra_blocked = frozenset(extra_blocked)
        return clone

    def with_reserve(self, reserve: int):
        """Copy of this problem with a different fuel reserve (shares the tables).
        The simulator uses with_reserve(0) as the REAL world's rule."""
        clone = copy.copy(self)
        clone.reserve = int(reserve) if self.cfg.use_fuel else 0
        return clone

    def stop_index(self, cell):
        """Index 0..4 of the stop at `cell`, or None."""
        bit = self._stop_bit.get(tuple(cell))
        return None if bit is None else bit.bit_length() - 1

    def is_station(self, cell) -> bool:
        """True for a charging station (the depot is NOT a station but also refuels)."""
        return tuple(cell) in self._stations

    def is_refuel_point(self, cell) -> bool:
        """True where entering refills the tank: stations and the depot."""
        return tuple(cell) in self._refuel

    def tunnel_exit(self, cell):
        """Other end of the tunnel at `cell`, or None (also None when tunnels are off)."""
        return self._tunnel_exit.get(tuple(cell))

    def height(self, cell) -> int:
        """Height used by the rules (0 everywhere when hills are off)."""
        return int(self.elevation[tuple(cell)])

    def delivered(self, mask) -> list:
        """Stop indices that are delivered in `mask`."""
        return [i for i in range(len(self.stops)) if mask >> i & 1]

    def describe(self, state) -> str:
        r, c, mask, fuel = state
        done = self.delivered(mask)
        return (f"at ({r},{c}) h={self.height((r, c))} | delivered {done} "
                f"({len(done)}/{len(self.stops)}) | fuel {fuel}/{self.capacity}")
