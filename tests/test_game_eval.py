"""Turn 2 session 4: the game state and the evaluation function (no Minimax needed)."""
import math

import numpy as np
import pytest

from oel.config import parse_cli
from oel.game.evaluation import DEFAULT_WEIGHTS, FEATURES, WIN_VALUE, evaluate, features
from oel.game.state import (GameContext, after_agent_move, after_rival_move, from_simulator, is_terminal,
                            make_state)
from oel.search.registry import default_planner
from oel.search.uninformed import ucs
from oel.world.problem import DeliveryProblem
from oel.world.simulator import RejoinReplanner, Simulator

FAR = (20, 20)            # a free cell far from the default route's start


@pytest.fixture(scope="module")
def ctx():
    return GameContext.for_problem(DeliveryProblem(parse_cli([])))


def only_left(ctx, stop):
    """A mask where every stop except `stop` is delivered."""
    return ctx.problem.goal_mask & ~(1 << stop)


def free_neighbour(ctx, cell):
    for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nxt = (cell[0] + dr, cell[1] + dc)
        if ctx.problem.cfg.is_free(nxt):
            return nxt
    raise AssertionError("no free neighbour")


# ---------------------------------------------------------------- the state
def test_state_is_hashable_and_ctx_is_not_part_of_identity(ctx):
    a = make_state(ctx, (5, 4), FAR)
    b = make_state(ctx, (5, 4), FAR)
    assert a == b and hash(a) == hash(b) and len({a, b}) == 1
    assert make_state(ctx, (5, 4), (21, 20)) != a


def test_after_moves_do_the_bookkeeping(ctx):
    path = ((5, 5), (5, 6), (5, 7))
    s = make_state(ctx, (5, 4), FAR, path=path)
    nxt = ctx.world.result(s.agent_state, "E")                 # (5, 4) -> (5, 5)
    s2 = after_agent_move(s, nxt)
    assert s2.agent == (5, 5) and s2.step == 1 and s2.to_move == "rival"
    assert s2.path == ((5, 6), (5, 7))                         # the reached cell is dropped
    s3 = after_rival_move(s2, (20, 21))
    assert s3.rival == (20, 21) and s3.to_move == "agent" and s3.step == 1


def test_from_simulator_reads_the_plan():
    cfg = parse_cli([])
    p = DeliveryProblem(cfg)
    plan = default_planner(p)
    seen = []
    sim = Simulator(cfg, p, np.random.default_rng(1), on_step=lambda sm: seen.append(from_simulator(sm)))
    sim.run_plan(plan.actions)                                  # blind mode (no replanning)
    first = seen[0]
    assert first.step == 1 and first.ctx is not None
    # the path is the plan's next cells after the state the plan expects us to be in now
    planned = sim.predict(plan.actions, state=p.initial_state())
    expected = tuple((s[0], s[1]) for s in planned[2:10])
    assert first.path == expected
    assert first.target_stop == 4                               # the plan delivers stop 4 first


def test_is_terminal(ctx):
    assert is_terminal(make_state(ctx, (5, 4), FAR, delivered_mask=ctx.problem.goal_mask)) == (True, "win")
    assert is_terminal(make_state(ctx, (5, 4), FAR)) == (False, "running")
    # stranded: an empty tank on a cell where every move needs fuel
    for cell, options in ctx.problem._trans.items():
        if options and all(use > 0 for _n, _c, use in options.values()) and not ctx.problem.is_refuel_point(cell):
            break
    assert is_terminal(make_state(ctx, cell, FAR, fuel=0)) == (True, "loss")
    assert is_terminal(make_state(ctx, (5, 4), FAR, step=ctx.problem.cfg.max_steps)) == (True, "draw")


