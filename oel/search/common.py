"""Small helpers shared by all planners (so each algorithm file shows only its own idea)."""
from __future__ import annotations

from oel.search.result import EXPANDED_ORDER_CAP, SearchResult


def reconstruct(parent: dict, goal) -> tuple:
    """Follow parent links back from the goal. parent[state] = (previous state, action), and
    parent[start] = None. Returns (states start..goal, actions)."""
    path, actions = [goal], []
    state = goal
    while parent[state] is not None:
        previous, action = parent[state]
        path.append(previous)
        actions.append(action)
        state = previous
    path.reverse()
    actions.reverse()
    return path, actions


def path_cost(problem, path, actions) -> float:
    """Total step cost of a path (used by planners that don't track g, e.g. BFS and Greedy)."""
    return sum(problem.step_cost(s, a, n) for s, a, n in zip(path, actions, path[1:]))


def record_expansion(order: list, state) -> None:
    """Remember the CELL of an expanded state, up to the cap (for the UI's search animation)."""
    if len(order) < EXPANDED_ORDER_CAP:
        order.append((state[0], state[1]))


def solved_result(path, actions, cost, expanded, max_frontier, order, stats) -> SearchResult:
    return SearchResult(path, actions, cost, expanded, max_frontier, 0.0, 0.0, True,
                        expanded_order=order, stats=stats)


def unsolved_result(expanded, max_frontier, order, stats) -> SearchResult:
    """No plan. stats["reason"] says why: failure, cutoff, node_limit, time_limit, max_depth."""
    return SearchResult([], [], float("inf"), expanded, max_frontier, 0.0, 0.0, False,
                        expanded_order=order, stats=stats)


class FuelDominance:
    """Optional pruning for UCS / A* (prune_dominated=True).

    For each (cell, mask) we keep the (g, fuel) pairs already reached. A new state is DOMINATED,
    and can be thrown away, if some stored pair has g' <= g AND fuel' >= fuel: it arrived no
    cheaper and with no more fuel.

    Why that is safe in our model (more fuel is never worse):
      - every action legal with less fuel is legal with more (legal = fuel - use >= reserve);
      - after a move, more fuel stays more (or equal): min(fuel - use, capacity) keeps the order;
      - refuelling resets BOTH to capacity, and downhill regen is capped at capacity for both;
      - path costs and deliveries do not depend on fuel at all.
    So whatever the dominated state can still do, the dominating one can do at the same cost,
    and the optimal cost is unchanged (tests: 307 / 329).
    """

    def __init__(self):
        self.front = {}    # (row, col, mask) -> list of (g, fuel), none dominating another
        self.pruned = 0

    def dominated(self, state, g) -> bool:
        for g2, fuel2 in self.front.get(state[:3], ()):
            if g2 <= g and fuel2 >= state[3]:
                self.pruned += 1
                return True
        return False

    def add(self, state, g) -> None:
        key, fuel = state[:3], state[3]
        # drop stored pairs that the new one dominates, then store it
        keep = [(g2, f2) for g2, f2 in self.front.get(key, ()) if not (g <= g2 and fuel >= f2)]
        keep.append((g, fuel))
        self.front[key] = keep
