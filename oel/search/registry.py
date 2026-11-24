"""Planner and heuristic registries: the ONE place that lists what exists.

The UI (algorithm/heuristic dropdowns), the LLM tools (get_instance_info, validator) and the
plan cache all read these dicts, so a new planner appears everywhere after one line:

    from oel.search.registry import register_planner, register_heuristic
    register_planner("astar", astar, uses_heuristic=True, description="A* search")
    register_heuristic("mst", h_mst, description="MST over undelivered stops (ours)")

Planners: planner(problem, **kwargs) -> SearchResult. A planner registered with
uses_heuristic=True is called as planner(problem, heuristic=h) with h(state, problem) -> float.
"""
from oel.search.standin import ucs

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


# TEMPORARY: Laiba replaces this with her own UCS (oel/search/uninformed.py) in Turn 2.
register_planner("ucs", ucs, description="uniform-cost search (temporary stand-in)")
