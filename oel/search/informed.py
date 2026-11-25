"""Part B: informed (heuristic) search, written from scratch: Greedy best-first, A*, weighted A*.

A heuristic is h(state, problem) -> float, an estimate of the cost still to pay to the goal.
"""
from __future__ import annotations

import heapq
import itertools

from oel.search.common import (path_cost, reconstruct, record_expansion, solved_result,
                               unsolved_result)
from oel.search.heuristics import h_zero
from oel.search.result import SearchResult


# ---------------------------------------------------------------- Greedy best-first
def greedy(problem, heuristic=h_zero, node_limit=None) -> SearchResult:
    """Expand the state that LOOKS closest to the goal (lowest h), ignoring the cost paid so far.
    Fast when h is good, but neither optimal nor (on infinite graphs) complete. A visited set
    stops it from adding a state twice. Goal test on pop."""
    start = problem.initial_state()
    tie = itertools.count()
    frontier = [(heuristic(start, problem), next(tie), start)]
    parent = {start: None}          # visited set: a state is added to it when first pushed
    expanded, max_frontier, order = 0, 1, []
    stats = {"goal_test": "on pop"}
    while frontier:
        _h, _, state = heapq.heappop(frontier)
        if problem.is_goal(state):
            path, actions = reconstruct(parent, state)
            return solved_result(path, actions, path_cost(problem, path, actions), expanded,
                                 max_frontier, order, {**stats, "steps": len(actions)})
        if node_limit is not None and expanded >= node_limit:
            return unsolved_result(expanded, max_frontier, order, {**stats, "reason": "node_limit"})
        expanded += 1
        record_expansion(order, state)
        for action, nxt, _cost in problem.successors(state):
            if nxt in parent:
                continue
            parent[nxt] = (state, action)
            heapq.heappush(frontier, (heuristic(nxt, problem), next(tie), nxt))
        max_frontier = max(max_frontier, len(frontier))
    return unsolved_result(expanded, max_frontier, order, {**stats, "reason": "failure"})


# ---------------------------------------------------------------- A* (and weighted A*)
def astar(problem, heuristic=h_zero, weight=1.0, is_goal=None, max_nodes=None) -> SearchResult:
    """A*: expand the state with the lowest f = g + weight * h (cost so far + estimated cost to
    go). With weight 1 and an admissible h (never overestimates) the first goal popped is the
    cheapest one.

    - Ties in f go to the LARGER g (the state further along its path), which usually reaches the
      goal sooner without changing optimality.
    - If a cheaper path to an already-EXPANDED (closed) state is found, the state is REOPENED,
      i.e. pushed again and later re-expanded. With a consistent h this never happens; our MST
      heuristic may not be consistent, so A* must allow it to stay optimal. Counted in
      stats["reopened"].
    """
    goal_test = is_goal if is_goal is not None else problem.is_goal
    start = problem.initial_state()
    tie = itertools.count()
    best_g = {start: 0.0}
    parent = {start: None}
    closed = set()                  # states already expanded (to count reopenings)
    h0 = heuristic(start, problem)
    # heap entries: (f, -g, tie, state): smallest f first; among equal f, largest g first
    frontier = [(weight * h0, -0.0, next(tie), start)]
    expanded, max_frontier, order, reopened = 0, 1, [], 0
    stats = {"goal_test": "on pop", "weight": weight}
    while frontier:
        _f, neg_g, _, state = heapq.heappop(frontier)
        g = -neg_g
        if g > best_g[state]:
            continue                # stale entry
        if goal_test(state):
            path, actions = reconstruct(parent, state)
            return solved_result(path, actions, g, expanded, max_frontier, order,
                                 {**stats, "steps": len(actions), "reopened": reopened})
        if max_nodes is not None and expanded >= max_nodes:
            return unsolved_result(expanded, max_frontier, order,
                                   {**stats, "reason": "node_limit", "reopened": reopened})
        expanded += 1
        closed.add(state)
        record_expansion(order, state)
        for action, nxt, cost in problem.successors(state):
            new_g = g + cost
            if nxt in best_g and new_g >= best_g[nxt]:
                continue            # not a better way to reach nxt
            if nxt in closed:
                reopened += 1       # cheaper path to an expanded state: it will be expanded again
                closed.discard(nxt)
            best_g[nxt] = new_g
            parent[nxt] = (state, action)
            f = new_g + weight * heuristic(nxt, problem)
            heapq.heappush(frontier, (f, -new_g, next(tie), nxt))
        max_frontier = max(max_frontier, len(frontier))
    return unsolved_result(expanded, max_frontier, order,
                           {**stats, "reason": "failure", "reopened": reopened})


def weighted_astar(problem, heuristic=h_zero, w=2.0, max_nodes=None) -> SearchResult:
    """Weighted A*: f = g + w*h with w > 1 trusts the heuristic more, so it expands fewer states
    but may return a costlier path (at most w times the optimum if h is admissible)."""
    return astar(problem, heuristic=heuristic, weight=w, max_nodes=max_nodes)
