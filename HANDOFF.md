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

## Turn 1 (session 4): M. Arsal Saeed (506676), 2026-11-23
### What I built (Part D: LLM dispatcher)
- `oel/world/constraints.py`: `PlanConstraints` (stop_order, avoid_terrain, avoid_cells, use_tunnels, fuel_reserve, max_cost) + `verify_plan()` (independent replay on the plain map). Wired into `DeliveryProblem(config, constraints=...)`; unconstrained behaviour is unchanged (307/329 tests pass).
- `oel/llm/plans.py`: planner registry (`register_planner(name, fn)`), on-disk plan cache (`oel/llm/cache/plans/`) and sim cache (`.../sims/`), keyed by hashes of algorithm + resolved constraints + planning config.
- `oel/llm/tools.py` (get_instance_info, plan_route, simulate, fuel_report), `validator.py` (pydantic + map checks + contradiction pre-check), `agent.py` (own ReAct loop, Groq tool calling, LLM response cache, retry with backoff, traces).
- `oel/llm/requests.json` (20 requests, 4 tiers) + `docs/llm_gold_answers.md`; `oel/experiments/llm_eval.py` (direct vs LLM vs LLM+validation, outcome-based grading); `report/sections/part_d_traces.md`.
### How to run it
- `python run_all.py --quick` replays Part D from the committed caches (no key needed). `python -m oel.experiments.llm_eval --live` calls Groq for missing replies (needs `GROQ_API_KEY` in `.env`). `--llm-model <id>` switches the model.
### Key results / numbers
- Model `openai/gpt-oss-120b` (Groq production model with tool calling), temperature 0, max 8 tool calls.
- Success: direct 18/18, LLM 20/20, LLM+validation 20/20 (Wilson 95% CI 0.84-1.00); 1.6 tool calls per request; 0 validator rejections; 0 API failures.
- Map facts found: avoiding mud cuts the depot off from stops 0-3 (infeasible); avoiding ford is feasible (465).
### Known issues / TODOs
- The benchmark does not separate validation ON/OFF for gpt-oss-120b (it made no argument errors). Because the LLM cache key is the conversation, validation-ON replayed validation-OFF replies until a rejection would have made them differ (none did).
- In `--quick`, Part D is skipped if the gold plans for the current config aren't cached (e.g. a live change with `--no-hills`).
### What the next person needs to know
- **Laiba:** `from oel.llm.plans import register_planner; register_planner("astar", astar)` makes it available to the LLM (`get_instance_info` lists it). Planners must work with `DeliveryProblem(constraints=...)`; nothing changes for you if you only use the interface.
- `verify_plan(actions, constraints, cfg)` is a handy independent checker for your planners too.

