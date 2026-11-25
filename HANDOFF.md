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

---

## Turn 2 (session 2): Laiba's part, done by M. Arsal Saeed (506676), 2026-11-25
### What I built
- `oel/search/distance_fields.py`: relaxed distances D_i(cell) (same walls / terrain / hills / tunnels / avoided cells, NO fuel), by our own backward Dijkstra over reversed edges, cached per map + constraints.
- `oel/search/heuristics.py`: `h_manhattan_raw` (inadmissible example), `h_manhattan` (baseline 1, tunnel-aware with any number of hops), `h_farthest` (baseline 2), `h_mst` (Prim), **`h_ours = max(h_mst, h_farthest)`**; all memoised on (cell, mask) and registered.
- `FuelDominance` pruning (`prune_dominated=True`) in `ucs` and `astar` (`oel/search/common.py`).
- `oel/experiments/heuristic_eval.py`: admissibility, consistency, full-map comparison + `heuristic_nodes.png`, ablation. `report/sections/part_b_heuristic.md`: the proof. `tests/test_heuristics.py`.
- UI: the expansion grids for UCS and A*+h_ours on the default plan are recorded (Search tab, side by side).
### How to run it
- `python -m oel.experiments.heuristic_eval` (full run, measures peak memory) or `--quick` (~100 s, part of `run_all.py --quick`).
### Key results / numbers
- **Full map, reserve 0:** UCS 1,775,457 nodes; A*+h_manhattan 1,596,654; A*+h_farthest 686,321; A*+h_mst = A*+h_ours **29,542 (60x fewer than UCS)**, all with cost 329. A*+h_ours + fuel pruning: 2,752 nodes. Greedy+h_ours: 20,617 nodes but cost 485 (not optimal). Reserve 20: UCS 1,326,200 vs A*+h_ours 79,615 (cost 353).
- h_ours(start) = 277 vs the true 329 (84% tight); mean h/h* = 0.91 (small instances), 0.88 (full-map samples).
- **Admissibility:** 0 violations for h_manhattan / h_farthest / h_mst / h_ours (553 checked states); h_manhattan_raw: 2 violations next to tunnels (up to +34); h_ours without tunnel edges: 17/17 full-map states violated (up to +136).
- **Consistency:** h_ours violates it on 15.5% of the 92,171 edges A* generated on the full map (largest 19) -> 4,525 reopenings, still optimal. h_farthest and h_manhattan: 0 violations.
- **Ablation (nodes, reserve 0):** full 29,542; -tunnel edges 19,925 (inadmissible, happened to stay optimal); -hill costs 73,121; -MST (= h_farthest) 686,321; -farthest (= h_mst) 29,542. The MST term does almost all the work.
### Files I created or changed
- New: `oel/search/distance_fields.py`, `oel/experiments/heuristic_eval.py`, `tests/test_heuristics.py`, `report/sections/part_b_heuristic.md`. Changed: `heuristics.py`, `common.py`, `uninformed.py` / `informed.py` (pruning flag), `registry.py`, `run_all.py`, `docs/viva_notes.md`.
### Changes to other people's code (if any)
- None outside Part B.
### Known issues / TODOs
- Next: weighted A* study, IDS vs A* under a memory limit, the 30-seed experiments framework + ablation, the evaluation function for Ali.
- Now that A* is fast: move the fuel-reserve experiment back into `--quick`, and use A*+h_ours for the simulator's full replans. Then do the deliberate live LLM re-run with A*+h_ours exposed (`cfg.llm_algorithms`).
### What the next person needs to know
- Use `astar(problem, heuristic=h_ours)` for anything big; add `prune_dominated=True` for another ~10x.

---

## Turn 2 (session 3): Laiba Rehman (505099), 2026-11-25
### What I built
- **Search additions:**
  - `max_states=` memory cap in `ucs` and `astar` (reason `"memory_limit"`), plus `stats["stored_states"]`;
  - `weighted_astar` now passes `prune_dominated` / `max_states` through;
  - **IDA\*** (`ida_star` in `informed.py`: f-limit iterative deepening with the same on-path cycle check as DLS and total node/time budgets).
