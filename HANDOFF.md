# HANDOFF: Ridgeline Courier (instance 38bfda97)

_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

## How to use this file
- We work one member at a time on `main` (turn order: Arsal → Laiba → Ali → Rayyan).
- **Start of your turn:** `git pull origin main`, then read every entry below.
- **End of your turn:** append your entry using the template (append only, never edit older
  entries). Then push and tag the turn: `git tag turn<N>-<firstname>` followed by `git push origin --tags`.
- If you change someone else's code, list it under "Changes to other people's code".

## Entry template
```
## Turn <N>: <Full Name> (<CMS ID>), <date>
### What I built
- ...
### How to run it
- ...
### Key results / numbers
- ...
### Files I created or changed
- ...
### Changes to other people's code (if any)
- ...
### Known issues / TODOs
- ...
### What the next person needs to know
- ...
```

---

## Turn 1 (part 1 of 2): M. Arsal Saeed (506676), 2026-11-21
### What I built
- Repo skeleton (full layout from CLAUDE.md, empty placeholder modules for later turns).
- Data files: `data/grid_38bfda97.npy`, `data/instance_38bfda97.json` (from `scripts/oel_instance.py`, unchanged), `data/twists_38bfda97.json` (from `scripts/make_twists.py`, unchanged), `data/elevation_38bfda97.npy` (new `scripts/make_elevation.py`: 4 Gaussian hills, heights 0..9, neighbouring cells differ by at most 1).
- `oel/config.py`: `MEMBERS`, `INSTANCE_ID`, `BASE_SEED` (= 952097431), hill constants + `assert REGEN < UP_FUEL`, `Config` dataclass, `parse_cli()` with validation.
- `oel/stamp.py`: `stamp()`, `save_fig()`, `save_table()`, `get_logger()`, plus `results/manifest.json`.
- `oel/world/plots.py`: instance map + elevation map (shared by `run_all.py` and `make_elevation.py`).
- `run_all.py` skeleton with Part A-E placeholders; tests in `tests/`.
### How to run it
- `python run_all.py --quick` (prints config, redraws the two maps), `pytest -q`.
- Live change: `python run_all.py --quick --slip 0.5 --stop 2=14,23 --no-tunnels --no-hills`.
### Key results / numbers
- instance_id 38bfda97 verified; twists match CLAUDE.md (capacity 98, stations, tunnels).
- Elevation: min 0, max 9, mean 3.05. Heights: start (5,4)=2; stops 0..4 = 2, 1, 1, 3, 4.
- `pytest -q`: 16 passed. `run_all.py --quick`: ~1 s.
### Files I created or changed
- Everything except `CLAUDE.md`, `scripts/oel_instance.py`, `scripts/make_twists.py`.
### Changes to other people's code (if any)
- None. Added `oel/world/plots.py` (not in the CLAUDE.md layout): shared map drawing code.
### Known issues / TODOs
- `docs/OEL_brief.txt` is still missing; please add it.
- CLAUDE.md's live-change example `--stop 2=14,22` is a BLOCKED cell on our grid (CLI rejects it correctly). Use `--stop 2=14,23` instead.
- Not built yet: DeliveryProblem, simulator, Parts D/E (my later sessions).
### What the next person needs to know
- Get every parameter from `Config` (`from oel.config import parse_cli, load_config`); never hard-code instance values.
- Save outputs ONLY via `oel.stamp.save_fig / save_table / get_logger` or `tests/test_stamp.py` fails.
- `save_table` CSVs start with a `# stamp` line: read them back with `pd.read_csv(path, comment="#")`.
- Grid indexing is `grid[row, col]`; cells are `(row, col)` tuples everywhere.

