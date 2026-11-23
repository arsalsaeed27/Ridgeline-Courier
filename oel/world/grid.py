"""Part A: the grid as NumPy arrays.

Cell codes: -1 blocked, 0 road, 1 grass, 2 mud, 3 ford.
Both maps are built with a lookup table: make a small array where position k holds the value
for code k, then index it with the whole grid at once (NumPy does the loop in C).
Codes start at -1, so we shift by +1: lookup[0] is "blocked", lookup[1] is road, and so on.
"""
import numpy as np

from oel.config import TERRAINS

# TODO(Rayyan): loop version + benchmark (Part A), e.g. build_cost_map_loop() and a timing plot.


def _lookup_map(grid: np.ndarray, value_per_terrain: dict) -> np.ndarray:
    """Return a float array the shape of `grid`; blocked cells get np.inf."""
    lookup = np.empty(len(TERRAINS) + 1, dtype=float)
    lookup[0] = np.inf                          # code -1 (blocked) -> index 0 -> impassable
    for code, terrain in enumerate(TERRAINS):   # road=0, grass=1, mud=2, ford=3
        lookup[code + 1] = value_per_terrain[terrain]
    return lookup[grid + 1]


def build_cost_map(grid: np.ndarray, terrain_costs: dict) -> np.ndarray:
    """Path cost of ENTERING each cell (road 1, grass 3, mud 5, ford 9; blocked inf)."""
    return _lookup_map(grid, terrain_costs)


def build_fuel_map(grid: np.ndarray, fuel_burn: dict) -> np.ndarray:
    """Base fuel burned ENTERING each cell (road 1, grass 1, mud 2, ford 3; blocked inf)."""
    return _lookup_map(grid, fuel_burn)
