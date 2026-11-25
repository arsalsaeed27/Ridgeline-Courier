"""Part B search algorithms: correctness on the full map (slow) and on small instances (fast)."""
import pytest

from oel.config import parse_cli
from oel.experiments.small_instances import make_small_instance, small_instances
from oel.llm import plans
from oel.search import registry
from oel.search.heuristics import h_zero
from oel.search.informed import astar, greedy, weighted_astar
from oel.search.result import SearchResult
from oel.search.uninformed import bfs, dls, ids, ucs
from oel.world.constraints import PlanConstraints, verify_plan
from oel.world.problem import DeliveryProblem

BUDGET = dict(node_limit=500_000, time_limit=20.0)


@pytest.fixture(scope="module")
def small():
    """10 small instances (7x7 window around the depot, 1-3 stops) and their problems."""
    return [(cfg, DeliveryProblem(cfg)) for cfg in small_instances(10, radius=3)]


# ---------------------------------------------------------------- full map (slow)
@pytest.mark.slow
@pytest.mark.parametrize("flags, optimum", [(["--no-hills"], 307), ([], 329)])
def test_astar_h_zero_matches_reference(flags, optimum):
    """UCS == A*(h_zero) == reference optimum (UCS itself is checked in test_problem.py)."""
    res = astar(DeliveryProblem(parse_cli(flags + ["--fuel-reserve", "0"])), heuristic=h_zero)
    assert res.solved and res.cost == optimum
    assert res.stats["reopened"] == 0          # h_zero is consistent: nothing is ever reopened


# ---------------------------------------------------------------- small instances (fast)
def test_ucs_equals_astar(small):
    for cfg, p in small:
        u, a = ucs(p), astar(p, heuristic=h_zero)
        assert u.solved and a.solved and u.cost == a.cost


def test_bfs_and_ids_find_the_fewest_moves(small):
    for cfg, p in small:
        b, i = bfs(p), ids(p, max_depth=30, **BUDGET)
        assert i.solved, i.stats
        assert len(b.actions) == len(i.actions) == b.stats["steps"]
        assert i.stats["re_expansions"] >= 0 and len(i.stats["iterations"]) == len(i.actions) + 1


def test_dls_succeeds_at_d_star_and_cuts_off_below(small):
    for cfg, p in small:
        d_star = bfs(p).stats["steps"]
        assert dls(p, limit=d_star, **BUDGET).solved
        below = dls(p, limit=d_star - 1, **BUDGET)
        assert not below.solved and below.stats["reason"] == "cutoff"


def test_dls_reports_failure_when_nothing_exists():
    """A 3x3 window whose only stop lies outside it: every path is explored without ever
    hitting the limit, so the answer is 'failure', not 'cutoff'."""
    cfg = make_small_instance(0, radius=1)
    cfg.stops = [tuple(cfg.stops[0]), (36, 32)]          # (36, 32) is a wall in this window
    res = dls(DeliveryProblem(cfg), limit=50, **BUDGET)
    assert not res.solved and res.stats["reason"] == "failure"


def test_dls_and_ids_respect_their_budgets(small):
    # an instance whose goal is at least 6 moves away cannot be solved in 5 expansions
    p = next(p for cfg, p in small if bfs(p).stats["steps"] >= 6)
    for res in (dls(p, limit=40, node_limit=5, time_limit=None),
                ids(p, max_depth=40, node_limit=5, time_limit=None)):
        assert not res.solved and res.stats["reason"] == "node_limit"
        assert res.nodes_expanded <= 5


def test_greedy_and_weighted_astar_find_valid_plans(small):
    for cfg, p in small:
        optimum = ucs(p).cost
        g = greedy(p, heuristic=h_zero)
        w = weighted_astar(p, heuristic=h_zero, w=2.0)
        assert g.solved and g.cost >= optimum
        assert w.solved and optimum <= w.cost <= 2.0 * optimum


def test_every_plan_passes_verify_plan(small):
    for cfg, p in small:
        d_star = bfs(p).stats["steps"]
        for res in (bfs(p), ucs(p), dls(p, limit=d_star, **BUDGET), ids(p, max_depth=30, **BUDGET),
                    greedy(p, heuristic=h_zero), astar(p, heuristic=h_zero)):
            assert res.solved
            assert verify_plan(res.actions, PlanConstraints(), cfg) == []
            assert res.path[0] == p.initial_state() and p.is_goal(res.path[-1])


# ---------------------------------------------------------------- registry + result fields
def test_all_planners_registered_and_complete(small):
    expected = {"bfs", "ucs", "dls", "ids", "greedy", "astar", "weighted_astar"}
    assert expected <= set(registry.PLANNERS)
    assert {n for n, info in registry.PLANNER_INFO.items() if info["uses_heuristic"]} >= {"greedy", "astar", "weighted_astar"}
    assert "h_zero" in registry.HEURISTICS
    cfg, p = small[0]
    for name in expected:
        kwargs = {"heuristic": h_zero} if registry.PLANNER_INFO[name]["uses_heuristic"] else {}
        res = registry.PLANNERS[name](p, **kwargs)
        assert isinstance(res, SearchResult) and res.solved, name
        assert res.nodes_expanded > 0 and res.max_frontier >= 1 and res.cost > 0
        assert isinstance(res.expanded_order, list) and len(res.expanded_order) > 0
        assert all(len(cell) == 2 for cell in res.expanded_order)
        assert isinstance(res.stats, dict) and "goal_test" in res.stats


def test_cached_plans_still_load():
    """Replacing the stand-in must not change plan ids (CACHE_VERSION was not bumped)."""
    cfg = parse_cli([])
    plan_id = plans.plan_key(cfg, PlanConstraints(), "ucs")
    rec = plans.load_plan(plan_id)
    assert rec is not None and rec["feasible"] and rec["cost"] == 353.0
