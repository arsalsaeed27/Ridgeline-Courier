"""Distance fields for the heuristics: D_i(cell) = the cheapest cost from `cell` to stop i in a
RELAXED version of the problem: the same walls, terrain costs, uphill costs and tunnels as the
real problem (and the same avoided cells/terrain), but NO fuel limit.

Why it is a lower bound: every real route is also a route in the relaxed problem (fuel can only
force extra detours to stations), so the relaxed cost <= the real cost.

How: hills make moves direction-dependent (A->B != B->A), and we want the cost TO the stop, so we
run our own Dijkstra BACKWARDS from the stop over REVERSED edges: if the real move u -> v costs c,
the reversed edge v -> u costs c, and the backward distance of u is exactly the cost of u -> stop.
The edges are taken from the problem's own move table, so the fields use exactly the moves the
search uses. The rival's cell (extra_blocked, only used while replanning) is NOT a wall here:
fewer walls means smaller distances, so the bound stays valid and one cached field set serves
every replan.

Variants for the ablation: tunnels=False drops tunnel edges, hills=False uses terrain cost only.
"""
from __future__ import annotations

import hashlib
import heapq

import numpy as np

from oel.world.problem import TUNNEL

_CACHE = {}


def _signature(problem, tunnels: bool, hills: bool) -> str:
    """Everything that changes the relaxed graph: map, stops, costs, twists, constraints, variant."""
    cfg, c = problem.cfg, problem.constraints
    parts = [np.ascontiguousarray(cfg.grid).tobytes(), np.ascontiguousarray(problem.elevation).tobytes(),
             repr(problem.stops), repr(sorted(problem._tunnel_exit.items())), repr(sorted(cfg.terrain_cost.items())),
             repr((cfg.up_cost, cfg.tunnel_cost)), repr((c.avoid_cells, c.avoid_terrain, c.use_tunnels)),
             repr((tunnels, hills))]
    h = hashlib.sha256()
    for part in parts:
        h.update(part if isinstance(part, bytes) else part.encode())
    return h.hexdigest()


def _reversed_edges(problem, tunnels: bool, hills: bool) -> dict:
    """reverse[v] = list of (u, cost) for every real move u -> v in the relaxed graph."""
    reverse = {}
    for u, options in problem._trans.items():
        for action, (v, cost, _fuel) in options.items():
            if action == TUNNEL and not tunnels:
                continue
            if action != TUNNEL and not hills:
                cost = float(problem.cost_map[v])        # terrain only, no climbing cost
            reverse.setdefault(v, []).append((u, cost))
    return reverse


def _backward_dijkstra(reverse: dict, target, shape) -> np.ndarray:
    """Cheapest cost from every cell TO `target` (np.inf where the target can't be reached)."""
    dist = np.full(shape, np.inf)
    dist[target] = 0.0
    heap = [(0.0, target)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue                       # stale heap entry
        for u, cost in reverse.get(v, ()):
            nd = d + cost
            if nd < dist[u]:
                dist[u] = nd
                heapq.heappush(heap, (nd, u))
    return dist


def distance_fields(problem, tunnels: bool = True, hills: bool = True) -> dict:
    """{"to_stop": [D_0, D_1, ...] (n x n arrays), "between": S with S[i][j] = D_j(stop_i)}.
    Cached per (map + constraints + variant), so every problem with the same setup shares them."""
    key = _signature(problem, tunnels, hills)
    if key not in _CACHE:
        reverse = _reversed_edges(problem, tunnels, hills)
        shape = problem.cfg.grid.shape
        to_stop = [_backward_dijkstra(reverse, stop, shape) for stop in problem.stops]
        between = [[float(to_stop[j][stop]) for j in range(len(problem.stops))] for stop in problem.stops]
        _CACHE[key] = {"to_stop": to_stop, "between": between}
    return _CACHE[key]
