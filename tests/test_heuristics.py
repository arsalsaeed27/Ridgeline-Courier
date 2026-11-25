"""Part B heuristics: admissibility, the reference optima, pruning, and the documented examples."""
import dataclasses
import math

import numpy as np
import pytest

from oel.config import BASE_SEED, parse_cli
from oel.experiments.heuristic_eval import _random_walk_states
from oel.experiments.small_instances import small_instances
from oel.search.distance_fields import distance_fields
from oel.search.heuristics import h_farthest, h_manhattan, h_manhattan_raw, h_mst, h_ours, h_zero
from oel.search.informed import astar
from oel.search.uninformed import ucs
from oel.world.constraints import PlanConstraints
from oel.world.problem import DeliveryProblem

ADMISSIBLE = {"h_zero": h_zero, "h_manhattan": h_manhattan, "h_farthest": h_farthest,
              "h_mst": h_mst, "h_ours": h_ours}


@pytest.fixture(scope="module")
def full():
    return DeliveryProblem(parse_cli(["--fuel-reserve", "0"]))


# ---------------------------------------------------------------- admissibility on small instances
@pytest.mark.parametrize("fuel", [False, True])
def test_admissible_heuristics_never_overestimate(fuel):
    rng = np.random.default_rng(BASE_SEED + 7)
    for cfg in small_instances(12, radius=3, use_fuel=fuel):
        p = DeliveryProblem(cfg)
        for s in _random_walk_states(p, rng, 6, 12):
            h_star = ucs(p.replan_from(s)).cost           # true cost-to-go
            for name, h in ADMISSIBLE.items():
                assert h(s, p) <= h_star + 1e-9, (name, s, h(s, p), h_star)


def test_heuristics_are_zero_at_the_goal(full):
    goal = (full.stops[0][0], full.stops[0][1], full.goal_mask, 50)
    for h in list(ADMISSIBLE.values()) + [h_manhattan_raw]:
        assert h(goal, full) == 0.0


def test_h_ours_is_the_max_of_its_parts(full):
    rng = np.random.default_rng(BASE_SEED + 8)
    for s in _random_walk_states(full, rng, 20, 40):
        assert h_ours(s, full) == max(h_mst(s, full), h_farthest(s, full))
        assert h_manhattan(s, full) <= h_manhattan_raw(s, full) + 1e-9   # tunnels can only help


def test_manhattan_raw_overestimates_next_to_a_tunnel(full):
    """WHY h_manhattan_raw is not admissible: at (5,2), next to the tunnel entrance (4,2), with only
    stop 4 (12,37) left, Manhattan says 7 + 35 = 42, but the real route goes (5,2) -> (4,2), jumps
    to (10,36) for cost 2 and walks to the stop: 8 in total. The tunnel-aware baseline and h_ours
    stay below the true cost."""
    mask = full.goal_mask & ~(1 << 4)
    s = (5, 2, mask, full.capacity)
    true_cost = ucs(full.replan_from(s), prune_dominated=True).cost
    assert h_manhattan_raw(s, full) == 42 and true_cost == 8
    assert h_manhattan_raw(s, full) > true_cost
    assert h_manhattan(s, full) <= true_cost and h_ours(s, full) <= true_cost


def test_distance_fields_match_independent_ucs(full):
    """D_i(cell) must equal the cheapest no-fuel route cost from that cell to stop i."""
    f = distance_fields(full)
    no_fuel = DeliveryProblem(dataclasses.replace(full.cfg, use_fuel=False), constraints=PlanConstraints())
    for i, stop in enumerate(full.stops):
        assert f["to_stop"][i][stop] == 0.0
    for cell, i in [((5, 4), 4), ((5, 4), 0), ((30, 20), 1), ((17, 14), 2)]:
        start = (cell[0], cell[1], 0, no_fuel.capacity)
        res = ucs(no_fuel.replan_from(start), is_goal=lambda s, t=full.stops[i]: s[:2] == t)
        assert math.isclose(f["to_stop"][i][cell], res.cost), (cell, i)


# ---------------------------------------------------------------- pruning on small instances (fast)
def test_fuel_pruning_keeps_costs_optimal_on_small_instances():
    for cfg in small_instances(15, radius=3, use_fuel=True):
        p = DeliveryProblem(cfg)
        optimum = ucs(p).cost
        assert ucs(p, prune_dominated=True).cost == optimum
        pruned = astar(p, heuristic=h_ours, prune_dominated=True)
        assert pruned.cost == optimum and "pruned" in pruned.stats


# ---------------------------------------------------------------- full map (slow)
@pytest.mark.slow
@pytest.mark.parametrize("flags, optimum", [(["--no-hills"], 307), ([], 329)])
def test_astar_h_ours_and_pruning_match_reference(flags, optimum):
    cfg = parse_cli(flags + ["--fuel-reserve", "0"])
    a = astar(DeliveryProblem(cfg), heuristic=h_ours)
    assert a.cost == optimum and a.nodes_expanded < 200_000     # far fewer than UCS's ~1.8M
    assert ucs(DeliveryProblem(cfg), prune_dominated=True).cost == optimum
    assert astar(DeliveryProblem(cfg), heuristic=h_ours, prune_dominated=True).cost == optimum
