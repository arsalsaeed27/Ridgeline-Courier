_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part B: 30-scenario comparison, ablation and failure analysis (draft)

## Why scenarios
Session 2 compared the heuristics on **one** map: our instance with its 5 fixed stops. A single map can mislead, and the ablation below shows it did once. So the framework (`oel/experiments/framework.py`) draws **30 scenarios**. Each one is our real map with the 5 stops re-drawn:
- on free cells reachable from the depot;
- not on a station, a tunnel end or the start;
- seeded from BASE_SEED + 5000 + i;
- redrawn if no plan exists with the default planning reserve of 20.

Every twist stays on. Each (scenario, planner) run is one row of a tidy table. Means come with 95% percentile-bootstrap CIs, and solved % with Wilson CIs. The optimum of each scenario comes from A\* + h_ours + fuel pruning, which is proven optimal and tested against UCS (UCS agreed on all 60 scenario × reserve runs).

Outputs:
- `results/tables/scenarios_{comparison,ablation,hardest,greedy_worst,runs}`;
- `results/figures/scenarios_{comparison,ablation,hardness,greedy_worst,hardest_route}.png`.

## Main comparison (30 scenarios; mean nodes [95% CI])

| planner | reserve 0 | reserve 20 | optimal |
|---|---:|---:|---:|
| UCS | 1,476,045 [1,326,100, 1,621,724] | 1,111,169 [993,532, 1,229,734] | 30/30 |
| A\* + h_manhattan | 1,298,434 | 991,168 | 30/30 |
| A\* + h_farthest | 474,154 | 430,765 | 30/30 |
| A\* + h_mst | 44,037 | 87,611 | 30/30 |
| **A\* + h_ours** | **43,974 [27,024, 62,856]** | **87,454 [54,046, 125,953]** | 30/30 |
| Greedy + h_ours | 18,847 | 17,705 | **0/30** (+54.5% [43.6, 66.3] on average) |
| A\* + h_ours + fuel pruning | 3,586 [2,278, 5,042] | 7,539 [4,664, 10,836] | 30/30 |

- **The session-2 result generalises.** The order of the heuristics is the same on every scenario set.
  - A\* + h_ours expands **34× fewer nodes than UCS** on average (ratio of the means). The per-scenario ratio has a median of **73×** and ranges from 10× to 2,507×.
  - With fuel pruning on top it is **~410× fewer** (median ratio per scenario: 725×).
  - Our default map (29,542 nodes) is an easier-than-average scenario for h_ours.
- **The MST term does the work; the farthest term rarely matters.** h_mst and h_ours differ by 0.1%: the farthest stop beats the MST in only a few states.
- **No budget or memory limit was hit.** UCS and A\* had a cap of 4M stored states. The largest UCS run expanded 2.26M nodes (scenario 18).

## Ablation over 30 scenarios (reserve 0)

| variant | nodes (mean [95% CI]) | optimal | mean gap % (max) | h(start)/optimal |
|---|---:|---:|---:|---:|
| h_ours (full) | 43,974 [27,024, 62,856] | 30/30 | 0 | 0.83 |
| − tunnel edges | 31,378 [19,811, 45,422] | **15/30** | **7.2 (53.4)** | **1.07** |
| − hill costs | 79,837 [51,561, 110,949] | 30/30 | 0 | 0.77 |
| − MST term (= h_farthest) | 474,154 [372,876, 578,221] | 30/30 | 0 | 0.36 |
| − farthest term (= h_mst) | 44,037 [27,086, 62,910] | 30/30 | 0 | 0.83 |

**The important correction to session 2.** On the default map, h_ours without tunnel edges "happened to stay optimal" (cost 329). Over 30 scenarios it returns a **non-optimal route in 15 of 30**, up to **53% too expensive**. Its h(start) is above the optimum on average (1.07). It is *faster* (31k vs 44k nodes) only because it overestimates: a fast, wrong heuristic. This is why the admissibility proof needs the tunnel edges in the relaxed distance fields.

Removing the hill costs keeps h admissible but looser (0.77 vs 0.83 tight), so it needs 82% more nodes. That shows the twist-aware relaxation pays off.

## Failure analysis

