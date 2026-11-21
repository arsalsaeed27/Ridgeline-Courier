"""Generate the elevation map for our third twist (hills with regenerative braking).

Usage (from the repo root):  python scripts/make_elevation.py
Reads:  data/instance_38bfda97.json, data/grid_38bfda97.npy, data/twists_38bfda97.json
Writes: data/elevation_38bfda97.npy, results/figures/elevation_map.png

Recipe: add up 4-6 Gaussian "hills" (random centre, height and width), rescale to 0..9 and
round to integers. Deterministic: the rng is seeded from sha256(instance_id + "|elevation").
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # so "import oel" works when run as a script
DATA = ROOT / "data"
INSTANCE_ID = "38bfda97"
MAX_HEIGHT = 9


def make_elevation(n, instance_id=INSTANCE_ID):
    seed = int(hashlib.sha256((instance_id + "|elevation").encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    rows, cols = np.mgrid[0:n, 0:n]          # row index and column index of every cell
    surface = np.zeros((n, n))
    n_hills = int(rng.integers(4, 7))        # 4, 5 or 6 hills
    for _ in range(n_hills):
        cr, cc = rng.uniform(0, n - 1, size=2)          # hill centre
        peak = rng.uniform(0.5, 1.0)                    # relative height
        width = rng.uniform(0.12, 0.25) * n             # spread (std dev) in cells
        dist2 = (rows - cr) ** 2 + (cols - cc) ** 2
        surface += peak * np.exp(-dist2 / (2 * width ** 2))
    # rescale to 0..MAX_HEIGHT, then round to whole height units
    surface = (surface - surface.min()) / (surface.max() - surface.min())
    return np.rint(surface * MAX_HEIGHT).astype(int), n_hills


if __name__ == "__main__":
    grid = np.load(DATA / f"grid_{INSTANCE_ID}.npy")
    inst = json.loads((DATA / f"instance_{INSTANCE_ID}.json").read_text())
    elev, n_hills = make_elevation(grid.shape[0])
    np.save(DATA / f"elevation_{INSTANCE_ID}.npy", elev)
    print(f"Saved data/elevation_{INSTANCE_ID}.npy ({n_hills} hills)")

    free = grid != -1
    print(f"height min {elev.min()}  max {elev.max()}  mean {elev.mean():.2f} "
          f"(free cells mean {elev[free].mean():.2f})")
    print(f"start {tuple(inst['start'])}: h = {elev[tuple(inst['start'])]}")
    for i, s in enumerate(inst["delivery_stops"]):
        print(f"stop {i} {tuple(s)}: h = {elev[tuple(s)]}")

    from oel.config import load_config
    from oel.world.plots import plot_elevation_map
    print("Saved", plot_elevation_map(load_config()).relative_to(ROOT))
