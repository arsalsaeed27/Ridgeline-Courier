"""Part B heuristics: h(state, problem) -> float, an estimate of the cost still to pay.

Session 1 only has h_zero (always 0). With h_zero, A* expands exactly like UCS, so
"UCS cost == A*(h_zero) cost" is a test of the A* code itself. Our MST-based, hill-aware
heuristic and the two baselines (h_manhattan_min, h_farthest) come next session.
"""


def h_zero(state, problem) -> float:
    """The trivial heuristic: never overestimates (admissible) and is consistent, but carries no
    information, so A* behaves like UCS and Greedy like a FIFO search."""
    return 0.0
