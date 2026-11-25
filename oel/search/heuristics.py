"""Part B heuristics: h(state, problem) -> a LOWER BOUND on the cost still to pay (admissible),
except h_manhattan_raw, our deliberately inadmissible example.

    h_zero           0 (A* = UCS)
    h_manhattan_raw  Manhattan to the nearest undelivered stop x cheapest terrain cost.
                     NOT admissible: a tunnel jump (cost 2) can cross 20+ cells.
    h_manhattan      baseline 1: the same, but tunnel-aware (any number of tunnel hops)
    h_farthest       baseline 2: max over undelivered stops of the relaxed distance D_i(cell)
    h_mst            MST over {current cell} + undelivered stops with relaxed distances
    h_ours           max(h_mst, h_farthest): OUR heuristic (proof: report/sections/part_b_heuristic.md)

None of them looks at fuel, so each is memoised on (cell, delivered mask). The memo lives on the
problem (problem copies made for replanning share it, because they have the same map).
Relaxed distances come from oel/search/distance_fields.py (no fuel limit -> lower bounds).
"""
from __future__ import annotations

import heapq
import math

from oel.search.distance_fields import distance_fields


def h_zero(state, problem) -> float:
    """The trivial heuristic: admissible and consistent, but no information (A* behaves like UCS)."""
    return 0.0


# ---------------------------------------------------------------- shared pieces
def _undelivered(problem, mask) -> list:
    return [i for i in range(len(problem.stops)) if not mask >> i & 1]


def _memo(problem, name: str) -> dict:
    """Per-problem cache {(row, col, mask): h} for one heuristic."""
    store = problem.__dict__.setdefault("_h_memo", {})
    return store.setdefault(name, {})


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def mst_weight(root_to: dict, between) -> float:
    """Prim's algorithm on the complete graph {root} + the stops in root_to.
    root_to[j] = edge weight root -> stop j; between(i, j) = edge weight stop i <-> stop j.
    With at most 6 nodes, a simple O(n^2) Prim is plenty."""
    best = dict(root_to)          # cheapest known edge from the tree to each stop not yet in it
    total = 0.0
    while best:
        j = min(best, key=best.get)
        total += best.pop(j)
        if math.isinf(total):
            return math.inf       # some stop can't be reached at all: dead state
        for k in best:            # stop j joined the tree: its edges may be cheaper
            best[k] = min(best[k], between(j, k))
    return total


# ---------------------------------------------------------------- Manhattan heuristics
def _cheapest_step(problem) -> float:
    return float(min(problem.cfg.terrain_cost.values()))


def h_manhattan_raw(state, problem) -> float:
    """Manhattan distance to the nearest undelivered stop x the cheapest terrain cost.
    Ignores tunnels, so it is NOT admissible on our map: at (5,2), next to the tunnel entrance
    (4,2), with only stop 4 (12,37) left, Manhattan says 42 but the real cost through the
    tunnel (4,2)->(10,36) is 8."""
    r, c, mask, _fuel = state
    left = _undelivered(problem, mask)
    if not left:
        return 0.0
    return min(_manhattan((r, c), problem.stops[i]) for i in left) * _cheapest_step(problem)


def h_manhattan(state, problem) -> float:
    """Baseline 1 (admissible): like h_manhattan_raw, but a route may use tunnels.
    We solve a tiny shortest-path problem over the nodes {cell, every tunnel end, the stops}:
    walking between two nodes costs at least Manhattan x cheapest terrain cost (walls and hills
    can only add), and a tunnel jump costs tunnel_cost. Any number of tunnel hops is allowed,
    because one tunnel can drop you next to another one."""
    r, c, mask, _fuel = state
    memo = _memo(problem, "h_manhattan")
    key = (r, c, mask)
    if key not in memo:
        left = _undelivered(problem, mask)
        if not left:
            memo[key] = 0.0
        else:
            step = _cheapest_step(problem)
            ends = list(problem._tunnel_exit)                 # tunnel ends (empty if tunnels off)
            targets = [problem.stops[i] for i in left]
            nodes = [(r, c)] + ends + targets
            dist = {node: math.inf for node in nodes}
            dist[(r, c)] = 0.0
            heap = [(0.0, (r, c))]
            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u]:
                    continue
                jumps = [(problem._tunnel_exit[u], problem.cfg.tunnel_cost)] if u in problem._tunnel_exit else []
                walks = [(v, _manhattan(u, v) * step) for v in nodes if v != u]
                for v, w in walks + jumps:
                    if d + w < dist[v]:
                        dist[v] = d + w
                        heapq.heappush(heap, (d + w, v))
            memo[key] = min(dist[t] for t in targets)
    return memo[key]


# ---------------------------------------------------------------- distance-field heuristics
def make_field_heuristic(name: str, use_mst: bool = True, use_farthest: bool = True,
                         tunnels: bool = True, hills: bool = True):
    """Build h = max(MST term, farthest term) on relaxed distance fields. The switches exist for
    the ablation; h_ours = make_field_heuristic("h_ours") uses everything."""

    def h(state, problem) -> float:
        r, c, mask, _fuel = state
        memo = _memo(problem, name)
        key = (r, c, mask)
        if key in memo:
            return memo[key]
        left = _undelivered(problem, mask)
        if not left:
            memo[key] = 0.0
            return 0.0
        f = distance_fields(problem, tunnels=tunnels, hills=hills)
        # cost from the CURRENT cell to each undelivered stop (the route starts here: that direction)
        root_to = {j: float(f["to_stop"][j][r, c]) for j in left}
        value = 0.0
        if use_farthest:
            value = max(root_to.values())
        if use_mst:
            S = f["between"]
            # between two stops we don't know the visiting order, so take the cheaper direction
            between = lambda i, j: min(S[i][j], S[j][i])          # noqa: E731
            value = max(value, mst_weight(root_to, between))
        memo[key] = value
        return value

    h.__name__ = name
    return h


h_farthest = make_field_heuristic("h_farthest", use_mst=False)
h_mst = make_field_heuristic("h_mst", use_farthest=False)
h_ours = make_field_heuristic("h_ours")