- **Registry:**
  - `astar_pruned` and `ida_star` registered;
  - `DEFAULT_PLANNER` / `default_planner` = A* + h_ours + fuel pruning;
  - the ablation heuristics (`h_ours_no_tunnels`, `h_ours_no_hills`) moved from `heuristic_eval.py` into `heuristics.py`, plus `ALL_HEURISTICS` (name -> h).
- **Experiment framework** `oel/experiments/framework.py` (for Ali and Rayyan too):
  - `make_scenarios(n=30, vary_start=False)`: our map with the 5 stops re-drawn, seeded from BASE_SEED + 5000 + i, feasible with reserve 20;
  - `Variant(label, planner, heuristic, options, slow)`;
  - `run_experiment(variants, n, name)` -> tidy DataFrame (4 processes, row cache in `oel/experiments/cache/`);
  - `summarise()` / `readable()` -> mean [95% bootstrap CI];
  - `run_cached(jobs, name)` for your own (config, variant) jobs.
- `oel/experiments/routes.py` (route facts, differing segments); `plots.plot_route_comparison`.
- **Experiments:**
  - `weighted_astar.py` (w = 1..5 + h_manhattan_raw, pruning off/on, reserve 0/20);
  - `memory_limit.py` (A*/UCS caps vs IDS vs IDA* on 30 small + 30 medium instances);
  - `heuristic_scenarios.py` (main comparison + ablation over 30 scenarios, failure analysis).
- **Default planner everywhere:** run_all demo, simulator full replans (`standin_demo`, `fuel_reserve`, `ui/app.py`), UI preselection. Rejoin stays UCS.
- **Fuel-reserve experiment back in `--quick`,** with the full 30 seeds.
- `tests/test_weighted_memory.py` (21 tests).
- Report: `report/sections/part_b_weighted.md`, `part_b_memory.md`, `part_b_failures.md`.
- Viva notes: session-3 block in Part B.
### How to run it
- `python run_all.py --quick`: **133 s**. A live change that recomputes everything (`--quick --no-hills`): **231 s**.
- Alone:
  - `python -m oel.experiments.weighted_astar` (~35 s uncached);
  - `python -m oel.experiments.memory_limit` (~30 s uncached);
  - `python -m oel.experiments.heuristic_scenarios` (full: ~10 min on 4 processes; `--quick`: fast variants only);
  - `python -m oel.experiments.fuel_reserve` (~40 s).
- **Full-mode only:** the slow scenario variants (UCS, A*+h_manhattan, A*+h_farthest over 30 scenarios x 2 reserves), peak-memory measurement in `heuristic_eval`, and fault-injection recomputation. Their cached rows are reused by `--quick`.
- `pytest -q`: **105 passed** (73 s).
### Key results / numbers
- **Weighted A\*** (full map; every run within cost <= w x optimum):
  - w = 1.2 saves 47-57% of the nodes for +2.3-2.4% cost (reserve 20: 34,454 vs 79,615 nodes, 361 vs 353).
  - Bigger w is not monotonically faster: reserve 20, w = 5 expanded 66,563 nodes for 494 (+40%). It went for stop 3 first and recharged at the depot 3 times.
  - h_manhattan_raw (inadmissible): 1.58M nodes and optimal by luck.
- **Memory** (medium = 15x15, fuel on):
  - A* + h_ours solves 10 / 47 / 80 / 100% with caps 25 / 100 / 1,000 / none (needs ~550 states on average); UCS needs ~4,000.
  - IDS: ~13 states, 27% solved within 500k nodes, ~200 expansions per state, optimal in 57-62% of its solved runs.
  - IDA*: ~18 states, 80% solved, always optimal, 102,900 nodes (small instances: 95 vs IDS 35,840).
