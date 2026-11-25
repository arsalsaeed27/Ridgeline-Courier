"""Turn 2 session 3: weighted A*, memory limits, IDA*, the scenario generator, the default planner."""
import pytest

from oel.config import parse_cli
from oel.experiments.framework import (FEASIBILITY_RESERVE, Variant, candidate_cells, make_scenario,
                                       run_variant)
from oel.experiments.small_instances import small_instances
from oel.search import registry
from oel.search.heuristics import h_ours
from oel.search.informed import astar, ida_star, weighted_astar
from oel.search.uninformed import ucs
from oel.world.constraints import PlanConstraints, verify_plan
from oel.world.problem import DeliveryProblem


@pytest.fixture(scope="module")
def small():
    """20 small instances: 10 with fuel OFF, 10 with fuel ON (tank 15), and their UCS optimum."""
    cfgs = small_instances(10, radius=3) + small_instances(10, radius=3, use_fuel=True)
    return [(cfg, DeliveryProblem(cfg), ucs(DeliveryProblem(cfg)).cost) for cfg in cfgs]


# ---------------------------------------------------------------- weighted A*
@pytest.mark.parametrize("w", [1.2, 1.5, 2.0, 3.0, 5.0])
@pytest.mark.parametrize("prune", [False, True])
def test_weighted_astar_within_w_times_optimal(small, w, prune):
    for cfg, p, optimum in small:
        res = weighted_astar(p, heuristic=h_ours, w=w, prune_dominated=prune)
        assert res.solved
        assert optimum <= res.cost <= w * optimum + 1e-9
        assert verify_plan(res.actions, PlanConstraints(), cfg) == []


def test_weighted_astar_full_map_bound():
    """The full map (reserve 0): every weight stays within w x 329."""
    p = DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))
    for w in (1.2, 2.0, 5.0):
        res = weighted_astar(p, heuristic=h_ours, w=w, prune_dominated=True)
        assert res.solved and 329 <= res.cost <= w * 329


# ---------------------------------------------------------------- IDA*
def test_ida_star_matches_ucs(small):
    for cfg, p, optimum in small:
        res = ida_star(p, heuristic=h_ours)
        assert res.solved, res.stats
        assert res.cost == optimum
        assert verify_plan(res.actions, PlanConstraints(), cfg) == []
        # memory = one path: never more states than the path it holds
        assert res.stats["stored_states"] <= len(res.path) + 1


def test_ida_star_reports_its_budget():
    p = DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))
    res = ida_star(p, heuristic=h_ours, node_limit=200, time_limit=5.0)
    assert not res.solved and res.stats["reason"] == "node_limit" and res.nodes_expanded == 200


# ---------------------------------------------------------------- memory limit
@pytest.mark.parametrize("planner", [astar, ucs])
def test_too_small_max_states_gives_memory_limit(planner):
    p = DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))
    res = planner(p, max_states=500)
    assert not res.solved
    assert res.stats["reason"] == "memory_limit"
    assert 500 < res.stats["stored_states"] <= 500 + 5     # stops right after crossing the cap


def test_large_enough_max_states_changes_nothing(small):
    for cfg, p, optimum in small:
        res = astar(p, heuristic=h_ours, max_states=100_000)
        assert res.solved and res.cost == optimum


# ---------------------------------------------------------------- scenario generator
def test_scenarios_are_deterministic_and_valid():
    base = parse_cli([])
    allowed = set(candidate_cells(base))
    reach = base.reachable_from_start()
    banned = {tuple(base.start)} | set(base.stations) | {c for pair in base.tunnels for c in pair}
    for i in range(3):
        a, b = make_scenario(i, base), make_scenario(i, base)
        assert a.stops == b.stops                        # same seed -> same scenario
        assert len(a.stops) == len(base.stops) == len(set(a.stops))
        for cell in a.stops:
            assert base.is_free(cell) and reach[cell] and cell not in banned and cell in allowed
        # feasible with the default reserve (so it works for reserve 0 and 20)
        p = DeliveryProblem(a, fuel_reserve=FEASIBILITY_RESERVE)
        assert registry.default_planner(p).solved
    assert make_scenario(0, base).stops != make_scenario(1, base).stops


def test_run_variant_row_has_the_metrics():
    row = run_variant(parse_cli(["--fuel-reserve", "0"]), Variant("ref", "astar_pruned", "h_ours"))
    assert row["solved"] and row["cost"] == 329 and row["nodes"] > 0 and row["h_start"] <= 329
    assert row["refuels"] == 2 and row["tunnel_jumps"] == 2


# ---------------------------------------------------------------- the default planner
@pytest.mark.parametrize("flags, optimum", [([], 329), (["--no-hills"], 307)])
def test_default_planner_gives_the_reference_optimum(flags, optimum):
    res = registry.default_planner(DeliveryProblem(parse_cli(flags + ["--fuel-reserve", "0"])))
    assert res.solved and res.cost == optimum


def test_new_planners_are_registered():
    assert {"ida_star", "astar_pruned"} <= set(registry.PLANNERS)
    assert registry.PLANNER_INFO["ida_star"]["uses_heuristic"]
    assert registry.DEFAULT_PLANNER in registry.PLANNERS
    assert registry.DEFAULT_HEURISTIC in registry.HEURISTICS
