"""DeliveryProblem rules (fuel, tunnels, hills, flags) and the reference optimal costs."""
import pytest

from oel.config import parse_cli
from oel.search.uninformed import ucs
from oel.world.problem import TUNNEL, DeliveryProblem

HILLS_OFF_OPTIMUM = 307   # reference from CLAUDE.md (brute-force UCS, hills OFF)
HILLS_ON_OPTIMUM = 329    # UCS with UP_COST=2, UP_FUEL=3, REGEN=1; also in CLAUDE.md
# Both references are TRUE optima, so they are computed with --fuel-reserve 0.


@pytest.fixture(scope="module")
def flat_plan():
    """Optimal plan with hills OFF (about 35 s, so it is computed once for the module)."""
    problem = DeliveryProblem(parse_cli(["--no-hills", "--fuel-reserve", "0"]))
    return problem, ucs(problem)


def _action_into(problem, cell, target):
    """The action that moves from `cell` into `target`."""
    for action in ("N", "S", "E", "W"):
        t = problem.transition(cell, action)
        if t is not None and t[0] == target:
            return action
    raise AssertionError(f"{target} is not next to {cell}")


def _same_terrain_slope(problem):
    """Two adjacent free cells with the same terrain, B one unit higher than A, neither a
    refuel point nor a stop (so only the hill rules make A->B and B->A differ)."""
    grid = problem.cfg.grid
    for (r, c), moves in problem._trans.items():
        for action, (nxt, _cost, _use) in moves.items():
            if action == TUNNEL:
                continue
            ok = (grid[r, c] == grid[nxt]
                  and problem.height(nxt) - problem.height((r, c)) == 1
                  and not problem.is_refuel_point((r, c)) and not problem.is_refuel_point(nxt)
                  and problem.stop_index((r, c)) is None and problem.stop_index(nxt) is None)
            if ok:
                return (r, c), nxt
    raise AssertionError("no slope found")


@pytest.mark.slow
def test_hills_off_optimum_is_307(flat_plan):
    _problem, res = flat_plan
    assert res.solved
    assert res.cost == HILLS_OFF_OPTIMUM


@pytest.mark.slow
def test_fuel_never_negative_along_plan(flat_plan):
    problem, res = flat_plan
    assert problem.is_goal(res.path[-1])
    for state in res.path:
        assert 0 <= state[3] <= problem.capacity


@pytest.mark.slow
def test_hills_on_optimum():
    res = ucs(DeliveryProblem(parse_cli(["--fuel-reserve", "0"])))
    assert res.cost == HILLS_ON_OPTIMUM


def test_station_refuels_to_capacity():
    problem = DeliveryProblem(parse_cli([]))
    station = problem.cfg.stations[0]
    for action in ("N", "S", "E", "W"):   # find a free neighbour of the station
        t = problem.transition(station, action)
        if t is not None:
            neighbour = t[0]
            break
    state = (neighbour[0], neighbour[1], 0, 40)
    after = problem.result(state, _action_into(problem, neighbour, station))
    assert after[:2] == tuple(station)
    assert after[3] == problem.capacity == 98


def test_tunnel_jumps_to_paired_end():
    problem = DeliveryProblem(parse_cli([]))
    for a, b in problem.cfg.tunnels:
        for here, there in ((a, b), (b, a)):
            state = (here[0], here[1], 0, 50)
            assert TUNNEL in problem.actions(state)
            after = problem.result(state, TUNNEL)
            assert after[:2] == tuple(there)
            assert after[3] == 50 - problem.cfg.tunnel_fuel
            assert problem.step_cost(state, TUNNEL, after) == problem.cfg.tunnel_cost


def test_no_tunnels_flag():
    problem = DeliveryProblem(parse_cli(["--no-tunnels"]))
    a = problem.cfg.tunnels[0][0]
    assert TUNNEL not in problem.actions((a[0], a[1], 0, 50))


def test_hills_make_moves_direction_dependent():
    problem = DeliveryProblem(parse_cli([]))
    low, high = _same_terrain_slope(problem)
    up = _action_into(problem, low, high)
    down = _action_into(problem, high, low)
    s_low, s_high = (low[0], low[1], 0, 50), (high[0], high[1], 0, 50)
    cost_up = problem.step_cost(s_low, up, problem.result(s_low, up))
    cost_down = problem.step_cost(s_high, down, problem.result(s_high, down))
    assert cost_up == cost_down + problem.cfg.up_cost   # A->B != B->A


def test_hills_off_is_symmetric():
    problem = DeliveryProblem(parse_cli(["--no-hills"]))
    assert not problem.elevation.any()


