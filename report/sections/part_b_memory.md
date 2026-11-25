_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part B: search under a memory limit (A\* vs IDS vs IDA\*) (draft)

## Question
A\* is fast, but it keeps **every state it has generated** (frontier + expanded). What happens if the planner may only hold a fixed number of states, and what can we use instead?

## Setup
- **A\* + h_ours and UCS with a memory cap** (`max_states`). If frontier + expanded states go above the cap, the search stops with reason `memory_limit`. Caps: 25, 50, 100, 250, 1,000 and 10,000 states, plus no cap.
  - The caps are small because h_ours is so accurate on these windows that A\* never needs more than a few hundred states on average. Caps of 10k and more never bite.
- **IDS**: depth-first with depth limits 0, 1, 2, …. It stores only the current path.
- **IDA\* + h_ours** (new, `oel/search/informed.py: ida_star`): depth-first with an **f = g + h** limit. The first limit is h(start). Each new limit is the smallest f that went over the previous one. It also stores only the current path.
- IDS and IDA\* get the **same budget**: 500,000 expanded nodes or 20 s in total.
- **Instances** (our real map masked to a window around the depot):
  - *small*: 30 instances, 7×7 window, 1–3 stops, fuel off (the session-1 set);
  - *medium*: 30 instances, 15×15 window, 2–3 stops, fuel on with a tank of 30.
- **Measured:**
  - solved % (Wilson 95% CI);
  - whether the cost is optimal (A\* without a cap gives the optimum);
  - nodes expanded and **distinct** states expanded (counted by a wrapper that is only for measurement), so nodes ÷ distinct = how often each state was expanded;
  - peak stored states (A\*/UCS: every generated state; IDS/IDA\*: the longest path);
  - runtime.

All means come with 95% bootstrap CIs.
Code: `oel/experiments/memory_limit.py`. Outputs: `results/tables/memory_limit{,_runs}` and `results/figures/memory_limit.png`.

## Results (means)

| set | algorithm | solved % | optimal % of solved | peak stored states | nodes expanded | expansions per state |
|---|---|---:|---:|---:|---:|---:|
| small | A\* (no cap) | 100 | 100 | 28 | 16 | 1.0 |
| small | A\* (cap 25 / 50) | 53 / 83 | 100 | ≤ cap | 10 / 15 | 1.0 |
| small | UCS (no cap) | 100 | 100 | 83 | 73 | 1.0 |
| small | IDS | 100 | 57 | **11** | **35,840** | 240 |
| small | IDA\* | 100 | 100 | **11** | **95** | 3.1 |
| medium | A\* (no cap) | 100 | 100 | 550 | 386 | 1.0 |
| medium | A\* (cap 25 / 100 / 250 / 1,000) | 10 / 47 / 73 / 80 | 100 | ≤ cap | 10 / 30 / 60 / 168 | 1.0 |
| medium | UCS (no cap) | 100 | 100 | 3,999 | 3,587 | 1.0 |
| medium | UCS (cap 100 / 1,000 / 10,000) | 0 / 17 / 93 | 100 | ≤ cap | 43 / 591 / 3,579 | 1.0 |
| medium | IDS | **27** (22 runs hit the node budget) | 62 | **13** | 374,797 | 197 |
| medium | IDA\* | **80** (6 hit the node budget) | 100 | **18** | 102,900 | 148 |

## What it shows
1. **A\* fails below a memory cap.** On medium instances A\* solves 10% with 25 states, 47% with 100, 80% with 1,000, and 100% when it may hold about 550 on average. It never returns a wrong answer: it either finds the optimum or stops with `memory_limit`.
2. **A better heuristic also means less memory.** UCS needs 7× more stored states than A\* (3,999 vs 550 on medium), so the same caps hurt it much earlier. With a cap of 1,000 states UCS solves 17% of the medium instances and A\* 80%.
3. **IDS never runs out of memory, but it repeats work.**
   - It holds only one path: 11–13 states.
   - It expands each distinct state about 200 times on average. Every iteration starts again from the depot, and different branches keep reaching the same states.
   - On medium instances (fuel on) it hits the 500k-node budget in 22 of 30 runs.
   - When it does finish, it finds the fewest moves, which is the cheapest route only 57–62% of the time.
4. **IDA\* fixes most of this.**
   - Memory is the same as IDS (11–18 states).
   - On small instances it needs **95 nodes instead of 35,840**, about 380× fewer.
   - On medium instances it solves 80% instead of 27%, with about 3.6× fewer nodes.
   - Every answer is optimal: h_ours is admissible, and IDA\* only needs admissibility, not consistency.
5. **The honest limit of IDA\*.** On medium instances IDA\* still expands each state about 148 times, and 6 of 30 runs hit the budget. Like IDS, it only checks the *current path* for repeats. A grid has a huge number of different paths to the same (cell, mask, fuel) state, so these transpositions are re-searched in every branch and every iteration. That repeated work is the price of storing one path instead of every state. Where memory allows, A\* is still far faster (386 nodes vs 102,900).

## Design decisions
- **Memory is counted in states, not bytes.** It is exact, it doesn't depend on Python's allocator, and it is what the cap limits.
- **"Peak stored" for IDS/IDA\* is the longest path held at once.** The on-path set is the only structure they keep.
- **The distinct-state counter is outside the algorithms** (it wraps `successors`). It costs memory but is not counted, because it is only there to measure the re-expansions.
- **The medium set keeps fuel on.** That is our real problem, and it is exactly where the repeated work of IDS/IDA\* explodes: a different fuel level makes "the same cell" a new state.
