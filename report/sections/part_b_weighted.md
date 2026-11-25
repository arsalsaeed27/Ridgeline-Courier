_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part B: weighted and inadmissible A* (draft)

## What we ran
Full map, all twists on (hills, fuel, tunnels), planning reserve 0 (optimum 329) and 20 (optimum 353).
- **Weighted A\***: f = g + w·h_ours with w ∈ {1, 1.2, 1.5, 2, 3, 5}.
- **Inadmissible A\***: plain A\* with h_manhattan_raw (Manhattan distance to the nearest stop, ignoring tunnels).

Each variant ran **without** fuel-dominance pruning, so the effect of w is clear, and **with** it, which is the practical setting.
Code: `oel/experiments/weighted_astar.py`. Outputs:
- Table: `results/tables/weighted_astar`.
- Figures: `results/figures/weighted_astar_pareto.png` (nodes vs cost gap), `weighted_astar_route.png` and `weighted_astar_route_worst.png`.
- Route facts: `weighted_astar_case*`.

## The guarantee
With an admissible h, weighted A\* returns a cost **≤ w × optimum**. While the optimal path is unfinished, some state n on it waits in the frontier with its optimal g. So f(n) = g(n) + w·h(n) ≤ w·(g(n) + h(n)) ≤ w·C\*. The goal is popped before n, and h = 0 at a goal, so its cost is ≤ f(n) ≤ w·C\*.

Reopening and fuel pruning keep this true. A pruned state is replaced by one at the same cell that is at least as cheap and has at least as much fuel. Since our heuristics ignore fuel, that replacement has the same h. **All 24 weighted runs satisfied the bound** (column `cost_le_w_opt`). The tests also check it on 20 small instances for 5 weights, with pruning on and off.

## Results (nodes expanded; pruning off / on)

| reserve | variant | cost | gap % | nodes (off) | nodes (on) |
|---:|---|---:|---:|---:|---:|
| 0 | w = 1 (A\*) | 329 | 0 | 29,542 | 2,752 |
| 0 | w = 1.2 | 337 | 2.4 | 15,562 | 1,528 |
| 0 | w = 1.5 | 337 | 2.4 | 25,394 | 2,249 |
| 0 | w = 2 | 390 | 18.5 | 24,192 | 1,657 |
| 0 | w = 3 | 372 | 13.1 | 14,427 | 857 |
| 0 | w = 5 | 392 | 19.1 | 25,229 | 1,107 |
| 0 | h_manhattan_raw | 329 | 0 | 1,583,930 | 86,558 |
| 20 | w = 1 (A\*) | 353 | 0 | 79,615 | 7,007 |
| 20 | w = 1.2 | 361 | 2.3 | 34,454 | 2,965 |
| 20 | w = 1.5 | 371 | 5.1 | 24,653 | 2,095 |
| 20 | w = 2 | 375 | 6.2 | 36,007 | 2,999 |
| 20 | w = 3 | 478 | 35.4 | 54,796 | 3,547 |
| 20 | w = 5 | 494 | 39.9 | 66,563 | 4,669 |
| 20 | h_manhattan_raw | 353 | 0 | 1,182,416 | 75,710 |

What the table shows:
1. **A small weight buys most of the speed.** At w = 1.2, A\* expands 47% fewer nodes (reserve 0) or 57% fewer (reserve 20) for a route only 2.3–2.4% more expensive.
2. **More weight is not monotonically faster.** w = 1.5 expands more nodes than w = 1.2 at reserve 0. At reserve 20, w = 3 and w = 5 expand *more* nodes than w = 1.2 while returning routes 35–40% worse.
   The reason is that our h ignores fuel. A heavy weight pushes the search straight at the stops. Those routes then run short of fuel, and A\* has to explore many detours to stations. It also reopens more: 34,127 reopenings at w = 5 vs 11,456 at w = 1, because h_ours is not consistent and weighting makes that worse.
   **The bound w·C\* is a worst-case guarantee, not a prediction.** At w = 5 the bound allows 1,765, and we got 494.
3. **Inadmissible ≠ fast.** h_manhattan_raw overestimates only next to the tunnel entrances (by up to 34, session 2). Everywhere else it is a weak bound (Manhattan × 1). So it expands 54× more nodes than h_ours at reserve 0. It still returned the optimum here, but nothing guarantees that.
4. **Fuel pruning and weighting stack.** With pruning on, every variant needs 10–23× fewer nodes. The costs are identical, because pruning never changes the result of a run.

## The clearest "faster but worse" case: reserve 20, w = 1.2 (pruning off)
- **Work:** 34,454 nodes instead of 79,615 (**57% fewer**), 0.76 s instead of 1.68 s.
- **Route:** cost **361 instead of 353 (+2.3%)**. The delivery order (4-1-3-2-0), the recharge stops (depot, (23,11), (31,20)) and both tunnel jumps are the same.
- **Where they differ:** one stretch on the way to the station at (31,20). The optimal route goes south along column 20, from (23,20) to (27,20) (7 cells). The weighted route takes column 21–22, from (22,21) to (27,22) (9 cells), which is two moves longer and 8 more cost.

This is the typical behaviour of a small weight: the same plan, with a locally greedier corridor. See `weighted_astar_route.png`.

## The most expensive case: reserve 20, w = 5
- **Work:** 66,563 nodes (only 16% fewer than A\*).
- **Route:** cost **494 (+39.9%)**, 205 moves instead of 147.
- **Where they differ:** trusting h five times more than g, the search heads for stop 3 first (order 3-1-4-2-0 instead of 4-1-3-2-0). That leaves the tank too low, so the route **returns to the depot to recharge three times** (instead of once at the depot and twice at stations) and makes 3 tunnel jumps instead of 2.
  The cells only on the weighted route (circled in `weighted_astar_route_worst.png`) form three pieces:
  - a 13-cell trip from (8,8) back to the depot at (5,3);
  - a 6-cell loop between (9,10) and (11,13), driven once in each direction;
  - a 20-cell run from the depot south to the tunnel end (19,6), which it jumps through to (38,12) next to stop 2.

This shows why weighted A\* is risky on our map: h knows nothing about fuel, so over-trusting it causes exactly the detours h cannot see.

## Design decisions
- The Pareto plot uses **log x** (nodes span 857 to 1.6M) and one panel per reserve, with no dual axis.
- **Which case to describe** was chosen by a fixed rule (the largest share of nodes saved per % of extra cost), not by eye.
- Runs are cached (`oel/experiments/cache/weighted_astar.json`). A live change (e.g. `--no-hills`) gives new cache keys and recomputes in about 35 s.