### 1. What makes a scenario hard for A\* + h_ours?
Spearman rank correlation of A\* + h_ours nodes with each feature of the optimal route (30 scenarios; see `scenarios_hardness.png`):

| feature | rho | p |
|---|---:|---:|
| optimal cost (longer tours) | +0.82 | < 0.001 |
| h(start) / optimal (how tight h is) | **−0.69** | < 0.001 |
| mud cells on the route | +0.61 | < 0.001 |
| height climbed | +0.56 | 0.001 |
| recharges | +0.49 | 0.006 |
| ford cells | +0.44 | 0.015 |
| tunnel jumps | +0.13 | 0.50 (no effect) |

In words: a scenario is hard when the **true route is long and expensive in ways the heuristic cannot see**.
- **Fuel.** Every recharge is a detour to a station that h ignores. All six scenarios above 100k nodes need 1–2 recharges, and the one scenario with **0** recharges is among the easiest (2.7k nodes).
- **Expensive terrain and climbs.** h_ours *does* include these, through the relaxed distances. But a route forced through mud or uphill by the fuel limit costs more than the relaxed shortest path, which may use other, cheaper terrain. The gap h\* − h grows, and A\* has to raise f past every cheaper-looking alternative before it believes the expensive route.
- **Tunnels make no difference.** h_ours already models them exactly (rho 0.13, not significant).

**Hardest scenario: 19.** Stops at (38,2), (28,7), (29,28), (4,25) and (33,38) are spread over three corners. The optimal cost is 468 (the most expensive of the 30). The route crosses 30 mud and 7 ford cells, climbs 16 units, recharges twice and uses one tunnel jump.
- A\* + h_ours: 179,899 nodes and 13,528 reopenings.
- With pruning: 12,339 nodes.
- UCS: 1,848,469 nodes.
- h(start)/optimal = 0.80.

Figure: `scenarios_hardest_route.png`.

### 2. Where reopenings happen
h_ours is not consistent (session 2: 15.5% of edges), so A\* reopens states in **29 of 30 scenarios** (median 1,887, max 19,023 in scenario 18). Reopenings are highest in the hard scenarios: the same long, fuel-constrained routes where h jumps when a stop is delivered and the MST shrinks. Fuel pruning removes almost all of them (mean 37 instead of 3,708), because most reopened states are fuel variants of one cell. The cost stays optimal in every scenario.

### 3. Where greedy goes badly wrong
Greedy + h_ours is never optimal. It is 14% to 131% worse (median 52%), and it doesn't even save much work: 18.8k nodes against 3.6k for pruned A\*.

**Worst case: scenario 16** (+131%: 395 instead of 171), figure `scenarios_greedy_worst.png`.
- **The optimal route** delivers the three stops near the depot first (4, 1, 0). It then takes tunnel 2 from (19,6) south to (38,12) and finishes with stops 3 and 2: 64 moves, 1 recharge.
- **Greedy delivers 4, then 0, then 3,** skipping stop 1 (10,8), which is right next to stop 4. Greedy only looks at h, never at the cost already paid, so it follows whichever state *looks* closest at each moment and returns the first goal it reaches.
- **Then it has to come back for stop 1:** a 39-cell walk from (28,26) back north to (9,9).
- **Next it recharges at the depot and jumps through tunnel 1** (4,2)→(10,36), then walks 28 cells south to stop 2.
- In total: 133 moves, 2 recharges, 8 ford and 25 mud cells.

### 4. Limits hit
None. All 30 × 7 × 2 main runs and 30 × 5 ablation runs finished within their caps.

## Design decisions
- **The scenarios re-draw only the stops,** so every scenario keeps our map, terrain, hills, stations and tunnels. `vary_start=True` also moves the depot, for anyone who needs it.
- **Feasibility is checked with reserve 20,** so the same 30 scenarios serve reserve 0 and reserve 20 and the two columns are paired.
- **Slow variants run in full mode only.** UCS, A\* + h_manhattan and A\* + h_farthest take about 10 min on 4 processes; `--quick` reads them from the cache. Every row is cached under a hash of (scenario, planner settings, planning config), so reruns are instant and a live change recomputes.
