"""Small statistics helpers shared by the experiments (Laiba/Ali can reuse them)."""
import math


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple:
    """95% Wilson score interval for a proportion successes/n.

    Better than the simple p +/- 1.96*sqrt(p(1-p)/n) for small n or p near 0 or 1: it never
    goes below 0 or above 1, and it isn't zero-width when p is 0 or 1.
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