- **30 scenarios** (reserve 0):
  - Mean nodes: UCS 1,476,045; A*+h_ours 43,974 (34x fewer; median per scenario 73x); + pruning 3,586 (~410x). All optimal, no limit hits.
  - Greedy is never optimal (+54% mean, +131% worst).
  - **Ablation:** without tunnel edges h_ours is non-optimal in 15/30 scenarios (up to +53%); on the default map this was hidden.
- **Hardness:** nodes correlate with optimal cost (rho 0.82), h tightness (-0.69), mud (0.61), climbing (0.56) and recharges (0.49); not with tunnels (0.13).
- **Pipeline:**
  - Fuel-reserve experiment ~28 min -> 40 s.
  - Its win rates changed with A* replans (equal-cost but different plans): 20 / 33 / 53 / 57 / 47% for reserve 0 / 5 / 10 / 15 / 20 (was 13 / 47 / 47 / 53 / 63%). The rule now picks 15, but the CIs of 10 / 15 / 20 overlap (~30-73%).
  - Default simulation (seed 952097431, reserve 20) is now a **loss (stranded)** at real cost 785 after 321 steps and 92 slips (with UCS it was a win, 877).
### Files I created or changed
- New:
  - `oel/experiments/{framework,routes,weighted_astar,memory_limit,heuristic_scenarios}.py`, `oel/experiments/cache/*.json`;
  - `tests/test_weighted_memory.py`;
  - `report/sections/part_b_{weighted,memory,failures}.md`;
  - new tables and figures (`weighted_astar*`, `memory_limit*`, `scenarios_*`).
- Changed:
  - `oel/search/{informed,uninformed,heuristics,registry}.py`;
  - `oel/experiments/{heuristic_eval,small_instances,standin_demo,fuel_reserve}.py`;
  - `oel/world/plots.py`, `ui/app.py`, `run_all.py`, `CLAUDE.md`, `docs/viva_notes.md`.
### Changes to other people's code (if any)
- `oel/world/plots.py` (Arsal): **added** `plot_route_comparison` (nothing existing changed).
- `oel/experiments/standin_demo.py`, `oel/experiments/fuel_reserve.py`, `ui/app.py` (Arsal): full replans and the demo plan use `default_planner`; rejoin stays `ucs`. Also:
  - `fuel_reserve.SEEDS_QUICK` 10 -> 30, so `--quick` no longer overwrites the 30-seed table with a 10-seed one;
  - the UI preselects `astar_pruned` + `h_ours`, and its time estimate was updated.
- `run_all.py`: fuel reserve runs in `--quick` again; the three new Part B experiments were added.
- **NOT changed:**
  - `oel/llm/` (Part D still plans/simulates with `ucs`, so the cached conversations and sims replay exactly; `cfg.llm_algorithms` is still `("ucs",)`);
  - `cfg.fuel_reserve` (still 20; see TODO).
### Known issues / TODOs
- **Decision for the group: the default fuel reserve.** With A* replans, 30 seeds can't separate 10 / 15 / 20 (overlapping CIs); the rule picks 15. Changing `cfg.fuel_reserve` changes plan ids, so the Part D caches would need a live re-run. Options: keep 20 and explain, or more seeds (e.g. 100, ~2 min now) before deciding.
- The deliberate live LLM re-run exposing `astar_pruned` (widen `cfg.llm_algorithms`) still needs a Groq key.
- Still in my turn: the evaluation function for Ali's rival game.
- IDA* still re-expands states ~150x on medium instances (transpositions); a transposition table would fix that, but it is no longer "memory = one path".
- The project's `venv/` folder is empty. This session ran on the global Python after `pip install -r requirements.txt`.
### What the next person needs to know
- **Ali:** use `framework.run_cached(jobs, "your_name")` or `run_experiment` for your tournament sweeps (caching + parallel + CIs), and `stats.wilson_ci` for W/D/L. A rival policy can plan with `registry.default_planner` (about 0.1 s on the full map).
- Cached rows are keyed by the planning config, so live changes are recomputed automatically. If you change a planner's behaviour, bump `framework.FRAMEWORK_VERSION`.
