# Viva notes: Ridgeline Courier (instance 38bfda97)

_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

Likely questions with short answers, grouped by part. Every member should be able to answer all of them.

## Shared base (config, stamp, data)

**Q: How is the instance reproducible?**
A: `scripts/oel_instance.py` hashes our sorted CMS IDs with sha256 and seeds `numpy.random.default_rng` with the hash. The twist and elevation scripts seed from `sha256("38bfda97|twists")` and `sha256("38bfda97|elevation")`. `BASE_SEED` in `oel/config.py` comes from the sorted CMS IDs. Every run produces the same files.

**Q: How do you do a live change?**
A: All parameters live in one `Config` object. `parse_cli` applies flags such as `--slip 0.5 --stop 2=14,23 --no-hills` and validates them. For example, a moved stop must be inside the grid, not blocked, reachable from the depot and not on another stop.

**Q: How do you guarantee that every output is stamped?**
A: Figures, tables and logs are only written through `oel/stamp.py`. Figures get the stamp as a suptitle and in their PNG metadata. Tables get it on the first line. Logs get it on the first line. `tests/test_stamp.py` checks every file in `results/`, using `results/manifest.json` and the PNG metadata for images.

**Q: What is the difference between DeliveryProblem and the Simulator?**
A: DeliveryProblem is the perfect, deterministic model that planners search: an action always does the same thing. The Simulator is the real world, with slips (25% of moves turn 90°) and a rival that moves every step. Successful moves in the simulator go through `problem.result()`, so both use the same fuel, hill and tunnel rules and can never disagree.

**Q: Why is fuel part of the state but elevation isn't?**
A: Elevation is fixed for each cell, so `(row, col)` already tells you the height. Fuel depends on the route taken to get there, so two visits to the same cell with different fuel are different situations: one can reach the next station and the other can't.

**Q: Why does UCS test for the goal when it pops a state, not when it pushes it?**
A: When a state is pushed, a cheaper route to it may still be waiting in the queue. When it is popped with the lowest g, every cheaper path has already been expanded, so g is optimal.

**Q: How do you check that the rules are right?**
A: The stand-in UCS reproduces all the reference optima from the brute-force run: 307 (hills off), 400 (no tunnels), 296 (no fuel). With hills on (UP_COST 2, UP_FUEL 3, REGEN 1) the optimum is 329. All reference optima use fuel reserve 0.

**Q: What happens after a slip?**
A: First a *rejoin*: a small UCS within 4 cells, with the rival treated as a wall, looks for the cheapest way back onto the remaining plan. The target state must have the same delivered set and at least `need[k]` fuel, the minimum fuel the rest of the plan needs from that point, computed backwards. More fuel never hurts, so the rest of the plan stays fuel-feasible. If the agent is still on the plan and only the rival is in the way, it *waits* one step. Otherwise it does a *full replan*. Over a run, about 94% of replans are cheap rejoins.

**Q: What does a failed move cost?**
A: The agent stays put and burns no fuel, but it pays 1 (a wasted time step) and the step counts toward the 600-step limit. If it were free, we would underestimate how much slipping costs.

**Q: Why does the agent sometimes get stranded?**
A: The optimal plan uses the tank almost to empty before each recharge, because spare fuel has no value in a perfect world. Slips burn extra fuel, so the agent can end up where no route to a station exists. This is what the no-slip assumption gets wrong: an optimal plan for a perfect world is fragile in a slippery one.

**Q: What is the fuel reserve and why is it 20?**
A: The optimal plan has zero fuel slack, so slips strand it. A reserve trades a little cost for robustness. With a reserve of r, the PLANNER treats a move as legal only if at least r fuel is left after it; refuelling still fills the tank. The simulated world keeps the real limit of 0, so the reserve is a safety margin, not a rule of the world. Replans keep the reserve too, and fall back to the real limit if slips have already pushed the tank below it.
We tested reserves 0, 5, 10, 15 and 20, with 30 seeded runs each (slip 0.25, rival, rejoin/full replanning; `oel/experiments/fuel_reserve.py`):

| reserve | planned cost | wins / 30 | win rate (95% Wilson CI) |
|---|---|---|---|
| 0 | 329 | 4 | 13% (5–30%) |
| 5 | 329 | 14 | 47% (30–64%) |
| 10 | 353 | 14 | 47% (30–64%) |
| 15 | 353 | 16 | 53% (36–70%) |
| 20 | 353 | 19 | 63% (46–78%) |