def test_fuel_need_field_is_the_exact_fixed_point(ctx):
    """need(u) = min over moves u -> v of max(use + need(v), 0), and 0 at refuel points."""
    need, problem = ctx.fuel_need, ctx.problem
    for cell in problem.cfg.refuel_cells():
        assert need[tuple(cell)] == 0
    for u, options in problem._trans.items():
        if problem.is_refuel_point(u) or math.isinf(need[u]):
            continue
        best = min(max(use + need[v], 0) for v, _c, use in options.values())
        assert need[u] == best


# ---------------------------------------------------------------- each feature moves the right way
def test_closer_to_the_stop_scores_higher(ctx):
    stop = ctx.problem.stops[0]
    mask = only_left(ctx, 0)
    near = make_state(ctx, free_neighbour(ctx, stop), FAR, delivered_mask=mask)
    far = make_state(ctx, (5, 4), FAR, delivered_mask=mask)
    assert features(near)["progress"] > features(far)["progress"]
    assert evaluate(near) > evaluate(far)


def test_rival_on_our_path_scores_lower(ctx):
    path = ((5, 5), (5, 6), (5, 7), (5, 8))
    on_path = make_state(ctx, (5, 4), (5, 6), path=path)
    away = make_state(ctx, (5, 4), FAR, path=path)
    assert features(on_path)["interference"] < features(away)["interference"] == 0
    assert evaluate(on_path) < evaluate(away)
    # the very next cell is the worst place for the rival
    next_cell = make_state(ctx, (5, 4), (5, 5), path=path)
    assert features(next_cell)["interference"] == -1.0


def test_low_fuel_far_from_a_station_scores_lower(ctx):
    # the reachable cell farthest (in fuel) from any refuel point
    cell = max((c for c in ctx.problem._trans if not math.isinf(ctx.fuel_need[c])), key=lambda c: ctx.fuel_need[c])
    low = make_state(ctx, cell, FAR, fuel=5)
    high = make_state(ctx, cell, FAR, fuel=ctx.problem.capacity)
    assert features(low)["fuel_safety"] < 0 < features(high)["fuel_safety"]
    assert evaluate(low) < evaluate(high)


def test_more_delivered_scores_higher(ctx):
    for stop in range(len(ctx.problem.stops)):
        none = make_state(ctx, (20, 20), (30, 30))
        one = make_state(ctx, (20, 20), (30, 30), delivered_mask=1 << stop)
        assert features(one)["delivered"] > features(none)["delivered"]
        assert evaluate(one) > evaluate(none)


def test_rival_winning_the_race_scores_lower(ctx):
    stop = ctx.problem.stops[1]
    at_stop = make_state(ctx, (5, 4), free_neighbour(ctx, stop), target_stop=1)
    far = make_state(ctx, (5, 4), (36, 30), target_stop=1)
    assert features(at_stop)["race"] < features(far)["race"]


def test_rival_next_to_us_reduces_mobility(ctx):
    free = make_state(ctx, (5, 4), FAR)
    boxed = make_state(ctx, (5, 4), free_neighbour(ctx, (5, 4)))
    assert features(boxed)["mobility"] < features(free)["mobility"]


def test_features_are_scaled_and_a_win_beats_everything(ctx):
    cfg = parse_cli([])
    p = DeliveryProblem(cfg)
    states = []
    sim = Simulator(cfg, p, np.random.default_rng(cfg.seed), on_step=lambda sm: states.append(from_simulator(sm)))
    sim.run_plan(default_planner(p).actions, RejoinReplanner(default_planner, ucs, cfg.rejoin_radius))
    for s in states:
        f = features(s)
        assert set(f) == set(FEATURES)
        assert all(-1.5 <= v <= 1.0 for v in f.values())
    win = make_state(ctx, (5, 4), FAR, delivered_mask=ctx.problem.goal_mask, step=599)
    best_possible = sum(abs(w) for w in DEFAULT_WEIGHTS.values()) * 1.5
    assert evaluate(win) > best_possible
    assert evaluate(win) > max(evaluate(s) for s in states if not is_terminal(s)[0])
    assert evaluate(win) > WIN_VALUE - 1
