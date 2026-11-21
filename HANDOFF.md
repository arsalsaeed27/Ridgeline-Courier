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