The rule we fixed in advance: take the smallest reserve with a win rate of at least 80%, or the best one if none reaches it. None did, so we chose 20. Going from 0 to 20 cuts losses from 23 to 9 and raises the planned cost by only 7% (329 → 353). Reserves 5–20 have overlapping CIs, so their order among themselves isn't certain; the clear result is "any reserve beats 0". The remaining non-wins are mostly the placeholder rival parking on a stop (draws), plus a few strandings after slips. The reference optima (307 / 329) are always computed with `--fuel-reserve 0`.

**Q: How are the stops numbered?**
A: From **0 to 4**, everywhere: in the code (stop i = bit i of `delivered_mask`), the figures, the tables, the LLM tools (`get_instance_info` says "Stops are numbered 0-4") and the docs. Stop 0 is (36,32), 1 is (4,10), 2 is (38,7), 3 is (17,14) and 4 is (12,37). So "stop 7" (or "stop 5") does not exist and is an *invalid* request.

## Part A: Environment, PEAS, cost map

## Part B: Search planners and heuristic

**Q: How do BFS, UCS, DLS, IDS, Greedy and A\* differ?**
A: They all walk the same graph (states `(row, col, mask, fuel)`) and differ in which state they expand next:
- **BFS** expands the oldest state (FIFO) and finds the fewest **moves**.
- **UCS** expands the cheapest-so-far state (lowest g) and finds the cheapest **cost**.
- **DLS** goes depth-first down to a limit, storing only the current path.
- **IDS** repeats DLS with limits 0, 1, 2, …: fewest moves like BFS, little memory like DLS.
- **Greedy** expands the state that looks closest (lowest h); fast but not optimal.
- **A\*** expands the lowest g + h; optimal if h never overestimates.

**Q: Why isn't BFS optimal here?**
A: Moves cost 1–9 (road to ford) plus climbing, so the route with the fewest moves isn't the cheapest. On 30 small instances BFS cost 1.07× the optimum on average (95% CI 1.03–1.11), while UCS and A\* were always optimal.

**Q: When is the goal tested, and why does it matter?**
A: BFS tests a state when it's **generated**: every state at depth d is generated before any at depth d+1, so the first goal generated already has the fewest moves, and a whole layer is saved. UCS and A\* must test when a state is **popped**: only then is g guaranteed to be the cheapest, because every cheaper path was popped first. Testing on push could return a costlier path. So node counts aren't measured at exactly the same moment for each algorithm, and the table has a `goal_test` column for that reason.

**Q: What does DLS return, and what is "cutoff" versus "failure"?**
A: DLS returns a solution, *cutoff* or *failure*:
- *cutoff*: some branch reached the depth limit, so a deeper solution might exist; IDS should try a bigger limit.
- *failure*: everything reachable was explored without hitting the limit, so no solution exists at any depth.

On every small instance, DLS with limit d\* (the BFS move count) succeeded, and with d\*−1 it returned cutoff (30/30 each).

**Q: How does DLS avoid loops without a visited set?**
A: It keeps the set of states on the **current path**: a state is added when the search goes down and removed when it backtracks, and states already on the path are skipped. That stops cycles but doesn't stop reaching the same state again along a different path, which is why DLS and IDS repeat work. Mean nodes on the small instances: BFS 70, DLS(d\*) 5,381, IDS 35,840 (including 0-limit to d\* repeats, counted in `stats["re_expansions"]`).

**Q: Why does IDS struggle with fuel ON?**
A: Fuel is part of the state, so returning to a cell with a different fuel level counts as a new state, and the on-path check almost never prunes. With fuel ON (or a 9×9 window), IDS solved only 25/30 (or 24/30) within 500k nodes. The main table therefore uses a 7×7 window with fuel off, where IDS solves 30/30.

**Q: Why does A\* break ties by larger g, and what is a reopening?**
A: Among states with equal f, the one with larger g is further along its path, so it usually reaches the goal sooner without hurting optimality. *Reopening* means finding a cheaper path to an already-expanded state; A\* then pushes it again. That never happens with a consistent heuristic (h_zero reopened 0 times), but our MST heuristic may be inconsistent, so A\* allows it and counts it.

