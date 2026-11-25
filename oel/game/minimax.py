"""Part C: Minimax for the window game (Turn 3), written from scratch. Alpha-Beta comes next.

    move, value, stats = minimax(game, state, depth)
    move, value, stats = choose_move(state, depth, algorithm="minimax")   # shared entry point

How Minimax works here:
  - MAX (our agent) picks the move with the HIGHEST value, MIN (the rival) the LOWEST.
  - The value of a position is: evaluate() if the game is over there or no depth is left;
    otherwise the max (our turn) or min (rival's turn) of the values after each legal move.
  - So Minimax assumes the rival always answers with the move that is worst for us, and
    picks the move whose worst case is best.
Depth is in PLIES: depth 1 = one move by the player to move, then evaluate.

Determinism: moves are tried in the game's fixed order (N, E, S, W, TUNNEL, WAIT for us;
N, E, S, W, WAIT for the rival) and a move only replaces the best one if it is STRICTLY
better, so the same position always gives the same move and the same node count.

stats: nodes (every position visited, the root included), leaves (positions scored with
evaluate()), terminal_leaves (of which the game was over), max_ply (deepest ply reached),
time_s, and the root moves with their values.
"""
from __future__ import annotations

import math
import time

from oel.game.window import DEFAULT_WIDTH, Game


def minimax(game: Game, state, depth: int):
    """Returns (best move, its value, stats). The root may be our turn (MAX) or the rival's (MIN)."""
    if depth < 1:
        raise ValueError("depth must be at least 1 ply")
    stats = {"nodes": 0, "leaves": 0, "terminal_leaves": 0, "max_ply": 0}

    def value(s, depth_left: int, ply: int) -> float:
        stats["nodes"] += 1
        stats["max_ply"] = max(stats["max_ply"], ply)
        over = game.is_terminal(s)[0]
        if over or depth_left == 0:
            stats["leaves"] += 1
            stats["terminal_leaves"] += over
            return game.evaluate(s)
        if s.to_move == "agent":                       # MAX: the best for us
            best = -math.inf
            for move in game.moves(s):
                best = max(best, value(game.result(s, move), depth_left - 1, ply + 1))
            return best
        best = math.inf                                # MIN: the worst for us
        for move in game.moves(s):
            best = min(best, value(game.result(s, move), depth_left - 1, ply + 1))
        return best

    t0 = time.perf_counter()
    stats["nodes"] += 1                                # the root
    maximising = state.to_move == "agent"
    best_move, best_value = None, -math.inf if maximising else math.inf
    root_values = []
    for move in game.moves(state):
        v = value(game.result(state, move), depth - 1, 1)
        root_values.append((move, v))
        if (maximising and v > best_value) or (not maximising and v < best_value):   # strictly better
            best_move, best_value = move, v
    stats["time_s"] = time.perf_counter() - t0
    stats["root_values"] = root_values
    stats["max_ply"] = max(stats["max_ply"], 1)
    return best_move, best_value, stats


# the shared entry point: Alpha-Beta registers itself here next session
ALGORITHMS = {"minimax": minimax}


def choose_move(state, depth: int, algorithm: str = "minimax", width: int = DEFAULT_WIDTH,
                weights: dict | None = None):
    """Build the window game around `state` and search it. Returns (move, value, stats).
    Both algorithms are called the same way, so they can be compared on identical positions."""
    game = Game(state, width=width, weights=weights)
    move, value, stats = ALGORITHMS[algorithm](game, state, depth)
    stats["algorithm"] = algorithm
    stats["depth"] = depth
    return move, value, stats


def effective_branching_factor(nodes: int, depth: int) -> float:
    """b* such that a full tree of this depth has `nodes` nodes: 1 + b + b^2 + ... + b^depth = nodes
    (solved by bisection). The standard way to compare search effort across depths."""
    if nodes <= depth + 1:
        return 1.0

    def total(b):
        return sum(b ** i for i in range(depth + 1))

    lo, hi = 1.0, float(nodes)
    for _ in range(100):
        mid = (lo + hi) / 2
        if total(mid) < nodes:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
