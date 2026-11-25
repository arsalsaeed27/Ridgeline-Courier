"""Part C: our evaluation function for the agent-vs-blocker game (designed in Turn 2).

    features(state) -> {name: value}     each value is scaled to about -1..1 (or 0..1)
    evaluate(state, weights) -> float    from OUR agent's point of view: higher = better for us

    evaluate = sum(weight[f] * feature[f])        for a non-terminal state
             = +WIN_VALUE / -WIN_VALUE / 0        for a won / lost / drawn state

The six features (justification: report/sections/part_c_evaluation.md):
  progress      -h_ours(cell, delivered) / h_ours(start): minus the remaining LOWER-BOUND cost
                 (our admissible heuristic: tunnels and hills included, fuel ignored)
  delivered     parcels delivered / number of stops
  interference  -(how close the rival is to the next PATH_LEN cells of our plan; cells we
                 reach sooner count more). -1 = the rival stands on our very next cell
  race          (rival's moves to our target stop - our moves) / RACE_SCALE, clipped to -1..1.
                 Moves, not cost: both robots move one cell per turn whatever the terrain. Our
                 count may use tunnels; the rival's can't (it only moves N/S/E/W)
  mobility      half our legal moves / 4 + half the free cells within 2 steps / 12, the
                 rival's cell not counted (being cornered against a wall or the rival)
  fuel_safety   (fuel - fuel needed to reach the nearest station or the depot) / capacity,
                 clipped to -1..1 (hills and regen included; 1 when the fuel twist is off)
"""
from __future__ import annotations

import math

from oel.game.state import PATH_LEN, GameState, agent_moves, is_terminal
from oel.search.heuristics import h_ours

WIN_VALUE = 1000.0      # far above any non-terminal score (|sum of weights| is about 21)
RACE_SCALE = 20.0       # a 20-move lead (or deficit) in the race counts as the maximum
NEAR = 3                # interference: the rival counts as "near" a path cell within 3 moves
FEATURES = ["progress", "delivered", "interference", "race", "mobility", "fuel_safety"]

# Default weights (the scale of every feature is about 1, so the weights compare directly).
# Ali tunes them in Turn 3 with oel/game/tuning.py.
DEFAULT_WEIGHTS = {
    # the main goal: each delivered parcel is worth 10/5 = 2 points, more than any one-step
    # change of the other features, so the search never gives up a delivery for position
    "delivered": 10.0,
    # the route itself: closing the remaining cost is what wins; scaled so that the whole
    # route is worth 4 points
    "progress": 4.0,
    # running dry was our most common real loss (session 3): a negative fuel margin must
    # outweigh a little progress, so the agent detours to a station in time
    "fuel_safety": 3.0,
    # a blocker on our next cells costs waits and replans; important, but it moves away,
    # so less than the parcels and the fuel
    "interference": 2.0,
    # if the rival reaches our next stop first it can park on it (the placeholder rival does
    # exactly that): worth avoiding, but a margin of a few moves rarely decides the game
    "race": 1.5,
    # a tie-breaker: prefer positions with room to dodge the rival and slips
    "mobility": 0.5,
}


def _clip(x, low=-1.0, high=1.0):
    return float(max(low, min(high, x)))     # plain float (the fields are numpy arrays)


# ---------------------------------------------------------------- the six features
def progress(state: GameState) -> float:
    h = h_ours(state.agent_state, state.ctx.problem)
    if math.isinf(h):
        return -1.5                                  # a stop is unreachable: the worst value
    return _clip(-h / state.ctx.h_start, -1.5, 0.0)


def delivered(state: GameState) -> float:
    return bin(state.delivered_mask).count("1") / len(state.ctx.problem.stops)


def interference(state: GameState) -> float:
    """-max over the next path cells of (how soon we reach it) x (how close the rival is to it).
    Path cell j (0 = the next one) has weight 1 - j / PATH_LEN; the rival's closeness to it is
    1 - distance / (NEAR + 1) (Manhattan), so 1 when the rival stands on it and 0 from 4 cells away."""
    if state.rival is None or not state.path:
        return 0.0
    worst = 0.0
    for j, cell in enumerate(state.path[:PATH_LEN]):
        d = abs(state.rival[0] - cell[0]) + abs(state.rival[1] - cell[1])
        closeness = max(0.0, 1.0 - d / (NEAR + 1))
        worst = max(worst, (1.0 - j / PATH_LEN) * closeness)
    return -worst if worst > 0 else 0.0              # (no "-0.0" when the rival is far away)


def race(state: GameState) -> float:
    """(rival's moves - our moves) to our target stop, scaled. Positive = we get there first."""
    if state.target_stop is None or state.rival is None:
        return 0.0
    ours = state.ctx.agent_steps[state.target_stop][state.agent]
    theirs = state.ctx.rival_steps[state.target_stop][state.rival]
    if math.isinf(ours):
        return -1.0
    if math.isinf(theirs):
        return 1.0
    return _clip((theirs - ours) / RACE_SCALE)


def mobility(state: GameState) -> float:
    """Room to move: legal moves now (fuel and the rival included) and free cells within 2 moves."""
    legal = min(len(agent_moves(state)), 4) / 4
    cfg = state.ctx.problem.cfg
    r, c = state.agent
    free = 0
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if 0 < abs(dr) + abs(dc) <= 2:
                cell = (r + dr, c + dc)
                if cfg.is_free(cell) and cell != state.rival:
                    free += 1
    return 0.5 * legal + 0.5 * free / 12


def fuel_safety(state: GameState) -> float:
    """Fuel left over after reaching the nearest station or the depot, as a share of the tank.
    Negative = we can't reach any refuel point any more (heading for a stranding)."""
    ctx = state.ctx
    if not ctx.problem.cfg.use_fuel:
        return 1.0
    need = ctx.fuel_need[state.agent]
    if math.isinf(need):
        return -1.0
    return _clip((state.fuel - need) / ctx.problem.capacity)


FEATURE_FUNCTIONS = {"progress": progress, "delivered": delivered, "interference": interference,
                     "race": race, "mobility": mobility, "fuel_safety": fuel_safety}


# ---------------------------------------------------------------- the evaluation
def features(state: GameState) -> dict:
    """{feature name: value} for a state (also for terminal states, for inspection)."""
    return {name: fn(state) for name, fn in FEATURE_FUNCTIONS.items()}


def evaluate(state: GameState, weights: dict | None = None) -> float:
    """The score of a state for OUR agent. Terminal states get +-WIN_VALUE (0 for a draw).
    A win reached in fewer steps scores slightly higher, so the search prefers faster wins
    (and slower losses)."""
    weights = DEFAULT_WEIGHTS if weights is None else weights
    done, outcome = is_terminal(state)
    if done:
        if outcome == "win":
            return WIN_VALUE - state.step * 1e-3
        if outcome == "loss":
            return -WIN_VALUE + state.step * 1e-3
        return 0.0
    f = features(state)
    return sum(weights.get(name, 0.0) * value for name, value in f.items())