def test_up_then_down_loses_fuel():
    """REGEN < UP_FUEL: climbing one level and coming back down never gains fuel."""
    problem = DeliveryProblem(parse_cli([]))
    low, high = _same_terrain_slope(problem)
    start = (low[0], low[1], 0, 50)
    up_state = problem.result(start, _action_into(problem, low, high))
    back = problem.result(up_state, _action_into(problem, high, low))
    assert back[:2] == low
    assert back[3] < start[3]


def test_round_trip_never_gains_fuel_anywhere():
    problem = DeliveryProblem(parse_cli([]))
    for cell, moves in problem._trans.items():
        for action, (nxt, _cost, use) in moves.items():
            if action == TUNNEL:
                continue
            back = _action_into(problem, nxt, cell)
            assert use + problem.transition(nxt, back)[2] > 0


def test_move_that_empties_tank_is_not_offered():
    problem = DeliveryProblem(parse_cli([]))
    for cell, moves in problem._trans.items():
        for action, (nxt, _cost, use) in moves.items():
            if use >= 2 and not problem.is_refuel_point(nxt):
                state = (cell[0], cell[1], 0, use - 1)   # one unit short
                assert action not in problem.actions(state)
                with pytest.raises(ValueError):
                    problem.result(state, action)
                return
    raise AssertionError("no costly move found")


def test_downhill_coasting_with_empty_tank():
    """Net fuel rule: an empty tank can still roll downhill if the regen pays for the move.
    This is the REAL limit, so check it with reserve 0 (a planning reserve forbids it)."""
    problem = DeliveryProblem(parse_cli([])).with_reserve(0)
    for cell, moves in problem._trans.items():
        for action, (_nxt, _cost, use) in moves.items():
            if use <= 0:
                assert action in problem.actions((cell[0], cell[1], 0, 0))
                return
    raise AssertionError("no free downhill move found")


def test_no_fuel_flag_keeps_fuel_constant():
    problem = DeliveryProblem(parse_cli(["--no-fuel"]))
    state = problem.initial_state()
    for _ in range(20):
        state = problem.result(state, problem.actions(state)[0])
        assert state[3] == problem.capacity


def test_stop_delivered_on_entry_and_helpers():
    problem = DeliveryProblem(parse_cli([]))
    stop = problem.stops[3]
    for action in ("N", "S", "E", "W"):
        t = problem.transition(stop, action)
        if t is not None:
            neighbour = t[0]
            break
    after = problem.result((neighbour[0], neighbour[1], 0, 50), _action_into(problem, neighbour, stop))
    assert after[2] == 1 << 3
    assert problem.stop_index(stop) == 3
    assert problem.is_station(problem.cfg.stations[0]) and not problem.is_station(problem.start)
    assert problem.is_refuel_point(problem.start)
    assert "delivered [3]" in problem.describe(after)


# ---------------------------------------------------------------- planning fuel reserve
def test_reserve_blocks_planning_but_not_the_real_world():
    """Reserve 5: a move that would leave 2 fuel is illegal for the PLANNER, legal in the world."""
    problem = DeliveryProblem(parse_cli(["--fuel-reserve", "5"]))
    world = problem.with_reserve(0)
    assert problem.reserve == 5 and world.reserve == 0
    for cell, moves in problem._trans.items():
        for action, (nxt, _cost, use) in moves.items():
            if use >= 1 and not problem.is_refuel_point(nxt):
                state = (cell[0], cell[1], 0, use + 2)   # 2 fuel left after the move
                assert action not in problem.actions(state)
                assert action in world.actions(state)
                return
    raise AssertionError("no fuel-burning move found")


def test_reserve_still_refuels_to_capacity():
    problem = DeliveryProblem(parse_cli(["--fuel-reserve", "5"]))
    station = problem.cfg.stations[0]
    for action in ("N", "S", "E", "W"):
        t = problem.transition(station, action)
        if t is not None:
            neighbour = t[0]
            break
    move = _action_into(problem, neighbour, station)
    use = problem.transition(neighbour, move)[2]
    after = problem.result((neighbour[0], neighbour[1], 0, use + 5), move)
    assert after[3] == problem.capacity
    # arriving with less than the reserve left is not planned, even at a station
    assert move not in problem.actions((neighbour[0], neighbour[1], 0, use + 4))


def test_reserve_ignored_without_fuel_twist():
    assert DeliveryProblem(parse_cli(["--no-fuel", "--fuel-reserve", "10"])).reserve == 0
