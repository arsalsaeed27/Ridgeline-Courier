"""Central configuration for the Ridgeline Courier project (instance 38bfda97).

Everything that describes the problem (grid, stops, twists, hills, slip, rival) is loaded
from data/ into ONE Config object. Algorithms read their parameters from that object and
never hard-code instance values, so a live change in the viva is just a CLI flag:

    python run_all.py --quick --slip 0.5 --stop 2=14,23 --no-tunnels --no-hills
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# ---------------------------------------------------------------- team + instance
# Order = order printed in the stamp line (matches CLAUDE.md exactly).
MEMBERS = [
    ("Laiba Rehman", "505099"),
    ("M. Arsal Saeed", "506676"),
    ("Ali Salman Mustafa", "534732"),
    ("M. Rayyan", "534733"),
]
INSTANCE_ID = "38bfda97"

# One master seed for every random thing in the project. It is derived from the sorted
# CMS IDs (same recipe as the instance generator), so it is fixed for our group and
# anyone can recompute it. Experiments derive their own seeds from it (BASE_SEED + i).
_seed_key = "|".join(sorted(cms for _, cms in MEMBERS))
BASE_SEED = int(hashlib.sha256(_seed_key.encode()).hexdigest()[:8], 16)

TERRAINS = ["road", "grass", "mud", "ford"]   # cell codes 0, 1, 2, 3 (-1 = blocked)
BLOCKED = -1

# ---------------------------------------------------------------- twist 3: hills
# dh = h(next) - h(current) for a normal move.
#   path cost = terrain_cost(next) + UP_COST * max(dh, 0)
#   fuel      = fuel_burn(next)    + UP_FUEL * max(dh, 0) - REGEN * max(-dh, 0)
UP_COST = 2   # extra path cost per height unit climbed
UP_FUEL = 3   # extra fuel burned per height unit climbed
REGEN = 1     # fuel recovered per height unit descended (regenerative braking)

# Why REGEN < UP_FUEL: climbing k units costs 3k fuel and coming back down returns only k,
# so any up-and-down loop LOSES fuel overall. If REGEN >= UP_FUEL the agent could gain
# fuel for free by bouncing between two cells, which breaks the idea of a fuel limit and
# could let a search keep finding "better" fuel states forever.
assert REGEN < UP_FUEL, "REGEN must stay below UP_FUEL (no free-fuel loops)"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


@dataclass
class Config:
    """All problem parameters. Build one with Config.load() or parse_cli()."""
    # world
    grid: np.ndarray
    elevation: np.ndarray
    start: tuple
    stops: list                    # list of (row, col); index = bit in delivered_mask
    terrain_cost: dict             # terrain name -> path cost of ENTERING that terrain
    # uncertainty + rival
    slip: float
    rival_type: str
    rival_depth: int
    # twist 1: fuel
    fuel_capacity: int
    fuel_burn: dict                # terrain name -> fuel burned entering that terrain
    stations: list                 # charging stations (the depot also recharges)
    depot_recharges: bool
    # twist 2: tunnels
    tunnels: list                  # list of ((r1, c1), (r2, c2)), bidirectional
    tunnel_cost: float
    tunnel_fuel: int
    # twist 3: hills
    up_cost: int = UP_COST
    up_fuel: int = UP_FUEL
    regen: int = REGEN
    # simulator ("real world") settings
    failed_move_cost: float = 1.0  # a move that fails (slip into a wall/rival) still wastes one time step
    max_steps: int = 600           # step limit for one simulated run -> outcome "draw"
    rejoin_radius: int = 4         # after a slip, look this far (Manhattan) for a way back onto the plan
    # planning safety margin: the PLANNER never lets fuel drop below this (the real world's
    # limit stays 0). Chosen with oel/experiments/fuel_reserve.py, see docs/viva_notes.md.
    fuel_reserve: int = 20
    # Part D: LLM dispatcher (Groq). gpt-oss-120b: a production Groq model with tool calling.
    llm_model: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.0
    llm_max_tool_calls: int = 8
    llm_live: bool = False         # False = replay cached LLM replies only (no API key needed)
    # planners get_instance_info advertises to the LLM. Pinned to what the Part D benchmark was
    # graded with, so the cached conversations replay exactly; widen it with a live re-run.
    llm_algorithms: tuple = ("ucs",)
    # twist on/off flags
    use_fuel: bool = True
    use_tunnels: bool = True
    use_hills: bool = True
    # run options
    quick: bool = False
    seed: int = BASE_SEED
    instance_id: str = INSTANCE_ID
    overrides: list = field(default_factory=list)   # human-readable list of applied CLI changes

    @classmethod
    def load(cls, data_dir: Path = DATA_DIR) -> "Config":
        inst = _load_json(data_dir / f"instance_{INSTANCE_ID}.json")
        tw = _load_json(data_dir / f"twists_{INSTANCE_ID}.json")
        grid = np.load(data_dir / f"grid_{INSTANCE_ID}.npy")
        elev = np.load(data_dir / f"elevation_{INSTANCE_ID}.npy")
        assert inst["instance_id"] == INSTANCE_ID, "data/ holds a different instance"
        return cls(
            grid=grid,
            elevation=elev,
            start=tuple(inst["start"]),
            stops=[tuple(s) for s in inst["delivery_stops"]],
            terrain_cost=dict(inst["terrain_cost"]),
            slip=float(inst["slip_probability"]),
            rival_type=inst["adversary"],
            rival_depth=int(inst["adversary_search_depth"]),
            fuel_capacity=int(tw["fuel_capacity"]),
            fuel_burn=dict(tw["fuel_burn"]),
            stations=[tuple(s) for s in tw["charging_stations"]],
            depot_recharges=bool(tw["depot_recharges"]),
            tunnels=[(tuple(a), tuple(b)) for a, b in tw["teleport_tunnels"]],
            tunnel_cost=float(tw["tunnel_cost"]),
            tunnel_fuel=int(tw["tunnel_fuel"]),
        )

    # ---------------------------------------------------------- small helpers
    @property
    def n(self) -> int:
        return self.grid.shape[0]

    def is_free(self, cell) -> bool:
        r, c = cell
        return 0 <= r < self.n and 0 <= c < self.n and self.grid[r, c] != BLOCKED

    def refuel_cells(self) -> list:
        """Cells that refill fuel to capacity: the stations, plus the depot."""
        cells = list(self.stations)
        if self.depot_recharges:
            cells.append(self.start)
        return cells

    def reachable_from_start(self) -> np.ndarray:
        """Boolean mask of cells reachable from the depot by normal moves (tunnels ignored).
        Used only for validating CLI changes, NOT a graded search algorithm."""
        seen = np.zeros(self.grid.shape, dtype=bool)
        seen[self.start] = True
        queue = deque([self.start])
        while queue:
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (r + dr, c + dc)
                if self.is_free(nxt) and not seen[nxt]:
                    seen[nxt] = True
                    queue.append(nxt)
        return seen

    def summary(self) -> str:
        on = lambda b: "ON" if b else "OFF"
        lines = [
            f"instance {self.instance_id}: grid {self.n}x{self.n}, start/depot {self.start}",
            f"stops: {self.stops}",
            f"terrain cost: {self.terrain_cost}",
            f"slip {self.slip} | rival {self.rival_type} depth {self.rival_depth} | seed {self.seed}",
            f"fuel {on(self.use_fuel)}: capacity {self.fuel_capacity}, burn {self.fuel_burn}, "
            f"stations {self.stations}, planning reserve {self.fuel_reserve}",
            f"tunnels {on(self.use_tunnels)}: {self.tunnels} (cost {self.tunnel_cost}, fuel {self.tunnel_fuel})",
            f"hills {on(self.use_hills)}: UP_COST {self.up_cost}, UP_FUEL {self.up_fuel}, REGEN {self.regen}",
            f"quick mode: {self.quick}",
        ]
        if self.overrides:
            lines.append("CLI overrides: " + "; ".join(self.overrides))
        return "\n".join(lines)


# ---------------------------------------------------------------- CLI
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ridgeline Courier (instance 38bfda97)")
    p.add_argument("--quick", action="store_true", help="fast run (< 5 min) for the viva")
    p.add_argument("--slip", type=float, help="slip probability in [0, 1)")
    p.add_argument("--stop", action="append", default=[], metavar="IDX=R,C",
                   help="move delivery stop IDX to cell (R,C); repeatable")
    p.add_argument("--rival-depth", type=int, help="rival search depth (>= 1)")
    p.add_argument("--fuel-capacity", type=int, help="fuel tank size (>= 1)")
    p.add_argument("--fuel-reserve", type=int,
                   help="planning safety margin: plans never go below this fuel (0..capacity-1)")
    p.add_argument("--no-fuel", action="store_true", help="turn off the fuel twist")
    p.add_argument("--no-tunnels", action="store_true", help="turn off the tunnel twist")
    p.add_argument("--no-hills", action="store_true", help="turn off the hills twist")
    p.add_argument("--seed", type=int, help="override BASE_SEED")
    p.add_argument("--live", action="store_true",
                   help="call the Groq API for LLM replies missing from the cache (needs GROQ_API_KEY)")
    p.add_argument("--llm-model", help="Groq model id for the LLM dispatcher")
    return p


def _parse_stop(text: str) -> tuple:
    """'2=14,22' -> (2, (14, 22))."""
    try:
        idx_part, cell_part = text.split("=")
        r, c = cell_part.split(",")
        return int(idx_part), (int(r), int(c))
    except ValueError:
        raise ValueError(f"--stop must look like IDX=R,C (got {text!r})") from None


def parse_cli(argv=None, data_dir: Path = DATA_DIR) -> Config:
    """Parse CLI flags and return a validated Config with the overrides applied.
    Raises ValueError for an invalid override (bad slip, blocked/unreachable stop, ...)."""
    args = build_arg_parser().parse_args(argv)
    cfg = Config.load(data_dir)
    cfg.quick = args.quick

    if args.slip is not None:
        if not 0.0 <= args.slip < 1.0:
            raise ValueError(f"--slip must be in [0, 1), got {args.slip}")
        cfg.slip = args.slip
        cfg.overrides.append(f"slip={args.slip}")

    if args.rival_depth is not None:
        if args.rival_depth < 1:
            raise ValueError("--rival-depth must be >= 1")
        cfg.rival_depth = args.rival_depth
        cfg.overrides.append(f"rival_depth={args.rival_depth}")

    if args.fuel_capacity is not None:
        if args.fuel_capacity < 1:
            raise ValueError("--fuel-capacity must be >= 1")
        cfg.fuel_capacity = args.fuel_capacity
        cfg.overrides.append(f"fuel_capacity={args.fuel_capacity}")

    if args.fuel_reserve is not None:
        cfg.fuel_reserve = args.fuel_reserve
        cfg.overrides.append(f"fuel_reserve={args.fuel_reserve}")
    # checked even without the flag: a smaller --fuel-capacity could make the default too big
    if not 0 <= cfg.fuel_reserve < cfg.fuel_capacity:
        raise ValueError(f"--fuel-reserve must be in 0..{cfg.fuel_capacity - 1}, got {cfg.fuel_reserve}")

    if args.live:
        cfg.llm_live = True
        cfg.overrides.append("live LLM")
    if args.llm_model:
        cfg.llm_model = args.llm_model
        cfg.overrides.append(f"llm_model={args.llm_model}")

    if args.seed is not None:
        cfg.seed = args.seed
        cfg.overrides.append(f"seed={args.seed}")

    if args.no_fuel:
        cfg.use_fuel = False
        cfg.overrides.append("no-fuel")
    if args.no_tunnels:
        cfg.use_tunnels = False
        cfg.overrides.append("no-tunnels")
    if args.no_hills:
        cfg.use_hills = False
        cfg.overrides.append("no-hills")

    if args.stop:
        reach = cfg.reachable_from_start()
        for text in args.stop:
            idx, cell = _parse_stop(text)
            if not 0 <= idx < len(cfg.stops):
                raise ValueError(f"stop index {idx} out of range 0..{len(cfg.stops) - 1}")
            if not cfg.is_free(cell):
                raise ValueError(f"stop {idx} -> {cell} is outside the grid or blocked")
            if not reach[cell]:
                raise ValueError(f"stop {idx} -> {cell} is not reachable from the depot")
            if cell == cfg.start or cell in cfg.stops[:idx] + cfg.stops[idx + 1:]:
                raise ValueError(f"stop {idx} -> {cell} clashes with the depot or another stop")
            cfg.stops[idx] = cell
            cfg.overrides.append(f"stop{idx}={cell}")

    return cfg


def load_config() -> Config:
    """Default config with no overrides (handy in notebooks and tests)."""
    return Config.load()
