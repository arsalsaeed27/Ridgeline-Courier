"""SearchResult (what every planner returns) and a helper that times a planner."""
from __future__ import annotations

import dataclasses
import time
import tracemalloc
from dataclasses import dataclass


@dataclass
class SearchResult:
    path: list            # states, start..goal (empty if failed)
    actions: list
    cost: float
    nodes_expanded: int
    max_frontier: int
    runtime_s: float
    peak_mem_kb: float    # measured with tracemalloc
    solved: bool


def failed_result(nodes_expanded: int = 0, max_frontier: int = 0) -> SearchResult:
    """The result to return when no plan exists (or a node limit was hit)."""
    return SearchResult([], [], float("inf"), nodes_expanded, max_frontier, 0.0, 0.0, False)


def run_timed(planner, problem, measure_memory: bool = True, **kwargs) -> SearchResult:
    """Run planner(problem, **kwargs) and fill in runtime_s and peak_mem_kb.

    tracemalloc records every Python allocation, which makes the code roughly 2-3x slower, so
    pass measure_memory=False when only the time (or just the plan) matters.
    """
    if measure_memory:
        tracemalloc.start()
    t0 = time.perf_counter()
    try:
        res = planner(problem, **kwargs)
    finally:
        runtime = time.perf_counter() - t0
        peak_kb = 0.0
        if measure_memory:
            _current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_kb = peak / 1024
    return dataclasses.replace(res, runtime_s=runtime, peak_mem_kb=peak_kb)
