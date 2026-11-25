"""Part B: uninformed search, written from scratch: BFS, UCS, DLS, IDS.

All planners: planner(problem, **kwargs) -> SearchResult. They only use the DeliveryProblem
interface (initial_state, is_goal, successors = actions + result + step_cost), so constraints,
the fuel reserve and replanning from mid-route all work without extra code.
"""
from __future__ import annotations

import heapq
import itertools
import time
from collections import deque

from oel.search.common import (FuelDominance, path_cost, reconstruct, record_expansion,
                               solved_result, unsolved_result)
from oel.search.result import EXPANDED_ORDER_CAP, SearchResult


# ---------------------------------------------------------------- BFS
def bfs(problem, node_limit=None) -> SearchResult:
    """Breadth-first GRAPH search: expand the OLDEST state first (FIFO queue), never add a state
    twice (visited set). It finds the path with the FEWEST MOVES; because moves cost 1-9 (+climb)
    that is usually NOT the cheapest path, so the cost is reported as it is.

    The goal test is done when a state is GENERATED (not when it is popped): every state at depth
    d is generated before any state at depth d+1, so the first goal generated already has the
    fewest moves, and we save expanding a whole extra layer."""
    start = problem.initial_state()
    stats = {"goal_test": "on generation"}
    if problem.is_goal(start):
        return solved_result([start], [], 0.0, 0, 1, [], {**stats, "steps": 0})
    frontier = deque([start])
    parent = {start: None}      # doubles as the visited set: a state is in it once generated
    expanded, max_frontier, order = 0, 1, []
    while frontier:
        state = frontier.popleft()
        if node_limit is not None and expanded >= node_limit:
            return unsolved_result(expanded, max_frontier, order, {**stats, "reason": "node_limit"})
        expanded += 1
        record_expansion(order, state)
        for action, nxt, _cost in problem.successors(state):
            if nxt in parent:
                continue                     # already seen: BFS reached it at least as early
            parent[nxt] = (state, action)
            if problem.is_goal(nxt):         # early goal test (see docstring)
                path, actions = reconstruct(parent, nxt)
                return solved_result(path, actions, path_cost(problem, path, actions), expanded,
                                     max_frontier, order, {**stats, "steps": len(actions)})
            frontier.append(nxt)
        max_frontier = max(max_frontier, len(frontier))
    return unsolved_result(expanded, max_frontier, order, {**stats, "reason": "failure"})


# ---------------------------------------------------------------- UCS
def ucs(problem, is_goal=None, max_nodes=None, prune_dominated=False, max_states=None) -> SearchResult:
    """Uniform-cost search: expand the state with the LOWEST path cost g first (priority queue).
    It finds the CHEAPEST path (307 hills off / 329 hills on, reserve 0).

    is_goal:   optional goal test (default problem.is_goal); the simulator's "rejoin" uses its own
    max_nodes: optional expansion limit (unsolved result with reason "node_limit")
    prune_dominated: skip states reached no cheaper and with no more fuel than an earlier one
                     at the same (cell, mask); FuelDominance in common.py explains why it is safe
    max_states: optional MEMORY limit on the states held (frontier + expanded = keys of best_g);
                above it: unsolved result with reason "memory_limit"
    """
    goal_test = is_goal if is_goal is not None else problem.is_goal
    start = problem.initial_state()
    tie = itertools.count()             # tie-breaker so the heap never compares two states
    frontier = [(0.0, next(tie), start)]
    best_g = {start: 0.0}               # cheapest cost found so far to each state
    parent = {start: None}
    expanded, max_frontier, order = 0, 1, []
    stats = {"goal_test": "on pop", "prune_dominated": prune_dominated}
    dominance = FuelDominance() if prune_dominated else None
    if dominance:
        dominance.add(start, 0.0)
    while frontier:
        g, _, state = heapq.heappop(frontier)
        if g > best_g[state]:
            continue    # stale entry: a cheaper way to this state was pushed after this one
        # Goal test when POPPING: only then is g guaranteed minimal (every cheaper path was
        # popped before). Testing when pushing could return a more expensive path.
        if goal_test(state):
            path, actions = reconstruct(parent, state)
            if dominance:
                stats["pruned"] = dominance.pruned
            return solved_result(path, actions, g, expanded, max_frontier, order,
                                 {**stats, "steps": len(actions), "stored_states": len(best_g)})
        if max_nodes is not None and expanded >= max_nodes:
            return unsolved_result(expanded, max_frontier, order,
                                   {**stats, "reason": "node_limit", "stored_states": len(best_g)})
        expanded += 1
        record_expansion(order, state)
        for action, nxt, cost in problem.successors(state):
            new_g = g + cost
            if nxt not in best_g or new_g < best_g[nxt]:
                if dominance:
                    if dominance.dominated(nxt, new_g):
                        continue      # an earlier state here is no costlier and has more fuel
                    dominance.add(nxt, new_g)
                best_g[nxt] = new_g
                parent[nxt] = (state, action)
                heapq.heappush(frontier, (new_g, next(tie), nxt))
        max_frontier = max(max_frontier, len(frontier))
        if max_states is not None and len(best_g) > max_states:
            return unsolved_result(expanded, max_frontier, order,
                                   {**stats, "reason": "memory_limit", "stored_states": len(best_g)})
    return unsolved_result(expanded, max_frontier, order,
                           {**stats, "reason": "failure", "stored_states": len(best_g)})


