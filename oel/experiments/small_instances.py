"""Small, seeded benchmark problems on which ALL six search algorithms can finish.

How: MASKING. We keep the real 40x40 map but turn every cell outside a square window around
the depot into a wall, then put 1-3 delivery stops on random reachable cells inside the window.
Why masking and not cropping: the terrain, heights and coordinates stay exactly those of our
instance, so DeliveryProblem, verify_plan, the plots and the UI all work unchanged; cropping
would renumber every cell.

Twists are configurable. Stations and tunnels outside the window disappear with it (the depot
still recharges). With fuel ON the tank is shrunk (default 15) so fuel can still matter in such
a small area, and the planning reserve is 0. Seeds come from BASE_SEED (+ 1000 + i).
"""
from __future__ import annotations

import dataclasses

import numpy as np

from oel.config import BASE_SEED, load_config

SEED_OFFSET = 1000


def masked_window(cfg, radius: int):
    """A copy of the grid where every cell more than `radius` rows/cols from the depot is a wall."""
    grid = np.array(cfg.grid, copy=True)
    sr, sc = cfg.start
    rows, cols = np.indices(grid.shape)
    outside = (np.abs(rows - sr) > radius) | (np.abs(cols - sc) > radius)
    grid[outside] = -1
    return grid


def make_small_instance(index: int, radius: int = 3, n_stops=(1, 3), use_fuel: bool = False,
                        use_hills: bool = True, use_tunnels: bool = True, capacity: int = 15,
                        base_cfg=None):
    """Instance number `index` (seed BASE_SEED + 1000 + index): a Config for a small problem."""
    base = base_cfg if base_cfg is not None else load_config()
    rng = np.random.default_rng(BASE_SEED + SEED_OFFSET + index)
    grid = masked_window(base, radius)
    small = dataclasses.replace(base, grid=grid, use_fuel=use_fuel, use_hills=use_hills,
                                use_tunnels=use_tunnels, fuel_reserve=0, overrides=[])
    inside = lambda cell: grid[tuple(cell)] != -1                 # noqa: E731
    small.stations = [tuple(s) for s in base.stations if inside(s)]
    small.tunnels = [(tuple(a), tuple(b)) for a, b in base.tunnels if inside(a) and inside(b)]
    if use_fuel:
        small.fuel_capacity = capacity
    # stops: distinct reachable free cells in the window (not the depot). With a small fuel tank
    # some draws are infeasible, so redraw (same seeded rng) until a plan exists.
    from oel.search.uninformed import bfs           # local import: avoids a cycle at load time
    from oel.world.problem import DeliveryProblem

    reach = small.reachable_from_start()
    cells = [tuple(map(int, p)) for p in np.argwhere(reach) if tuple(p) != tuple(base.start)]
    for _attempt in range(100):
        k = int(rng.integers(n_stops[0], n_stops[1] + 1))
        picks = rng.choice(len(cells), size=k, replace=False)
        small.stops = [cells[i] for i in picks]
        if bfs(DeliveryProblem(small)).solved:
            break
    else:
        raise RuntimeError(f"no feasible small instance for index {index}")
    small.instance_id = f"{base.instance_id}-small{index}"
    return small


def small_instances(n: int = 30, **kwargs) -> list:
    base = load_config()
    return [make_small_instance(i, base_cfg=base, **kwargs) for i in range(n)]
