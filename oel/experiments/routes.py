"""Plain facts about a planned route, used to DESCRIBE routes in tables and report text:
delivery order, refuels, tunnel jumps, mud/ford cells, height climbed, and where two routes differ.
"""
from __future__ import annotations

from oel.world.problem import TUNNEL

TERRAIN_NAMES = {0: "road", 1: "grass", 2: "mud", 3: "ford"}


def route_facts(problem, path, actions) -> dict:
    """path: states start..goal, actions: the moves between them."""
    order, refuels, climbed = [], [], 0
    terrain = {name: 0 for name in TERRAIN_NAMES.values()}
    for state, action, nxt in zip(path, actions, path[1:]):
        new_bits = nxt[2] & ~state[2]
        if new_bits:
            order.append(new_bits.bit_length() - 1)
        cell = (nxt[0], nxt[1])
        if problem.is_refuel_point(cell) and nxt[3] > state[3]:
            refuels.append(cell)
        if action != TUNNEL:
            terrain[TERRAIN_NAMES[int(problem.cfg.grid[cell])]] += 1
            climbed += max(problem.height(cell) - problem.height(state[:2]), 0)
    return {"delivery_order": order, "refuels": len(refuels), "refuel_cells": refuels,
            "tunnel_jumps": actions.count(TUNNEL), "moves": len(actions),
            "mud_cells": terrain["mud"], "ford_cells": terrain["ford"], "grass_cells": terrain["grass"],
            "height_climbed": climbed, "min_fuel": min(s[3] for s in path) if path else None}


def cells_of(path) -> list:
    return [(s[0], s[1]) for s in path]


def differing_segments(route, other) -> list:
    """Maximal runs of consecutive cells of `route` that never appear on `other`.
    Returns a list of segments (each a list of cells), longest first."""
    elsewhere = set(other)
    segments, current = [], []
    for cell in route:
        if cell in elsewhere:
            if current:
                segments.append(current)
            current = []
        else:
            current.append(cell)
    if current:
        segments.append(current)
    return sorted(segments, key=len, reverse=True)