**Q: Why does A\*(h_zero) give exactly the UCS result?**
A: With h = 0, f = g, so A\* orders states exactly like UCS. The tests check UCS == A\*(h_zero) == 307 (hills off) and 329 (hills on). Weighted A\* (f = g + w·h) trades optimality for speed; with an admissible h its cost is at most w × the optimum (checked with w = 2).

**Q: How were the small instances made, and why masking?**
A: We keep the real map but turn every cell outside a 7×7 window around the depot into a wall, and put 1–3 stops on random reachable cells inside (seeded from BASE_SEED + 1000 + i, redrawn if infeasible). Masking keeps the real terrain, heights and coordinates, so `verify_plan`, the plots and the UI work unchanged; cropping would renumber every cell.

**Q: Why bootstrap confidence intervals in the table?**
A: Node counts are very skewed (a few instances need far more nodes), and a t interval for DLS/IDS nodes even went below zero. The percentile bootstrap (resample the 30 values with replacement 10,000 times, seeded, and take the middle 95% of the means) handles skewed data. Solved % uses the Wilson interval.


**Q: What is our heuristic, in one sentence?**
A: h_ours = max(MST, farthest). Using relaxed distances (the real map but with no fuel limit), it takes the weight of a minimum spanning tree that connects the robot's cell to every undelivered stop, or the distance to the farthest undelivered stop if that is larger.

**Q: Worked example?**
A: At the start (depot (5,4), nothing delivered), the relaxed distances to stops 0–4 are 113, 59, 79, 58 and 14 (stop 4 is close thanks to the tunnel (4,2)→(10,36)). Prim picks depot→4 (14), depot→3 (58), 3→1 (51; 1→3 costs 55 because of the hills, and we take the cheaper direction), 4→2 (75) and 2→0 (79): 277. Farthest = 113. h_ours = 277; the true optimum is 329 (84% tight).

**Q: Why is it admissible?**
A: (a) Relaxed distances are lower bounds: every real route is also a relaxed route at the same cost, because fuel only removes routes. (b) Number the stops by when they are *delivered*. The rest of any route splits into segments cell→1st delivery→2nd→…, each costing at least the relaxed distance we used for that edge. Those edges form a path through all the nodes, and a path is a spanning tree, so it weighs at least the MST. (c) You must reach the farthest stop. (d) The max of two lower bounds is a lower bound. (e) Fuel, the reserve, stop order and the rival only remove or lengthen routes.

**Q: Why compute the distance fields backwards?**
A: Hills make A→B ≠ B→A (going up costs extra). We need the cost *from* every cell *to* a stop, so we run Dijkstra from the stop over reversed edges: one run per stop gives the cost-to-stop for all cells at once.

**Q: Why is h_manhattan_raw not admissible, and how did the baseline fix it?**
A: Tunnels jump across the map for cost 2. At (5,2) with only stop 4 left, Manhattan says 42, but the tunnel route costs 8. Our tunnel-aware baseline solves a tiny shortest-path problem over {cell, tunnel ends, stops}, with Manhattan × the cheapest terrain cost for walking and the tunnel cost for jumps. It allows *chains* of tunnels, because a min over a single tunnel could still overestimate when one tunnel drops you next to another.

**Q: Is h_ours consistent? Does it matter?**
A: No. Delivering a stop removes an MST node and can reshape the tree, so h can drop by more than one step's cost. We measured that on 15.5% of the edges A\* generated on the full map (largest gap 19). A\* stays optimal because it reopens a closed state when it finds a cheaper path (4,525 reopenings) and still gives 329.

**Q: How much does it help?**
A: On the full map (reserve 0), A\*+h_ours expands 29,542 states against UCS's 1,775,457 (60× fewer), in 0.3 s instead of 12 s, at the same cost of 329. The baselines help much less: tunnel-aware Manhattan 1.6M, farthest 686k. Greedy+h_ours is even faster but returns cost 485.

**Q: What does the ablation show?**
A: The MST term does almost all the work: without it (= h_farthest) A\* needs 686k nodes, while without the farthest term (= h_mst) the result is unchanged. Without hill costs in the fields it is still admissible but weaker (73k nodes). Without tunnel edges it becomes **inadmissible** (it overestimated on all 17 full-map states checked, by up to 136). It happened to return 329 anyway, but nothing guarantees that.

