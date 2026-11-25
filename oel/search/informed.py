"""Part B: informed (heuristic) search, written from scratch: Greedy best-first, A*, weighted A*,
IDA*.

A heuristic is h(state, problem) -> float, an estimate of the cost still to pay to the goal.
"""
from __future__ import annotations

import heapq
import itertools
import math
import time

from oel.search.common import (FuelDominance, path_cost, reconstruct, record_expansion,
                               solved_result, unsolved_result)
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
def astar(problem, heuristic=h_zero, weight=1.0, is_goal=None, max_nodes=None,
          prune_dominated=False, max_states=None) -> SearchResult:
    """A*: expand the state with the lowest f = g + weight * h (cost so far + estimated cost to
    go). With weight 1 and an admissible h (never overestimates) the first goal popped is the
    cheapest one.

    - max_states: a MEMORY limit. A* keeps every state it has generated (the frontier and the
      already-expanded states, both are keys of best_g). If that number goes above max_states
      it stops with solved=False and reason "memory_limit". stats["stored_states"] reports
      the number of states held (its peak, since A* never forgets a state).

    - Ties in f go to the LARGER g (the state further along its path), which usually reaches the
      goal sooner without changing optimality.
    - If a cheaper path to an already-EXPANDED (closed) state is found, the state is REOPENED,
      i.e. pushed again and later re-expanded. With a consistent h this never happens; our MST
      heuristic may not be consistent, so A* must allow it to stay optimal. Counted in
      stats["reopened"].
    - prune_dominated=True skips a state reached no cheaper and with no more fuel than an earlier
      one at the same (cell, mask) (FuelDominance in common.py explains why that is safe; our
      heuristics ignore fuel, so the two states also have the same h).
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
    stats = {"goal_test": "on pop", "weight": weight, "prune_dominated": prune_dominated}
    dominance = FuelDominance() if prune_dominated else None
    if dominance:
        dominance.add(start, 0.0)
    while frontier:
        _f, neg_g, _, state = heapq.heappop(frontier)
        g = -neg_g
        if g > best_g[state]:
            continue                # stale entry
        if goal_test(state):
            path, actions = reconstruct(parent, state)
            if dominance:
                stats["pruned"] = dominance.pruned
            return solved_result(path, actions, g, expanded, max_frontier, order,
                                 {**stats, "steps": len(actions), "reopened": reopened,
                                  "stored_states": len(best_g)})
        if max_nodes is not None and expanded >= max_nodes:
            return unsolved_result(expanded, max_frontier, order,
                                   {**stats, "reason": "node_limit", "reopened": reopened,
                                    "stored_states": len(best_g)})
        expanded += 1
        closed.add(state)
        record_expansion(order, state)
        for action, nxt, cost in problem.successors(state):
            new_g = g + cost
            if nxt in best_g and new_g >= best_g[nxt]:
                continue            # not a better way to reach nxt
            if dominance:
                if dominance.dominated(nxt, new_g):
                    continue        # an earlier state here is no costlier and has more fuel
                dominance.add(nxt, new_g)
            if nxt in closed:
                reopened += 1       # cheaper path to an expanded state: it will be expanded again
                closed.discard(nxt)
            best_g[nxt] = new_g
            parent[nxt] = (state, action)
            f = new_g + weight * heuristic(nxt, problem)
            heapq.heappush(frontier, (f, -new_g, next(tie), nxt))
        max_frontier = max(max_frontier, len(frontier))
        if max_states is not None and len(best_g) > max_states:
            return unsolved_result(expanded, max_frontier, order,
                                   {**stats, "reason": "memory_limit", "reopened": reopened,
                                    "stored_states": len(best_g)})
    return unsolved_result(expanded, max_frontier, order,
                           {**stats, "reason": "failure", "reopened": reopened,
                            "stored_states": len(best_g)})


def weighted_astar(problem, heuristic=h_zero, w=2.0, max_nodes=None, prune_dominated=False,
                   max_states=None) -> SearchResult:
    """Weighted A*: f = g + w*h with w > 1 trusts the heuristic more, so it expands fewer states
    but may return a costlier path.

    Guarantee (h admissible): cost <= w * optimum. Why, in short: while the optimal path is not
    finished, some state n on it waits in the frontier with g(n) = its optimal g, so
    f(n) = g(n) + w*h(n) <= w*(g(n) + h(n)) <= w * optimum. The goal we return was popped
    before n, so its f, which is just its cost (h = 0 at a goal), is <= f(n) <= w * optimum.
    Reopening and fuel pruning keep this true (a pruned state is replaced by one that is at
    least as cheap with at least as much fuel, at the same cell, so it has the same h)."""
    return astar(problem, heuristic=heuristic, weight=w, max_nodes=max_nodes,
                 prune_dominated=prune_dominated, max_states=max_states)


# ---------------------------------------------------------------- IDA*
class _BudgetHit(Exception):
    """Raised inside the IDA* recursion when the node or time budget runs out."""


def ida_star(problem, heuristic=h_zero, node_limit=500_000, time_limit=30.0,
             max_iterations=10_000) -> SearchResult:
    """IDA* (iterative deepening A*): depth-first search with a limit on f = g + h instead of on
    the depth. Memory like IDS (only the current path), guidance like A*.

    1. bound = h(start).
    2. Depth-first from the start; a child whose f = g + h is above the bound is NOT entered,
       but we remember the smallest such f.
    3. If a goal is reached within the bound: done. Otherwise set bound = that smallest f and
       start again from scratch (step 2).
    With an admissible h the first goal found is optimal: every path cheaper than it has an
    f <= its cost (h never overestimates), so a smaller bound would already have found it.
    Consistency is NOT needed (there is no closed set that could hold a too-expensive copy).

    Like DLS it skips states that are already ON the current path (added when we go down,
    removed when we come back up), so it never walks in a circle. It does NOT remember states
    from other branches or earlier iterations, so it can expand the same state many times:
    that repeated work is the price of storing only one path.
    node_limit / time_limit are TOTAL budgets over all iterations (same meaning as in ids)."""
    start = problem.initial_state()
    t0 = time.perf_counter()
    deadline = t0 + time_limit if time_limit else None
    path, actions, on_path = [start], [], {start}
    order, iterations = [], []
    expanded = 0
    deepest = 1                         # longest path held at once = the memory used

    def search(state, g, bound):
        """Returns ("found", g) or ("over", smallest f above the bound in this subtree)."""
        nonlocal expanded, deepest
        f = g + heuristic(state, problem)
        if f > bound:
            return "over", f
        if problem.is_goal(state):
            return "found", g
        if node_limit is not None and expanded >= node_limit:
            raise _BudgetHit("node_limit")
        if deadline is not None and time.perf_counter() > deadline:
            raise _BudgetHit("time_limit")
        expanded += 1
        record_expansion(order, state)
        next_bound = math.inf
        for action, nxt, cost in problem.successors(state):
            if nxt in on_path:
                continue                    # would close a loop on the current path
            on_path.add(nxt)
            path.append(nxt)
            actions.append(action)
            deepest = max(deepest, len(path))
            outcome, value = search(nxt, g + cost, bound)
            if outcome == "found":
                return "found", value       # keep path/actions: they hold the solution
            next_bound = min(next_bound, value)
            on_path.remove(nxt)             # backtrack
            path.pop()
            actions.pop()
        return "over", next_bound

    bound = heuristic(start, problem)
    stats = {"goal_test": "on visit", "iterations": iterations}
    try:
        for _ in range(max_iterations):
            before = expanded
            outcome, value = search(start, 0.0, bound)
            iterations.append({"bound": bound, "nodes": expanded - before})
            if outcome == "found":
                return solved_result(list(path), list(actions), value, expanded, deepest, order,
                                     {**stats, "steps": len(actions), "stored_states": deepest,
                                      "re_expansions": expanded - iterations[-1]["nodes"]})
            if math.isinf(value):
                break                       # nothing above the bound either: no solution
            bound = value
        else:
            return unsolved_result(expanded, deepest, order,
                                   {**stats, "reason": "max_iterations", "stored_states": deepest})
    except _BudgetHit as hit:
        return unsolved_result(expanded, deepest, order,
                               {**stats, "reason": str(hit), "stored_states": deepest})
    return unsolved_result(expanded, deepest, order,
                           {**stats, "reason": "failure", "stored_states": deepest})