### Turn 1 (session 4, addendum): weak model + validator fault injection
- **Two models** (`EVAL_MODELS` in `oel/experiments/llm_eval.py`): gpt-oss-120b 20/20 (OFF and ON); gpt-oss-20b 19/19 graded + 1 `ambiguous_reading` (H1: it chose stop 1 by straight-line distance, not stop 4 by path cost; 391 vs 353). **0 validator rejections for both models**, so the validation-ON runs followed exactly the same conversation as OFF. Honest summary: *neither model needed validation on our 20 requests; fault injection shows what the validator prevents regardless of model.*
- **Fault injection** (`oel/experiments/validator_fault_injection.py`, no API): 18 gold calls x 10 corruption types = 180 calls. Validator catches **100%**. Without it: 53 crashes, 30 silent ignores, 15 silent wrong plans (negative reserve -> fuel below 0), 18 wasted searches, 39 misleading "infeasible", 25 correct errors. That is 671 s of planning that validation avoids. Cached in `oel/llm/cache/fault_injection.json`; `run_all --quick` reuses it.
- Note for the report: in every fault row, 1 call is A3 (its gold call already contains the stop-0 contradiction, so the planner's pre-check reports it correctly), and A2/A5 are infeasible to begin with. That is why most rows have one `correct_error` and one wasted/misleading result that are not caused by the fault.
- Trace folders are now `results/logs/llm_traces/<model>_val-{on,off}/`.
- **Third model:** `openai/gpt-oss-safeguard-20b`. The smaller models in Groq's tool-use docs are not usable with our key: `llama-3.1-8b-instant` returns 404 (no access) and `allam-2-7b` (7B) rejects tool calling. So the smallest usable tool-calling models are the two 20B gpt-oss models. Result: 13/13 graded requests correct + 1 `ambiguous_reading` (H1, straight-line reading like 20b), **0 validator rejections**, and **6 of 20 runs lost to API errors**: our tier allows this model only **2,000 tokens/minute** and a request needs about 2,400 (HTTP 413). API failures are now cached (so replays are exact), reported in `runs_lost_to_api_errors` and NOT graded as LLM mistakes.
- `report/sections/part_d_traces.md`: (1) a successful run, (2) "no failure was fixed by validation" (no model had a validator rejection), (3) H1 for all three models: 120b reads "closest" by path cost (stop 4, 353); both 20B models read it as straight-line (stop 1, 391).
- Final honest summary for Part D: *none of the three models needed validation on our 20 requests; the smaller models differ only in how they read a vague request; fault injection shows what the validator prevents regardless of model.*

---

## Turn 1: M. Arsal Saeed (506676), 2026-11-23 (FINAL, all sessions)
### What I built
- **Shared base:** repo layout; `oel/config.py` (MEMBERS, INSTANCE_ID, BASE_SEED, hill constants, `Config`, `parse_cli` with validation; LLM settings); `oel/stamp.py` (stamp, save_fig, save_table, get_logger, manifest); data files incl. the elevation map (`scripts/make_elevation.py`); `oel/world/plots.py`.
- **World model:** `oel/world/grid.py` (vectorised cost/fuel maps; loop version left for Rayyan), `oel/world/problem.py` (DeliveryProblem; one fuel rule `fuel_after`; planning fuel reserve; constraints), `oel/world/constraints.py` (PlanConstraints, verify_plan), `oel/world/simulator.py` (slip, placeholder rival, failed moves/waits, RejoinReplanner, per-step timeline).
- **Search plumbing:** `SearchResult` (+ optional `expanded_order`), `run_timed`, `oel/search/registry.py` (planner + heuristic registries), TEMPORARY `oel/search/standin.py` (plain UCS).
- **Twist 3 (hills):** UP_COST 2, UP_FUEL 3, REGEN 1 (REGEN < UP_FUEL asserted).
- **Experiments:** `standin_demo.py`, `fuel_reserve.py` (+ `stats.py` with `wilson_ci`), `llm_eval.py`, `validator_fault_injection.py`.
- **Part D:** `oel/llm/` (plans + caches, tools, validator, agent, 20 requests), `docs/llm_gold_answers.md`, `report/sections/part_d.md`, `part_d_traces.md`.
- **Part E:** `ui/app.py` + `ui/views.py` (Streamlit + Plotly, 7 tabs), `tests/test_ui.py`, `report/sections/part_e.md`; `run_all.py` with a final list of every output file.
### How to run it
- `pip install -r requirements.txt`; `pytest -q` (64 tests, ~2 min; `-m "not slow"` skips the two full-map UCS tests); `python run_all.py --quick` (~1.5 min); `python run_all.py` (full, adds the 28-min fuel-reserve experiment and recomputes fault injection if needed); `streamlit run ui/app.py`.
- Live LLM calls: put `GROQ_API_KEY` in `.env`, then `python -m oel.experiments.llm_eval --live`. Without a key everything replays from `oel/llm/cache/`.
### Key results / numbers
- **Reference optima** (stand-in UCS, `--fuel-reserve 0`): hills OFF **307** (1.84M nodes, 2 recharges), hills OFF no tunnels **400**, hills OFF no fuel **296**, **hills ON 329** (+7.2%; same route as hills OFF because fuel/stations pin it; with `--no-fuel` the hills do reroute, 296 -> 320).
- **Fuel reserve** (30 seeds each, slip 0.25): win rate 13% / 47% / 47% / 53% / 63% for reserve 0 / 5 / 10 / 15 / 20; planned cost 329 -> 353. Default reserve **20** (no reserve reached 80%; the best one was chosen by the rule fixed in advance).
- **Default simulation** (seed 952097431, reserve 20): win, real cost 877 vs planned 353, 345 steps, 98 slips, 93 rejoins + 8 full replans.
- **LLM:** gpt-oss-120b 20/20; gpt-oss-20b 19/19 + 1 ambiguous (H1); gpt-oss-safeguard-20b 13/13 + 1 ambiguous + 6 lost to API limits (2,000 TPM). 0 validator rejections for all models.
- **Fault injection:** 180 corrupted calls, validator catches 100%; without it 53 crash, 30 silently ignored, 15 silently wrong plans, 18 wasted searches, 39 misleading "infeasible", 25 correct errors (671 s of planning avoided).
- Map fact: avoiding mud cuts the depot off from stops 0-3.
### Files I created or changed
- Everything in the repo except `scripts/oel_instance.py`, `scripts/make_twists.py` and the placeholder files of later turns (`oel/search/uninformed.py`, `informed.py`, `heuristics.py`, `oel/game/*`). `CLAUDE.md` edited: references, twist constants, interfaces.
### Changes to other people's code (if any)
- `oel/world/grid.py` (Rayyan, Part A): only the vectorised maps; `# TODO(Rayyan): loop version + benchmark` is left for him.
- `CLAUDE.md`: SearchResult gained the optional `expanded_order`; registries and constraints documented; hills-ON reference 329.
### Known issues / TODOs
- The stand-in UCS is slow: 25-50 s and ~360 MB per full-map plan (tracemalloc makes it 5-8x slower). So the fuel-reserve experiment is skipped in `--quick`, and live changes that alter planning skip the cached Part D in `--quick`.
- The placeholder rival (`greedy_blocker`) can park on the last undelivered stop -> the agent waits -> "draw".
- The hills do not change the optimal route while the fuel limit is ON (they change its cost).
- The LLM benchmark did not separate validation ON/OFF (no model made argument errors); the fault injection shows the validator's value.
- The UI search animation shows only the first 200,000 expansions of a big search (`EXPANDED_ORDER_CAP`).
### What the next person needs to know
- See **"Laiba, start here"** right below.

## Laiba, start here (Turn 2)
**Your part:** BFS, UCS, DLS, IDS, Greedy, A*, weighted A* from scratch; our MST-based, hill-aware heuristic + admissibility proof + consistency test; 2 baseline heuristics; IDS vs A* under a memory limit; the 30-seed experiments framework with 95% CIs and an ablation; the evaluation function for Ali's rival game.

**Use these, don't rebuild them:**
- `DeliveryProblem` (`oel/world/problem.py`): `initial_state / is_goal / actions / result / step_cost`, plus the fast helper `successors(state)` (same rules). State = `(row, col, delivered_mask, fuel)`. **Always start from `problem.initial_state()`**: the simulator replans mid-route through `problem.replan_from(state, extra_blocked)`, and user constraints and the fuel reserve live inside the problem, so your planners need no extra code for them.
- `SearchResult` (`oel/search/result.py`): fill every field, and also **`expanded_order`** (append `(row, col)` of each expanded state while `len < EXPANDED_ORDER_CAP`); the UI's search tab uses it. Measure time and memory with `run_timed(planner, problem)`.
- **Registries** (`oel/search/registry.py`): `register_planner("astar", astar, uses_heuristic=True)` and `register_heuristic("mst", h_mst)`. Your planners then appear in the UI dropdowns, the LLM tools and the plan cache automatically. Replace the stand-in line at the bottom with your own `register_planner("ucs", ucs)`.
- `verify_plan(actions, constraints, cfg)` checks any plan independently; `oel/experiments/stats.py` has `wilson_ci`.
- **Hills make moves direction-dependent** (A->B != B->A): compute heuristic distance fields BACKWARDS over reversed edges from each stop. Fuel can rise without a station (regen), so don't assume fuel only goes down. Ignoring fuel in a heuristic is a valid relaxation (it can only make the true cost higher).

**Tests you must keep passing:** all of `pytest -q` (64 now), especially `tests/test_problem.py`: UCS **307** (hills OFF) and **329** (hills ON), both with `--fuel-reserve 0`. Add UCS == A* == 307 / 329 tests and the heuristic admissibility test (h <= true cost-to-go on sampled states).

**Delete the stand-in** `oel/search/standin.py` once your UCS works, and switch everything that imports it to your `oel.search.uninformed.ucs`: `oel/search/registry.py`, `oel/llm/plans.py`, `oel/llm/tools.py`, `oel/experiments/standin_demo.py`, `oel/experiments/fuel_reserve.py`, `ui/app.py`, `tests/test_problem.py`, `tests/test_simulator.py`, `tests/test_llm.py` (`grep -rn standin --include=*.py .` lists them). Your UCS must accept `is_goal=` and `max_nodes=` (the simulator's rejoin uses them), or keep a small UCS for that.

**Plan cache note:** cached plans are keyed by the algorithm NAME. If your UCS is registered as `"ucs"`, the cached stand-in plans are reused (same optimal costs), so Part D still replays from the cache. Only bump `CACHE_VERSION` in `oel/llm/plans.py` if the planning RULES change: that invalidates every cached plan id and the cached LLM conversations (they would then need a live re-run with a key).

**Speed:** once A* is fast, move the fuel-reserve experiment back into `--quick` (see the comment in `run_all.py`) and use A* for the simulator's full replans (`RejoinReplanner(full_planner=astar, ...)`). Keep `python run_all.py --quick` under 5 minutes.

---

## Turn 2 (session 1): Laiba's part, done by M. Arsal Saeed (506676), 2026-11-25
### What I built
- `oel/search/uninformed.py`: `bfs` (graph search, goal test on generation), `ucs` (goal test on pop; keeps `is_goal=` / `max_nodes=` for the simulator's rejoin), `dls` (recursive, on-path cycle check, cutoff vs failure, node/time budget), `ids` (DLS 0..max_depth, per-iteration nodes, re-expansions, total budget).
- `oel/search/informed.py`: `greedy` (h only, visited set), `astar` (f = g + w*h, ties to larger g, reopens closed states and counts it), `weighted_astar` (A* with w, default 2).
- `oel/search/heuristics.py`: `h_zero` only (the real heuristics come next session). `oel/search/common.py`: shared path/result helpers.
- `oel/experiments/small_instances.py` (masking: real map, everything outside a 7x7 window around the depot becomes a wall, 1-3 seeded stops, redrawn if infeasible) and `oel/experiments/search_small.py` (comparison table). `oel/experiments/stats.py`: + `mean_ci` (t) and `bootstrap_mean_ci`.
- `tests/test_search.py`.
### How to run it
- `python -m oel.experiments.search_small` (~6 s; also part of `run_all.py --quick`). `pytest -q tests/test_search.py -m "not slow"` (~5 s).
### Key results / numbers
- `results/tables/search_uninformed_small` (30 instances, mean [95% bootstrap CI]): all algorithms solve 30/30 except DLS(d*-1), which returns cutoff 30/30 as it must. Mean nodes: BFS 70, UCS 74, A*(h_zero) 74, Greedy(h_zero) 79, DLS(d*) 5,381, IDS 35,840. BFS / DLS / IDS / Greedy cost 1.07x the optimum on average; UCS and A* are always optimal. Every plan passes `verify_plan`.
- IDS limits: with fuel ON (25/30) or a 9x9 window (24/30) IDS runs out of its 500k-node budget, because fuel makes "the same cell" a new state and the on-path check stops pruning. That's why the table uses a 7x7 window with fuel off.
### Files I created or changed
- New: `oel/search/uninformed.py`, `informed.py`, `common.py`, `oel/experiments/small_instances.py`, `search_small.py`, `tests/test_search.py`. Changed: `heuristics.py`, `registry.py`, `oel/experiments/stats.py`, `run_all.py`, `docs/viva_notes.md`, `CLAUDE.md`.
- **Deleted `oel/search/standin.py`**; all 10 importers now use `oel.search.uninformed.ucs`. `CACHE_VERSION` unchanged, so cached plans still load (tested).
### Changes to other people's code (if any)
- `oel/search/result.py` (shared interface): **new optional field `stats: dict`** (reason, goal_test, steps, IDS iterations / re_expansions, A* reopened, weight). Recorded in CLAUDE.md. Existing code is unaffected (it defaults to `{}`).
- `oel/llm/plans.py`: plan records also store `stats`; an unsolved search that stopped on a budget says so in its reason.
- `oel/config.py` + `oel/llm/tools.py`: new `cfg.llm_algorithms = ("ucs",)`. `get_instance_info` advertises only these, so the Part D benchmark replays exactly. The validator still accepts every registered planner. Widen it with ONE deliberate live re-run after the heuristic session.
### Known issues / TODOs
- Heuristics (MST + 2 baselines + admissibility proof/test), full-map A* comparison, weighted A* study, IDS vs A* under a memory limit, 30-seed experiments + ablation: next sessions.
- `dls` / `ids` on the full map only stop on their budgets (expected).
### What the next person needs to know
- All planners are registered (`bfs, ucs, dls, ids, greedy, astar, weighted_astar`) plus `h_zero`; they show up in the UI's Plan and Search tabs automatically.