# ---------------------------------------------------------------- DLS
class _LimitHit(Exception):
    """Raised inside the recursion when the node or time budget runs out."""


def dls(problem, limit=50, node_limit=500_000, time_limit=30.0) -> SearchResult:
    """Depth-limited search: depth-first (recursive), but never deeper than `limit` moves.

    Memory: only the CURRENT path is stored. To avoid walking in circles it skips any state that
    is already ON the current path (added when we go down, removed when we come back up). It
    does NOT remember states from other branches, so it can expand the same state many times.

    Returns: solved, or unsolved with stats["reason"]:
      "cutoff"   some branch hit the depth limit, so a deeper solution may exist
      "failure"  everything within reach was explored without hitting the limit: no solution
      "node_limit" / "time_limit"  the budget ran out first
    """
    if limit > 900:
        raise ValueError("limit too deep for Python's recursion (max ~900)")
    start = problem.initial_state()
    deadline = time.perf_counter() + time_limit if time_limit else None
    path, actions, on_path = [start], [], {start}
    order = []
    expanded = 0
    deepest = 1          # longest path held at once = DLS's memory ("max frontier")

    def recurse(state, depth) -> str:
        nonlocal expanded, deepest
        if problem.is_goal(state):
            return "found"
        if depth == limit:
            return "cutoff"
        if node_limit is not None and expanded >= node_limit:
            raise _LimitHit("node_limit")
        if deadline is not None and time.perf_counter() > deadline:
            raise _LimitHit("time_limit")
        expanded += 1
        record_expansion(order, state)
        hit_cutoff = False
        for action, nxt, _cost in problem.successors(state):
            if nxt in on_path:
                continue                      # would close a loop on the current path
            on_path.add(nxt)
            path.append(nxt)
            actions.append(action)
            deepest = max(deepest, len(path))
            outcome = recurse(nxt, depth + 1)
            if outcome == "found":
                return "found"                # keep path/actions: they hold the solution
            if outcome == "cutoff":
                hit_cutoff = True
            on_path.remove(nxt)               # backtrack
            path.pop()
            actions.pop()
        return "cutoff" if hit_cutoff else "failure"

    stats = {"limit": limit, "goal_test": "on visit"}
    try:
        outcome = recurse(start, 0)
    except _LimitHit as hit:
        return unsolved_result(expanded, deepest, order, {**stats, "reason": str(hit)})
    if outcome == "found":
        return solved_result(list(path), list(actions), path_cost(problem, path, actions),
                             expanded, deepest, order, {**stats, "steps": len(actions)})
    return unsolved_result(expanded, deepest, order, {**stats, "reason": outcome})


# ---------------------------------------------------------------- IDS
def ids(problem, max_depth=30, node_limit=500_000, time_limit=30.0) -> SearchResult:
    """Iterative deepening: run DLS with limit 0, 1, 2, ... until it finds a goal. It finds the
    FEWEST MOVES (like BFS) while storing only one path (like DLS). The price is re-doing the
    shallow levels in every iteration; stats["re_expansions"] counts that repeated work
    (all expansions minus those of the final iteration).

    node_limit and time_limit are TOTAL budgets over all iterations."""
    t0 = time.perf_counter()
    iterations = []
    total, deepest, order = 0, 1, []
    for depth in range(max_depth + 1):
        nodes_left = None if node_limit is None else node_limit - total
        time_left = None if time_limit is None else time_limit - (time.perf_counter() - t0)
        if (nodes_left is not None and nodes_left <= 0) or (time_left is not None and time_left <= 0):
            reason = "node_limit" if nodes_left is not None and nodes_left <= 0 else "time_limit"
            break
        res = dls(problem, depth, node_limit=nodes_left, time_limit=time_left)
        iterations.append({"limit": depth, "nodes": res.nodes_expanded})
        total += res.nodes_expanded
        deepest = max(deepest, res.max_frontier)
        order.extend(res.expanded_order[: max(0, EXPANDED_ORDER_CAP - len(order))])
        stats = {"goal_test": "on visit", "iterations": iterations,
                 "re_expansions": total - res.nodes_expanded}
        if res.solved:
            return solved_result(res.path, res.actions, res.cost, total, deepest, order,
                                 {**stats, "steps": len(res.actions), "depth_found": depth})
        if res.stats["reason"] != "cutoff":
            # "failure": nothing deeper exists; or the budget ran out inside this iteration
            return unsolved_result(total, deepest, order, {**stats, "reason": res.stats["reason"]})
    else:
        reason = "max_depth"
    return unsolved_result(total, deepest, order,
                           {"goal_test": "on visit", "iterations": iterations,
                            "re_expansions": total - (iterations[-1]["nodes"] if iterations else 0),
                            "reason": reason})
