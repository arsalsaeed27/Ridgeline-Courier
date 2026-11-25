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


def mean_ci(values, confidence: float = 0.95) -> tuple:
    """(mean, low, high): a t-based confidence interval for the mean of a sample.
    t (not 1.96) because the sample is small (30) and the spread is estimated from it."""
    from scipy import stats as st

    xs = [float(v) for v in values]
    n = len(xs)
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    mean = sum(xs) / n
    if n == 1:
        return (mean, mean, mean)
    sd = (sum((x - mean) ** 2 for x in xs) / (n - 1)) ** 0.5
    half = st.t.ppf((1 + confidence) / 2, n - 1) * sd / n ** 0.5
    return (mean, mean - half, mean + half)


def bootstrap_mean_ci(values, confidence: float = 0.95, n_resamples: int = 10_000, seed: int = 0) -> tuple:
    """(mean, low, high): a percentile-bootstrap confidence interval for the mean.
    Use it for skewed data such as node counts, where the t interval can even go below 0:
    resample the data with replacement many times, take the mean of each resample, and use the
    middle 95% of those means as the interval. Seeded, so the table is reproducible."""
    import numpy as np

    xs = np.asarray([float(v) for v in values])
    if len(xs) == 0:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = rng.choice(xs, size=(n_resamples, len(xs)), replace=True).mean(axis=1)
    tail = (1 - confidence) / 2 * 100
    return (float(xs.mean()), float(np.percentile(means, tail)), float(np.percentile(means, 100 - tail)))