## Turn 1 (session 2): M. Arsal Saeed (506676), 2026-11-23
### What I built
- `oel/world/grid.py`: `build_cost_map`, `build_fuel_map` (vectorised lookup tables; blocked = inf).
- `oel/world/problem.py`: `DeliveryProblem(config, extra_blocked=(), start_state=None)` with the CLAUDE.md interface, plus helpers `successors`, `transition`, `replan_from`, `stop_index`, `is_station`, `is_refuel_point`, `tunnel_exit`, `height`, `delivered`, `describe`. The fuel rule lives in ONE function, `fuel_after()`.
- `oel/search/result.py`: `SearchResult`, `failed_result()`, `run_timed()` (runtime + tracemalloc peak).
- `oel/search/standin.py`: TEMPORARY plain UCS (`ucs(problem, is_goal=None, max_nodes=None)`).
- `oel/world/simulator.py`: `Simulator` (slip, rival, failed moves, `wait`), `StepInfo`, `RunReport`, `run_plan(actions, replan_fn=None)`, `RejoinReplanner` (rejoin -> wait -> full replan), `fuel_needed()`, placeholder rival `greedy_blocker`.
- `oel/experiments/standin_demo.py` (called by `run_all.py`): `standin_route.png`, `standin_summary`.
### How to run it
- `python run_all.py --quick` (~60 s), `pytest -q` (~80 s; `pytest -q -m "not slow"` skips the two full-map UCS runs, ~10 s).
### Key results / numbers
- Stand-in UCS reproduces every CLAUDE.md reference: hills OFF **307** (1.84M nodes, 2 recharges), no tunnels 400, no fuel 296. **Hills ON: 318** (1.81M nodes, ~35 s), added to CLAUDE.md. The hills add only +11 (3.6%).
- Default simulation (seed 952097431, slip 0.25): **loss, stranded** after 112 steps, 33 slips, 30 rejoins + 2 full replans. Over 6 seeds: 1 win, 4 strandings, 1 draw (the rival parked on the last stop).
### Files I created or changed
- New: `oel/search/standin.py`, `oel/experiments/standin_demo.py`, `tests/test_problem.py`, `tests/test_simulator.py`.
- Filled placeholders: `oel/world/grid.py`, `problem.py`, `simulator.py`, `oel/search/result.py`.
- Changed: `oel/config.py` (+ `failed_move_cost`, `max_steps`, `rejoin_radius`), `oel/world/plots.py` (+ `plot_route`), `run_all.py`, `pytest.ini` (`slow` marker), `CLAUDE.md` (hills-ON reference 318).
### Changes to other people's code (if any)
- `oel/world/grid.py` is Rayyan's Part A file: I added only the vectorised maps; the loop version + benchmark is left as `# TODO(Rayyan)`.
### Known issues / TODOs
- **Optimal plans have no fuel margin.** The 318 plan runs the tank near 0 before recharging, so slips (which burn fuel) often strand the agent. That's a real finding for Ali's slip analysis. A possible fix: plan with a fuel reserve.
- The placeholder rival can park on the last undelivered stop -> the agent waits -> "draw". Ali's adversarial rival replaces `greedy_blocker`.
- A full UCS replan from the start of the route takes ~15-35 s. Laiba's A* should make full replans much cheaper.
### What the next person needs to know
- **Laiba:** planners take `planner(problem, **kwargs) -> SearchResult`. To replan mid-route, the simulator calls your planner on `problem.replan_from(state, extra_blocked)`, so just use `problem.initial_state()` and never assume the start is the depot with a full tank. `problem.successors(state)` is a faster (action, next_state, cost) helper with identical rules. Moves are direction-dependent (hills): build heuristic distance fields BACKWARDS over reversed edges. To swap planners: `RejoinReplanner(full_planner=your_astar, rejoin_planner=ucs, radius=cfg.rejoin_radius)` (rejoin_planner must accept `is_goal=` and `max_nodes=`). Delete `oel/search/standin.py` and update `standin_demo.py` + tests that import it.
- **Ali:** a rival is `rival_policy(sim) -> "N"/"S"/"E"/"W"/None`; pass it as `Simulator(..., rival_policy=...)`. `RunReport` has slips, failed_moves, waits, replans (kind per replan), extra_cost (NaN unless win), end_reason.
- A failed move (slip into a wall/rival) and a wait both cost `failed_move_cost` (1) and burn no fuel.

## Turn 1 (session 3): M. Arsal Saeed (506676), 2026-11-23
### What I changed
- **Hills stronger:** UP_COST 1->2, UP_FUEL 2->3 (REGEN 1, still < UP_FUEL). Hills-ON optimum **329** (+7.2% over 307), but the route is IDENTICAL to hills OFF: the fuel/station constraints pin it. With `--no-fuel` the hills do change the route (296 -> 320, 41 different cells).
- **Planning fuel reserve** (`cfg.fuel_reserve`, CLI `--fuel-reserve`, default **20**). DeliveryProblem only plans moves that leave >= reserve fuel. The Simulator executes with `problem.with_reserve(0)` (the real limit). Replans keep the reserve and fall back to 0 (kind `full_no_reserve`) if slips already pushed the tank below it.
- `oel/experiments/fuel_reserve.py` (+ `oel/experiments/stats.py` with `wilson_ci`): reserves 0/5/10/15/20 x 30 seeds; tables `fuel_reserve`, `fuel_reserve_runs`; figure `fuel_reserve.png`. Win rate 13% -> 63% from reserve 0 to 20; planned cost 329 -> 353.
- `RunReport.extra_cost_text()`: "n/a (stranded)" for losses.
### How to run it
- `python -m oel.experiments.fuel_reserve` (30 seeds, ~28 min, 3 worker processes) or `--quick` (10 seeds, ~10 min). Full `python run_all.py` runs it; `--quick` skips it (too slow for the 5-minute limit with the stand-in UCS).
### What the next person needs to know
- **Reference optima are computed with `--fuel-reserve 0`** (307, 329). With the default reserve 20 the stand-in plan costs 353.
- Laiba: the reserve lives inside DeliveryProblem, so your planners need no change. A faster A* would make the fuel-reserve experiment fit in `--quick` again.
- Memory: one full UCS uses ~360 MB of Python memory, and `tracemalloc` makes it ~5-8x slower.
