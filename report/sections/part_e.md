_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part E: user interface and reproducibility (draft, M. Arsal Saeed)

## One command
`python run_all.py` rebuilds every figure and table in `results/`; `python run_all.py --quick`
finishes in under 5 minutes (measured ~1.5 min) for the viva live change. All parameters come from
one `Config` (`oel/config.py`) with CLI overrides, e.g.
`python run_all.py --quick --slip 0.5 --stop 2=14,23 --no-tunnels --no-hills`; invalid values (a stop
on a wall, slip ≥ 1, a reserve above the tank) are rejected with a one-line message. All randomness
uses `numpy.random.default_rng` with seeds derived from `BASE_SEED` (sha256 of our CMS IDs).
Every output is written through `oel/stamp.py` (figure title + PNG metadata, first table line,
first log line), and `tests/test_stamp.py` checks every file in `results/`. At the end, `run_all.py`
lists every output file it wrote.

Expensive results are cached on disk under content hashes (plans, simulations, LLM replies, fault
injection), so `--quick` replays Part D in seconds; a live change that alters planning
(`--no-hills`, a moved stop) is detected and those cached parts are skipped with a message.

## Streamlit UI (`streamlit run ui/app.py`)
The UI contains no planning logic: it calls the same code as `run_all.py`.
- **Banner** with all four names, CMS IDs and the instance id on every page.
- **Sidebar live change**: slip, fuel reserve, rival depth, fuel capacity, the three twist toggles,
  moving any stop 0–4 (validated: free and reachable), seed, and reset. The widgets are converted
  into the exact CLI arguments and passed to `parse_cli`; the equivalent command line is shown.
- **World**: terrain or elevation map with depot, stops 0–4, stations, tunnel pairs, walls.
- **Plan**: algorithm and heuristic from the planner/heuristic registries (new planners appear
  automatically), constraints (stop order, avoided terrain, no tunnels), the route, a stats table
  (cost, nodes, runtime, optional peak memory, refuels, tunnels, climb) and a fuel + height profile.
- **Search visualisation**: from `SearchResult.expanded_order`, condensed into a 40×40
  "first expanded" grid (animation with play button and slider) and an expansion-count grid (log
  heatmap); two planners side by side for comparison (e.g. UCS vs A* in Turn 2).
- **Simulate**: animation of the agent, rival, slips and replans with the fuel over time; outcome
  and replan statistics.
- **Rival game**: placeholder for Turn 3 (Minimax / Alpha-Beta), showing the current rival.
- **LLM Dispatcher**: any of the 20 requests (cached) or a custom one (live, if a key exists), the
  answer, the plan on the map and an expandable Thought / Action / Observation timeline.
- **Experiments**: every stamped table and figure grouped by part, for a demo without re-running.

Responsiveness: nothing expensive runs on page load; planning, recording a search and simulating
happen on a button press with a spinner and a time estimate, and are cached.

## Testing
`tests/test_ui.py` drives the app headlessly (Streamlit AppTest): it loads, all seven tabs render,
the stamp is on the page, the slip slider changes the config, an invalid stop move shows an error
(no crash), reset restores defaults, and a cached LLM request replays.