**Q: What is fuel-dominance pruning, and why is it safe?**
A: At the same (cell, delivered set), a state that arrived no cheaper and with no more fuel than one we've already seen can be dropped. More fuel is never worse in our model: every move legal with less fuel is legal with more, and after any move the fuller tank stays at least as full (the cap and refuelling treat both the same). Costs and deliveries don't depend on fuel. It keeps 307/329 and cuts A\*+h_ours from 29,542 to 2,752 nodes.

## Part C: Adversarial search (rival blocker)

## Part D: LLM dispatcher

**Q: What does the LLM actually do?**
A: It only translates English into tool calls. Our own UCS does the planning, our simulator does the simulating and `fuel_report` reads the fuel and hills along the route. The LLM (Groq `openai/gpt-oss-120b`, temperature 0) runs in our own ReAct loop: Thought (its reasoning), Action (one tool call), Observation (the tool's result or the validator's error), repeated until it writes `RESULT: plan_id=… / infeasible / invalid`. It may make at most 8 tool calls.

**Q: How are constraints like "stop 3 first" put into the search?**
A: Inside the transition rule. Entering a stop only marks it delivered once the stops that must come first are delivered (one bitmask check per stop), so the state stays (row, col, mask, fuel). Avoided terrain and cells become walls, and `max_cost` is checked after planning. `verify_plan` checks a finished plan independently: it replays the moves on the plain map and checks the visited cells, without using the planner's own delivery rule.

**Q: What does the validation layer do?**
A: Before a tool runs it checks the shape (pydantic: the right argument names and types, nothing invented) and the values against our map (the stop exists, the cell is on the grid and not a wall, the terrain is real, the algorithm exists, numbers are in sane ranges, no duplicates). It also detects contradictions, such as avoiding a stop's own cell, which it reports as *infeasible*. If a check fails, the tool doesn't run and the message goes back to the LLM as its Observation.

**Q: How is the LLM graded?**
A: By outcome, not by exact arguments. A plan request succeeds if the LLM's final plan passes `verify_plan` against OUR gold constraints and costs at most 1% more than the direct planner's plan. An infeasible or invalid request succeeds if the LLM says the same word. Comparing arguments with the gold only assigns labels (equivalent_args, invented_argument, ignored_constraint, …).

**Q: Results?**
A: Three Groq models, each with validation OFF and ON:

| model / mode | success (95% Wilson CI) | ambiguous readings | runs lost to API errors | validator rejections |
|---|---|---|---|---|
| gpt-oss-120b OFF / ON | 20/20 (84–100%) | 0 | 0 | 0 |
| gpt-oss-20b OFF / ON | 19/19 (83–100%) | 1 (H1) | 0 | 0 |
| gpt-oss-safeguard-20b OFF / ON | 13/13 (77–100%) | 1 (H1) | 6 | 0 |

The honest summary: **none of the three models needed validation on our 20 requests.** No model produced an argument the validator would reject, so each ON run followed exactly the same conversation as its OFF run. The smaller models differ only on H1 ("the stop closest to the depot first"): 120b reads "closest" as path cost (stop 4, cost 14 via a tunnel, plan 353); both 20B models read it as straight-line distance (stop 1, 7 cells, plan 391, +10.8%). That reading is defensible, so it's reported as `ambiguous_reading`, not as a failure.

**Q: Why only 13 graded runs for safeguard-20b, and why not a smaller model?**
A: Our Groq tier allows safeguard-20b only 2,000 tokens per minute, and one request (system prompt + tool schemas + reply headroom) needs about 2,400. So 6 runs got HTTP 413. That's an account limit, not a model mistake, so those runs are reported separately and not graded. Smaller models from Groq's docs weren't usable with our key: llama-3.1-8b-instant returned 404 and allam-2-7b doesn't support tool calling. So the smallest usable tool-calling models were the 20B ones.

**Q: Then what is the validator for? (fault injection)**
A: We took the 18 gold `plan_route` calls and corrupted each in 10 ways an LLM could get wrong: stop 7, a cell off the grid, a wall cell, the terrain "lava", an unknown algorithm, reserve −5, reserve 500, max_cost −10, a duplicate stop, and avoiding a stop's own cell. That gives 180 calls. The validator caught **100%** before anything ran. Without it: **53 crashes**, **30 silent ignores** (the nonsense was dropped without telling anyone), **15 silent wrong plans** (reserve −5 lets fuel go below 0), **18 wasted searches** (e.g. a 30 s plan only to fail max_cost −10), **39 misleading "infeasible"** answers (e.g. a duplicate stop makes stop 3 wait for itself forever), and 25 correct errors (mostly the contradiction, which our planner also pre-checks). That's 671 s of planning avoided. So the validator protects the tools regardless of how good the model is; with a strong model it's a safety net that rarely fires.

