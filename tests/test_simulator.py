"""Simulator: slip, rival, failed moves, reproducibility.
Uses --no-fuel so planning takes under a second (the fuel rules are tested in test_problem.py)."""
import numpy as np
import pytest

from oel.config import parse_cli
from oel.search.uninformed import ucs
from oel.world.problem import TUNNEL, DeliveryProblem
from oel.world.simulator import PERPENDICULAR, RejoinReplanner, Simulator, fuel_needed


@pytest.fixture(scope="module")
def setup():
    cfg = parse_cli(["--no-fuel"])
    problem = DeliveryProblem(cfg)
    return cfg, problem, ucs(problem)


def test_no_slip_follows_plan_exactly(setup):
    cfg, problem, plan = setup
    cfg.slip = 0.0
    try:
        sim = Simulator(cfg, problem, np.random.default_rng(1), use_rival=False)
        report = sim.run_plan(plan.actions)   # blind: no replanning needed
    finally:
        cfg.slip = 0.25
    assert report.outcome == "win"
    assert report.total_cost == plan.cost and report.extra_cost == 0
    assert report.agent_path == [s[:2] for s in plan.path]
    assert report.slips == report.failed_moves == 0


def _run(cfg, problem, plan, seed):
    sim = Simulator(cfg, problem, np.random.default_rng(seed))
    return sim.run_plan(plan.actions, RejoinReplanner(ucs, ucs, cfg.rejoin_radius))


def test_same_seed_same_run(setup):
    cfg, problem, plan = setup
    a, b = _run(cfg, problem, plan, 42), _run(cfg, problem, plan, 42)
    assert (a.outcome, a.total_cost, a.steps, a.slips, a.waits) == (b.outcome, b.total_cost, b.steps, b.slips, b.waits)
    assert a.agent_path == b.agent_path and a.rival_path == b.rival_path
    assert [r["kind"] for r in a.replans] == [r["kind"] for r in b.replans]
    assert a.slips > 0   # slip 0.25 really does something


def test_slip_one_always_slips_except_tunnels(setup):
    cfg, problem, _plan = setup
    cfg.slip = 1.0
    try:
        sim = Simulator(cfg, problem, np.random.default_rng(3), use_rival=False)
        for _ in range(30):
            action = problem.actions(sim.state)[0]
            info = sim.step(action)
            assert info.slipped and info.actual in PERPENDICULAR[action]
        a, _b = cfg.tunnels[0]
        sim.state = (a[0], a[1], sim.state[2], sim.state[3])
        info = sim.step(TUNNEL)
        assert not info.slipped and info.new_state[:2] == tuple(cfg.tunnels[0][1])
    finally:
        cfg.slip = 0.25


def test_failed_move_costs_time_not_fuel():
    cfg = parse_cli(["--slip", "0"])
    problem = DeliveryProblem(cfg)
    sim = Simulator(cfg, problem, np.random.default_rng(0), use_rival=False)
    # find a free cell with a wall or map edge to the north
    for (r, c) in problem._trans:
        if problem.transition((r, c), "N") is None:
            break
    sim.state = (r, c, 0, 40)
    info = sim.step("N")
    assert info.failed and info.new_state == (r, c, 0, 40)
    assert info.cost == cfg.failed_move_cost and info.fuel_used == 0


def test_rival_blocks_and_never_overlaps(setup):
    cfg, problem, plan = setup
    report = _run(cfg, problem, plan, 7)
    assert len(report.rival_path) >= 1
    for agent, rival in zip(report.agent_path, report.rival_path):
        assert agent != rival
    assert all(cfg.is_free(c) for c in report.rival_path)


def test_fuel_needed_never_exceeds_plan_fuel():
    """Rejoin rule: the fuel the rest of a plan needs is <= the fuel the plan had there."""
    # all stops near the depot + a small tank: a quick instance whose plan refuels 3 times
    cfg = parse_cli(["--stop", "0=2,12", "--stop", "2=8,3", "--stop", "3=3,6", "--stop", "4=1,0",
                     "--fuel-capacity", "30", "--fuel-reserve", "0"])
    problem = DeliveryProblem(cfg)
    res = ucs(problem)
    assert res.solved
    need = fuel_needed(problem, res.actions, res.path)
    for k, state in enumerate(res.path):
        assert 0 <= need[k] <= state[3]


def test_simulator_executes_with_real_limit():
    """The planner's reserve is a safety margin; the simulated world only forbids < 0."""
    cfg = parse_cli(["--fuel-reserve", "10"])
    sim = Simulator(cfg, DeliveryProblem(cfg), np.random.default_rng(0), use_rival=False)
    assert sim.problem.reserve == 10 and sim.world.reserve == 0


def test_plan_with_reserve_keeps_margin_and_fuel_needed_fits():
    cfg = parse_cli(["--stop", "0=2,12", "--stop", "2=8,3", "--stop", "3=3,6", "--stop", "4=1,0",
                     "--fuel-capacity", "40", "--fuel-reserve", "5"])
    problem = DeliveryProblem(cfg)
    res = ucs(problem)
    assert res.solved
    assert all(state[3] >= 5 for state in res.path)
    need = fuel_needed(problem, res.actions, res.path, reserve=5)
    assert all(need[k] <= state[3] for k, state in enumerate(res.path))


def test_extra_cost_text():
    from oel.world.simulator import RunReport
    win = RunReport("win", 330, 318, 12, 140, 30, 2, 0)
    loss = RunReport("loss", 266, 318, float("nan"), 112, 33, 5, 0)
    assert win.extra_cost_text() == "+12"
    assert loss.extra_cost_text() == "n/a (stranded)"
