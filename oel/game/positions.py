"""Part C: a fixed, reproducible set of game positions for the Minimax / Alpha-Beta experiments.

    sampled_positions(cfg, n=50)   -> list of GameStates from seeded simulator runs
    HAND_MADE / hand_made_positions(cfg) -> a few positions on our real map with a known answer

SAMPLED: we run the default plan in the simulator (slip, replanning) against the PLACEHOLDER
rival (greedy_blocker, named explicitly, so the set doesn't change when the real Alpha-Beta
blocker replaces it), seeds BASE_SEED + 7000 + k, and record a GameState after every step. A
state qualifies when the rival is INSIDE our 9x9 window (a rival outside it can't move in the
game) and within 4 cells (Manhattan) of our agent or of a cell of our planned path, i.e. when
the blocker can actually matter. At most PER_RUN states per run, at least SPACING steps apart
(so one long standoff doesn't fill the set), then n are drawn with a seeded rng.
The chosen positions are saved in oel/game/positions.json (keyed by the planning config), so
every experiment, this session's and the next (Alpha-Beta), uses exactly the same positions.

HAND-MADE: real states of the default A* route (reserve 20) with the rival put by hand, each
with the move that is right for a reason we can argue WITHOUT running the search (see below).
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

import numpy as np

from oel.config import BASE_SEED
from oel.game.state import GameContext, GameState, _plan_target, from_simulator, make_state
from oel.search.registry import default_planner
from oel.search.uninformed import ucs
from oel.world.problem import DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator, greedy_blocker

POSITIONS_FILE = Path(__file__).resolve().parent / "positions.json"
SEED_OFFSET = 7000
HALF = 4                  # 9x9 window
NEAR = 4                  # "near": Manhattan distance to the agent or a path cell
PER_RUN = 4
SPACING = 15
MAX_RUNS = 60


# ---------------------------------------------------------------- (de)serialising
def to_dict(s: GameState) -> dict:
    return {"agent": list(s.agent), "rival": list(s.rival), "mask": s.delivered_mask, "fuel": s.fuel,
            "step": s.step, "target": s.target_stop, "path": [list(c) for c in s.path]}


def from_dict(ctx: GameContext, d: dict) -> GameState:
    return GameState(tuple(d["agent"]), tuple(d["rival"]), d["mask"], d["fuel"], d["step"], d["target"],
                     tuple(tuple(c) for c in d["path"]), "agent", ctx)


def _key(cfg) -> str:
    from oel.experiments.framework import planning_fingerprint
    blob = {"cfg": planning_fingerprint(cfg), "slip": cfg.slip, "offset": SEED_OFFSET,
            "rules": [HALF, NEAR, PER_RUN, SPACING]}
    return hashlib.sha256(json.dumps(blob, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- sampling
def qualifies(s: GameState) -> bool:
    """The rival is inside our window and near our agent or our planned path."""
    if s.rival is None:
        return False
    dr, dc = abs(s.rival[0] - s.agent[0]), abs(s.rival[1] - s.agent[1])
    if max(dr, dc) > HALF:
        return False
    cells = (s.agent,) + s.path
    return min(abs(s.rival[0] - c[0]) + abs(s.rival[1] - c[1]) for c in cells) <= NEAR


def _candidates_from_run(cfg, seed, actions) -> list:
    problem = DeliveryProblem(cfg)
    recorded = []
    sim = Simulator(cfg, problem, np.random.default_rng(seed), rival_policy=greedy_blocker,
                    on_step=lambda sm: recorded.append(from_simulator(sm)) if not sm.done else None)
    sim.run_plan(actions, RejoinReplanner(default_planner, ucs, cfg.rejoin_radius))
    picked, last = [], -SPACING
    for s in recorded:
        if s.step - last >= SPACING and qualifies(s) and s.target_stop is not None:
            picked.append(s)
            last = s.step
            if len(picked) == PER_RUN:
                break
    return picked


def sampled_positions(cfg, n: int = 50) -> list:
    """n positions (deterministic for a given config). Read from positions.json if they were
    made before for this config, otherwise generated (a few seconds) and saved."""
    ctx = GameContext.for_problem(DeliveryProblem(cfg))
    key = _key(cfg)
    store = json.loads(POSITIONS_FILE.read_text()) if POSITIONS_FILE.exists() else {}
    if key in store and len(store[key]) >= n:
        return [from_dict(ctx, d) for d in store[key][:n]]
    actions = default_planner(DeliveryProblem(cfg)).actions
    pool = []
    for k in range(MAX_RUNS):
        pool += _candidates_from_run(cfg, BASE_SEED + SEED_OFFSET + k, actions)
        if len(pool) >= 2 * n:
            break
    rng = np.random.default_rng(BASE_SEED + SEED_OFFSET)
    chosen = sorted(rng.choice(len(pool), size=min(n, len(pool)), replace=False))
    positions = [pool[i] for i in chosen]
    store[key] = [to_dict(s) for s in positions]
    POSITIONS_FILE.write_text(json.dumps(store, indent=1))
    return [dataclasses.replace(s, ctx=ctx) for s in positions]


# ---------------------------------------------------------------- hand-made positions
# Each one: a real state of the default A* route (index into its states) + a rival cell, and
# the set of moves that are right. Coordinates are (row, col); route = the default plan.
HAND_MADE = [
    {
        "name": "deliver now",
        "route_index": 38, "agent": (3, 10), "rival": (6, 10), "correct": {"S"},
        "why": "We are at (3,10), stop 1 is right below us at (4,10) and free. The rival at (6,10) is "
               "2 moves from the stop, we are 1: stepping onto it now delivers before the blocker "
               "can park there. Any other move or a wait gives the rival the chance to block it.",
    },
    {
        "name": "blocker in a corridor, no way round",
        "route_index": 55, "agent": (12, 14), "rival": (13, 14), "correct": {"WAIT"},
        "why": "We are at (12,14); the route goes south through the one-cell corridor (13,14), where "
               "the rival stands. Inside the window there is no other way to (14,13). Every move "
               "away only adds distance (and costs fuel), and we can't pass, so the right move is "
               "to WAIT for the blocker to move.",
    },
    {
        "name": "blocker on the next cell, equal way round",
        "route_index": 17, "agent": (6, 6), "rival": (7, 6), "correct": {"E"},
        "why": "We are at (6,6); the route goes S to (7,6) and then E to (7,7), and the rival stands "
               "on (7,6). Going E to (6,7) and then S to (7,7) reaches the same route cell in the "
               "same 2 moves, so we lose nothing by going round, while waiting gains nothing "
               "against a blocker that never has to move.",
    },
]


def hand_made_positions(cfg) -> list:
    """[(name, GameState, set of correct moves, why)] on the default route (reserve as in cfg)."""
    problem = DeliveryProblem(cfg)
    ctx = GameContext.for_problem(problem)
    states = default_planner(problem).path
    out = []
    for h in HAND_MADE:
        i = h["route_index"]
        s = states[i]
        if s[:2] != h["agent"]:       # the default route changed: these positions must be re-checked
            raise RuntimeError(f"hand-made position {h['name']!r}: route step {i} is {s[:2]}, "
                               f"expected {h['agent']}")
        state = make_state(ctx, s[:2], h["rival"], delivered_mask=s[2], fuel=s[3],
                           target_stop=_plan_target(states, i, s[2]),
                           path=tuple(x[:2] for x in states[i + 1:i + 9]))
        out.append((h["name"], state, h["correct"], h["why"]))
    return out
