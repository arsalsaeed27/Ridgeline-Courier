"""Temporary stand-in so the pipeline runs end to end. Laiba replaces this in Turn 2 with
oel/search/uninformed.py; delete this file then.

Plain uniform-cost search (UCS) on a DeliveryProblem.
"""
from __future__ import annotations

import dataclasses
import heapq
import itertools

from oel.search.result import EXPANDED_ORDER_CAP, SearchResult, failed_result


def ucs(problem, is_goal=None, max_nodes=None) -> SearchResult:
    """Cheapest path from problem.initial_state() to a goal.

    is_goal:   optional goal test (default problem.is_goal); the simulator's "rejoin" replan
               uses its own goal ("back on the plan").
    max_nodes: optional expansion limit; returns an unsolved result if it is reached.
    """
    goal_test = is_goal if is_goal is not None else problem.is_goal
    start = problem.initial_state()
    tie = itertools.count()   # tie-breaker so the heap never has to compare two states
    frontier = [(0.0, next(tie), start)]
    best = {start: (0.0, None, None)}   # state -> (cheapest cost found, parent state, action)
    expanded = 0
    max_frontier = 1
    order = []   # cell of each expanded state (for the UI's search animation), capped

    while frontier:
        g, _, state = heapq.heappop(frontier)
        if g > best[state][0]:
            continue   # stale entry: a cheaper way to this state was found after it was pushed
        # Goal test when POPPING (not when pushing): only then is g guaranteed to be the
        # cheapest cost, because every cheaper path would have been popped first.
        if goal_test(state):
            return dataclasses.replace(_build(best, state, g, expanded, max_frontier),
                                       expanded_order=order)
        if max_nodes is not None and expanded >= max_nodes:
            break
        expanded += 1
        if len(order) < EXPANDED_ORDER_CAP:
            order.append((state[0], state[1]))
        for action, nxt, cost in problem.successors(state):
            new_g = g + cost
            if nxt not in best or new_g < best[nxt][0]:
                best[nxt] = (new_g, state, action)
                heapq.heappush(frontier, (new_g, next(tie), nxt))
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)

    return dataclasses.replace(failed_result(expanded, max_frontier), expanded_order=order)


def _build(best, goal, cost, expanded, max_frontier) -> SearchResult:
    """Walk parent links back from the goal to get the states and actions."""
    path, actions = [goal], []
    state = goal
    while best[state][1] is not None:
        _g, parent, action = best[state]
        actions.append(action)
        path.append(parent)
        state = parent
    path.reverse()
    actions.reverse()
    return SearchResult(path, actions, cost, expanded, max_frontier, 0.0, 0.0, True)
