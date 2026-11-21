"""Generate the layout for our two assigned twists (fuel + teleport tunnels).

Usage (from the repo root):  python scripts/make_twists.py
Reads:  data/instance_38bfda97.json, data/grid_38bfda97.npy
Writes: data/twists_38bfda97.json

Deterministic: seeded from the instance_id, so anyone can regenerate the exact same layout.
"""
import hashlib, heapq, json
from pathlib import Path
import numpy as np

INSTANCE_ID = "38bfda97"
DATA = Path(__file__).resolve().parent.parent / "data"

TWIST_CFG = {
    "n_stations": 4,            # charging stations (the start/depot also recharges)
    "n_tunnel_pairs": 3,        # two-way teleport tunnels
    "tunnel_cost": 2,           # path cost of a tunnel jump
    "tunnel_fuel": 1,           # fuel burned by a tunnel jump
    "min_tunnel_span": 18,      # min Manhattan distance between the two tunnel ends
    "fuel_burn": {"road": 1, "grass": 1, "mud": 2, "ford": 3},  # fuel per move INTO that terrain
    "capacity_factor": 0.55,    # capacity = 0.55 x fuel of a no-refuel tour, so recharging is forced
}
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _reachable_cells(grid, start):
    n = grid.shape[0]; seen = np.zeros_like(grid, bool); seen[start] = True; q = [start]
    while q:
        r, c = q.pop()
        for dr, dc in MOVES:
            a, b = r + dr, c + dc
            if 0 <= a < n and 0 <= b < n and grid[a, b] >= 0 and not seen[a, b]:
                seen[a, b] = True; q.append((a, b))
    return seen


def _farthest_point_sample(cands, k, rng, avoid):
    """Spread points out: first one random, then each next one is the cell
    farthest from everything already chosen or avoided."""
    cands = np.asarray(cands)
    chosen = [cands[rng.integers(len(cands))]]
    for _ in range(k - 1):
        ref = np.array(chosen + list(avoid))
        d = np.abs(cands[:, None, :] - ref[None, :, :]).sum(-1).min(1)
        chosen.append(cands[int(np.argmax(d))])
    return [tuple(map(int, p)) for p in chosen]


def _dijkstra(grid, src, weight):
    # only used here to size the fuel capacity, NOT one of our graded planners
    n = grid.shape[0]; D = np.full(grid.shape, np.inf); D[src] = 0; pq = [(0, src)]
    while pq:
        d, (r, c) = heapq.heappop(pq)
        if d > D[r, c]: continue
        for dr, dc in MOVES:
            a, b = r + dr, c + dc
            if 0 <= a < n and 0 <= b < n and grid[a, b] >= 0:
                nd = d + weight[grid[a, b]]
                if nd < D[a, b]: D[a, b] = nd; heapq.heappush(pq, (nd, (a, b)))
    return D


def make_twists(inst, grid, cfg=TWIST_CFG):
    seed = int(hashlib.sha256((inst["instance_id"] + "|twists").encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    start = tuple(inst["start"]); stops = [tuple(s) for s in inst["delivery_stops"]]
    reach = _reachable_cells(grid, start)
    taken = {start, *stops}

    # charging stations: reachable ROAD cells, spread out, away from the start and stops
    road = [tuple(p) for p in np.argwhere(reach & (grid == 0)) if tuple(p) not in taken]
    stations = _farthest_point_sample(road, cfg["n_stations"], rng, avoid=[start, *stops])
    taken |= set(stations)

    # tunnel pairs: reachable free cells, far apart, no overlap with anything else
    free = [tuple(map(int, p)) for p in np.argwhere(reach) if tuple(p) not in taken]
    tunnels = []
    while len(tunnels) < cfg["n_tunnel_pairs"]:
        a, b = (free[i] for i in rng.choice(len(free), 2, replace=False))
        if a in taken or b in taken: continue
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) < cfg["min_tunnel_span"]: continue
        tunnels.append([list(a), list(b)]); taken |= {a, b}

    # fuel capacity: small enough to force recharging, big enough that every stop can be
    # reached from some refuel point and the agent can get back to one afterwards
    burn = np.array([cfg["fuel_burn"][t] for t in ["road", "grass", "mud", "ford"]], float)
    F = {p: _dijkstra(grid, p, burn) for p in [start, *stops, *stations]}
    cur, left, tour = start, set(stops), 0.0
    while left:  # nearest-neighbour tour fuel, no refuelling
        nxt = min(left, key=lambda s: F[cur][s]); tour += F[cur][nxt]; left.remove(nxt); cur = nxt
    refuel = [start, *stations]
    need = max(min(F[r][s] for r in refuel) + min(F[s][r] for r in refuel) for s in stops)
    capacity = int(max(np.ceil(cfg["capacity_factor"] * tour), np.ceil(need) + 2))

    return {
        "charging_stations": [list(s) for s in stations],
        "depot_recharges": True,
        "fuel_capacity": capacity,
        "fuel_burn": cfg["fuel_burn"],
        "teleport_tunnels": tunnels,
        "tunnel_cost": cfg["tunnel_cost"],
        "tunnel_fuel": cfg["tunnel_fuel"],
    }


if __name__ == "__main__":
    inst = json.loads((DATA / f"instance_{INSTANCE_ID}.json").read_text())
    grid = np.load(DATA / f"grid_{INSTANCE_ID}.npy")
    tw = make_twists(inst, grid)
    (DATA / f"twists_{INSTANCE_ID}.json").write_text(json.dumps(tw, indent=2))
    print(json.dumps(tw, indent=2))
    assert tw["fuel_capacity"] == 98, "Twist layout mismatch: check the instance files"
    print(f"Saved data/twists_{INSTANCE_ID}.json")