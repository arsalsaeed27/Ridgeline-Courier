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
