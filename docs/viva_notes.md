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

## Part A: Environment, PEAS, cost map

## Part B: Search planners and heuristic

## Part C: Adversarial search (rival blocker)

## Part D: LLM dispatcher

## Part E: UI and experiments

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
