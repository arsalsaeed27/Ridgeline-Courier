_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part B: our heuristic h_ours and its admissibility (draft)

## Definition
For each stop i, **D_i(x)** is the cheapest cost from cell x to stop i in the **relaxed problem**:
the same walls, terrain costs, uphill costs (`UP_COST · max(dh, 0)`) and tunnel edges (cost
`tunnel_cost`) as the real problem, the same avoided cells/terrain from the user's constraints,
but **no fuel limit**. It is computed by our own Dijkstra run **backwards** from stop i over
reversed edges (one run per stop). Hills make moves direction-dependent, so the backward run is
what gives the cost *to* the stop.

For a state s = (x, mask, fuel) with undelivered stops U:

- **h_farthest(s)** = max over i in U of D_i(x)
- **h_mst(s)** = the weight of a minimum spanning tree on the nodes {x} ∪ U, with edge weights
  w(x, j) = D_j(x) and w(i, j) = min(D_j(stop_i), D_i(stop_j)) (Prim's algorithm, at most 6 nodes)
- **h_ours(s)** = max(h_mst(s), h_farthest(s)); h(s) = 0 when U is empty.

**Worked example (start state, depot (5,4), all five stops undelivered, hills on).**
D_j(depot) = 113, 59, 79, 58, 14 for stops 0-4. Stop 4 is only 14 away thanks to the tunnel
(4,2)→(10,36). Prim builds: depot→stop 4 (14), depot→stop 3 (58), stop 3→stop 1 (51; the other
direction costs 55 because of the hills), stop 4→stop 2 (75), stop 2→stop 0 (79). The total is
h_mst = 277; h_farthest = 113 (stop 0); **h_ours = 277**, against a true optimal cost of 329
(84% tight).

## Admissibility proof: h_ours(s) ≤ h\*(s) for every state s
Let h\*(s) be the cost of an optimal completion from s (∞ if there is none; then nothing needs
proving).

**(a) D_i is a lower bound.** Every sequence of real moves is also a sequence of moves in the
relaxed problem, with exactly the same step costs (path costs never depend on fuel). The relaxed
problem only *removes* the fuel restriction. So for any real route from x to stop i,
cost ≥ D_i(x), because D_i(x) is the exact minimum over a superset of routes.

**(b) The MST bound.** Take any completion from s and number the undelivered stops in the order
in which they are **delivered**: u_1, u_2, …, u_k. (Under a stop-order constraint the robot may
drive through a stop without delivering it, so we use delivery time, not first visit.) Cut the
completion into segments: x → (delivery of) u_1 → u_2 → … → u_k. The first segment is a real route
from x to stop u_1, so it costs ≥ D_{u_1}(x) = w(x, u_1). Segment m is a real route from stop
u_{m-1} to stop u_m, so it costs ≥ D_{u_m}(stop_{u_{m-1}}) ≥ min(D_{u_m}(stop_{u_{m-1}}),
D_{u_{m-1}}(stop_{u_m})) = w(u_{m-1}, u_m). The segments don't overlap, so the completion costs at
least the sum of these weights. Those k edges form a **path** through all of {x} ∪ U. A path is a
spanning tree, and the minimum spanning tree weighs no more than any spanning tree. So
h\*(s) ≥ (path weight) ≥ h_mst(s).

**(c) The farthest bound.** Any completion must reach every undelivered stop, in particular the
one with the largest D_i(x). By (a) that part alone costs ≥ max_i D_i(x) = h_farthest(s).

**(d) The max of admissible heuristics is admissible.** Both terms are ≤ h\*(s), so their maximum
is too.

**(e) Fuel, stop order, the reserve and replanning don't break it.** The fuel limit, the planning
fuel reserve and a stop-order constraint only make fewer real routes legal, or force longer ones;
the bounds in (a)–(c) hold for every legal completion, so they still hold. Avoided cells/terrain
are walls in the relaxed problem too, which is fine because a legal completion never enters them.
The rival's cell during replanning is *not* a wall in the fields: fewer walls means smaller
D values, so the bound only gets looser, never wrong.

## Consistency: h_ours may not be consistent, and that is fine
Consistency requires h(s) ≤ c(s, s') + h(s') on every edge. It can fail for h_ours. Delivering a
stop removes a node from the MST, and moving the root can re-shape the whole tree, so h can drop by
more than the step's cost (for example, when the move that delivers a stop makes a long tree edge
disappear). Measured on every edge A\* generated: **15.5% of 92,171 edges on the full map
(largest violation 19)** and 7.0% on the small fuel-ON instances. h_farthest and h_manhattan had
0 violations.

An inconsistent but admissible heuristic still gives optimal A\* **provided A\* reopens a closed
state when it finds a cheaper path to it**. Our A\* does this and counts it: 4,525 reopenings on
the full map (reserve 0). It still expanded only 29,542 states against UCS's 1,775,457 (60× fewer),
with the same optimal cost 329.

## Empirical checks (results/tables/heuristic_admissibility, heuristic_consistency)
- **0 admissibility violations** for h_manhattan, h_farthest, h_mst and h_ours on 30 small
  instances with fuel OFF and 30 with fuel ON (536 sampled states with the true cost from UCS)
  and on full-map states (random walks plus tunnel-side states).
- **h_manhattan_raw** (Manhattan ignoring tunnels) overestimates next to tunnel entrances: at
  (5,2) with only stop 4 left it says 42, while the true cost through the tunnel is 8 (2 of 17
  full-map states violated, by up to 34).
- **Ablation:** removing the tunnel edges from the fields makes h_ours inadmissible (it
  overestimates on all 17 full-map states checked, by up to 136). Removing the hill costs keeps it admissible but weaker (73,121
  nodes instead of 29,542).
