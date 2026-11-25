"""Planner and heuristic registries: the ONE place that lists what exists.

The UI (algorithm/heuristic dropdowns), the LLM tools (get_instance_info, validator) and the
plan cache all read these dicts, so a new planner appears everywhere after one line:

    from oel.search.registry import register_planner, register_heuristic
    register_planner("astar", astar, uses_heuristic=True, description="A* search")
    register_heuristic("mst", h_mst, description="MST over undelivered stops (ours)")

Planners: planner(problem, **kwargs) -> SearchResult. A planner registered with
uses_heuristic=True is called as planner(problem, heuristic=h) with h(state, problem) -> float.
"""
from oel.search.heuristics import (h_farthest, h_manhattan, h_manhattan_raw, h_mst, h_ours,
                                   h_zero)
from oel.search.informed import astar, greedy, ida_star, weighted_astar
from oel.search.uninformed import bfs, dls, ids, ucs

PLANNERS = {}       # name -> planner function
PLANNER_INFO = {}   # name -> {"uses_heuristic": bool, "description": str}
HEURISTICS = {}     # name -> h(state, problem)
HEURISTIC_INFO = {}  # name -> {"description": str}


def register_planner(name: str, planner, uses_heuristic: bool = False, description: str = "") -> None:
    PLANNERS[name] = planner
    PLANNER_INFO[name] = {"uses_heuristic": uses_heuristic, "description": description}


def register_heuristic(name: str, heuristic, description: str = "") -> None:
    HEURISTICS[name] = heuristic
    HEURISTIC_INFO[name] = {"description": description}


# ---------------------------------------------------------------- Part B planners (Turn 2)
register_planner("bfs", bfs, description="breadth-first search: fewest moves, not cheapest")
register_planner("ucs", ucs, description="uniform-cost search: cheapest path")
register_planner("dls", dls, description="depth-limited search (limit 50, node/time budget)")
register_planner("ids", ids, description="iterative deepening (max depth 30, node/time budget)")
register_planner("greedy", greedy, uses_heuristic=True, description="greedy best-first on h")
register_planner("astar", astar, uses_heuristic=True, description="A*: f = g + h")
register_planner("weighted_astar", weighted_astar, uses_heuristic=True,
                 description="weighted A*: f = g + 2h (faster, may cost more)")


def astar_pruned(problem, heuristic=h_ours, **kwargs):
    """A* with fuel-dominance pruning (optimal, ~10x fewer nodes than plain A* on our map)."""
    return astar(problem, heuristic=heuristic, prune_dominated=True, **kwargs)


register_planner("astar_pruned", astar_pruned, uses_heuristic=True,
                 description="A* + fuel-dominance pruning (optimal, fastest; the default)")
register_planner("ida_star", ida_star, uses_heuristic=True,
                 description="IDA*: iterative deepening on f = g + h (tiny memory, node/time budget)")

# THE default planner (simulator full replans, run_all demo, fuel-reserve experiment, UI):
# A* + h_ours + fuel pruning. Session 2: 2,752 nodes on the full map vs UCS 1,775,457, same cost.
DEFAULT_PLANNER = "astar_pruned"
DEFAULT_HEURISTIC = "h_ours"
DEFAULT_LABEL = "A* + h_ours + fuel pruning"


def default_planner(problem, **kwargs):
    """Plan with the default planner. planner(problem, **kwargs) -> SearchResult like any other."""
    return astar_pruned(problem, heuristic=h_ours, **kwargs)


register_heuristic("h_zero", h_zero, description="always 0 (A* = UCS)")
register_heuristic("h_ours", h_ours, description="OURS: max(MST over relaxed distances, farthest stop)")
register_heuristic("h_mst", h_mst, description="MST over {cell} + undelivered stops (relaxed distances)")
register_heuristic("h_farthest", h_farthest, description="baseline 2: relaxed distance to the farthest stop")
register_heuristic("h_manhattan", h_manhattan, description="baseline 1: tunnel-aware Manhattan, nearest stop")
register_heuristic("h_manhattan_raw", h_manhattan_raw, description="NOT admissible: Manhattan ignoring tunnels")
