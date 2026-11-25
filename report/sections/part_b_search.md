_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part B: the six search algorithms (draft)

## The search problem
- **State:** (row, col, delivered_mask, fuel). The goal is all five bits set; we don't have to return to the depot.
- **Actions:** N/S/E/W into a free cell, and TUNNEL on a tunnel end.
- **Step cost:** the terrain of the cell entered (road 1, grass 3, mud 5, ford 9) plus 2 per level climbed. A tunnel jump costs 2.
- **Fuel:** a move is legal only if the tank stays ≥ the planning reserve. Stations and the depot refill the tank; downhill moves give fuel back.

Every planner uses only the `DeliveryProblem` interface, so constraints, the fuel reserve and replanning from mid-route work without extra code. All six are written from scratch (`oel/search/uninformed.py`, `informed.py`).

| algorithm | frontier / order | goal test | memory | optimal here? |
|---|---|---|---|---|
| BFS | FIFO queue, visited set | when a state is **generated** | all generated states | fewest **moves**, not cheapest |
| UCS | priority queue on g | when **popped** | all generated states | yes (cheapest cost) |
| DLS | recursion to a depth limit | on visit | the current path (on-path set) | no |
| IDS | DLS with limits 0, 1, 2, … | on visit | the current path | fewest moves |
| Greedy | priority queue on h | when popped | all generated states | no |
| A\* | priority queue on g + h (ties to larger g), reopening | when popped | all generated states | yes (admissible h) |

## Design decisions
- **When the goal is tested.**
  - BFS tests on *generation*: every state at depth d is generated before any at depth d+1, so the first goal generated already has the fewest moves, and a whole layer of expansions is saved.
  - UCS and A\* must test on *pop*: only then is g guaranteed minimal. Testing on push could return a costlier path.
- **DLS cycle check without a visited set.** A state is added to the on-path set when the search goes down and removed when it backtracks. That stops loops but not revisits through other branches.
- **DLS reports "cutoff" vs "failure".** Cutoff means some branch reached the limit, so a deeper solution may exist. Failure means everything reachable was explored, so there is no solution at any depth. Budgets give `node_limit` or `time_limit`.
- **A\* reopening.** h_ours is not consistent, so A\* must re-expand a closed state when it finds a cheaper path to it. We count the reopenings.
- **Ties go to the larger g:** the state further along its path usually reaches the goal sooner.

## Comparison on 30 small instances
To let every algorithm finish, we mask the real map to a 7×7 window around the depot (everything else becomes a wall). Each instance has 1–3 seeded stops, hills on and fuel off. Masking, rather than cropping, keeps the real terrain, heights and coordinates, so the plots and `verify_plan` work unchanged.

Means with 95% percentile-bootstrap CIs; solved % with Wilson CIs (`results/tables/search_uninformed_small`):

| algorithm | solved | nodes | max frontier | cost ÷ optimal |
|---|---:|---:|---:|---:|
| BFS | 30/30 | 70 [49, 92] | 13.4 | 1.070 [1.034, 1.110] |
| UCS | 30/30 | 74 [53, 95] | 14.7 | 1.000 |
| DLS (limit d\*) | 30/30 | 5,381 [857, 11,668] | 10.9 | 1.070 |
| DLS (limit d\* − 1) | 0/30 (all "cutoff", as required) | 11,173 | 9.9 | – |
| IDS | 30/30 | 35,840 [7,426, 71,549] | 10.9 | 1.070 |
| Greedy (h = 0) | 30/30 | 79 [57, 101] | 14.1 | 1.070 |
| A\* (h = 0) | 30/30 | 74 [53, 95] | 14.7 | 1.000 |

Every returned plan passes `verify_plan`, an independent replay.

What it shows:
- **Fewest moves ≠ cheapest.** BFS, DLS and IDS cost 7% more than the optimum on average (CI 3–11%), because terrain costs 1–9 per move.
- **UCS and A\* are always optimal.** With h = 0, A\* orders states exactly like UCS (same 74 nodes). The heuristics in `part_b_heuristic.md` change that.
- **The price of little memory is repeated work.** IDS stores at most about 11 states but expands about 500× more nodes than BFS, because every iteration redoes the shallower ones and different branches reach the same states.
- **With fuel on, or a 9×9 window, IDS runs out of its 500k-node budget** on 5–6 of 30 instances. Fuel makes "the same cell" a new state, so the on-path check rarely prunes. That's why this table uses fuel off. The memory study (`part_b_memory.md`) takes this further with IDA\*.

## On the full map (all twists, reserve 0)
UCS finds the optimum 329 (307 with hills off) after 1,775,457 expansions. A\* with our heuristic h_ours needs 29,542 (60× fewer), and with fuel-dominance pruning 2,752 (645× fewer), at the same cost. See `part_b_heuristic.md`; over 30 re-drawn scenarios, see `part_b_failures.md`.