**Q: How is it reproducible without an API key?**
A: Every LLM reply is cached under a hash of (model, temperature, messages, tools), and every plan and simulation under a hash of its inputs. The caches are committed, so `run_all.py` replays the exact runs in seconds; `--live` calls Groq only on a cache miss.


## Part E: UI and experiments

**Q: Does the UI have its own logic?**
A: No. The sidebar widgets are turned into the same command-line arguments `run_all.py` takes and passed to `parse_cli`, so the UI and the report use the same validated `Config`. Plans come from the shared plan cache, simulations from the same `Simulator` and `RejoinReplanner`, and LLM runs from the same agent. The sidebar shows the equivalent command line.

**Q: How does the live change work in the viva?**
A: Either from the CLI (`python run_all.py --quick --slip 0.5 ...`, about 1.5 min, under the 5-minute limit) or in the UI sidebar. Invalid changes, such as moving a stop onto a wall, show an error message instead of crashing (`parse_cli` raises `ValueError`; the UI catches it).

**Q: How does the search visualisation work?**
A: Planners can fill `SearchResult.expanded_order` (the cell of each expanded state, capped at 200,000). The plan cache condenses it into two 40×40 grids: when each cell was first expanded (shown as an animation) and how many states were expanded in it (a log heatmap). Two planners can be shown side by side, e.g. UCS against A*, where A*'s heuristic should focus the expansion towards the goal.

**Q: Why doesn't the UI freeze?**
A: Nothing expensive runs on page load. Planning (25–50 s with the stand-in UCS), recording a search and simulating (10–90 s) only start when you press a button; they show a spinner with a time estimate, and the results are cached (on disk for plans, `st.cache_data` for simulations).

**Q: How is the UI tested?**
A: `tests/test_ui.py` uses Streamlit's AppTest to run the app headlessly: it loads, all 7 tabs render, the stamp is on the page, the slip slider changes the config, an invalid stop shows an error, reset works, and a cached LLM request replays.


## Twists

### Twist 1: Fuel limit with charging stations

### Twist 2: Teleport tunnels

### Twist 3 (ours): Hills with regenerative braking

**Q: Why must REGEN < UP_FUEL?**
A: Climbing k units burns 3k extra fuel and descending k units gives back only k, so every up-and-down loop loses at least 2k fuel. With REGEN ≥ UP_FUEL, bouncing between two cells would create free fuel, the tank limit would mean nothing and the fuel part of the state would no longer be well-founded. `oel/config.py` asserts this.

**Q: How was the elevation map made?**
A: `scripts/make_elevation.py` adds 4–6 Gaussian bumps whose centres, peak heights and widths come from a seeded rng. It rescales the sum to 0..9 and rounds it to integers. Gaussians give smooth hills, so neighbouring cells differ by only a little, which makes sense for a city.

**Q: What changes for the planners?**
A: Moves become direction-dependent, because A→B ≠ B→A. Heuristic distance fields therefore have to be computed backwards over reversed edges. Fuel can also go up without a station, so feasibility checks can't assume fuel only decreases.

**Q: Can the agent move with an empty tank?**
A: Only downhill, when the regen pays for the move. We check the *net* fuel change (`burn + 2·climb − 1·drop`) against the tank. Rolling down one level into a road cell costs 1 − 1 = 0, so it is legal even at 0 fuel, like an electric car coasting. The rule lives in one function, `fuel_after()`, which both the planner and the simulator use.

**Q: How much do the hills change the optimum and the route?**
A: With UP_COST 2, UP_FUEL 3, REGEN 1 the optimum goes from 307 to 329 (+7.2%), but the route stays exactly the same (all 108 cells). The fuel limit and the stations fix the route: the agent has to pass the stations in a particular order, and that corridor happens to be low ground. It climbs only 11 height units in 135 moves, so the cost grows by exactly 2 × 11 = 22. Without the fuel limit (`--no-fuel`) the hills DO change the route: 296 → 320, with 41 different cells. So the hills interact with the fuel twist: on our map, fuel decides the route and the hills decide its price. In the simulator the hills matter more, because a slip uphill costs +3 fuel per level.
