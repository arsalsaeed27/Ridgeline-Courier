"""SearchResult (what every planner returns) and a helper that times a planner."""
from __future__ import annotations

import dataclasses
import time
import tracemalloc
from dataclasses import dataclass, field

# Planners record at most this many expanded cells in expanded_order (memory: ~15 MB of tuples).
EXPANDED_ORDER_CAP = 200_000


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
    # OPTIONAL: the CELL (row, col) of each expanded state, in expansion order, capped at
    # EXPANDED_ORDER_CAP entries. Used by the UI's search visualisation. None = not recorded.
    expanded_order: list | None = None
    # OPTIONAL planner-specific facts, e.g. {"reason": "cutoff"} for DLS, the per-iteration node
    # counts of IDS, A*'s reopenings, "goal_test": "on generation" / "on pop".
    stats: dict = field(default_factory=dict)


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
