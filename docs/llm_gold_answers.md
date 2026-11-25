_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part D: gold answers for the 20 LLM requests

Written by us, not by the LLM. Costs are the direct (UCS) plans on the gold constraints, with the default planning fuel reserve 20.

| id | tier | request | gold answer | reason |
|---|---|---|---|---|
| E1 | easy | Deliver all five parcels using uniform cost search (ucs). | plan: no constraints -> cost 353 | no constraints; ucs is the named algorithm |
| E2 | easy | Plan the cheapest route that delivers every parcel. | plan: no constraints -> cost 353 | 'cheapest' = the optimal plan, no constraints |
| E3 | easy | I need a route that covers all 5 delivery stops. What does it cost? | plan: no constraints -> cost 353 | no constraints; the answer must state the plan cost |
| E4 | easy | Find a delivery route for all stops, then simulate it with seed 7. Did the robot win? | plan: no constraints -> cost 353 | no constraints; must call simulate (seed 7) on the plan |
| E5 | easy | Use the ucs planner to plan a full delivery run from the depot. | plan: no constraints -> cost 353 | no constraints; the depot is always the start |
| M1 | medium | Deliver stop 3 first, then the others. | plan: stop_order=[3] -> cost 426 | one ordering constraint |
| M2 | medium | Deliver all parcels but never drive through ford (river crossing) cells. | plan: avoid_terrain=['ford'] -> cost 465 | avoid one terrain type; no stop is on ford |
| M3 | medium | Plan a delivery route that does not use any tunnels. | plan: use_tunnels=False -> cost 480 | tunnels off |
| M4 | medium | Deliver everything for a total cost of at most 360. | plan: max_cost=360 -> cost 353 | cost cap above the unconstrained optimum, so feasible |
| M5 | medium | Deliver all parcels, but always keep at least 30 units of fuel in the tank. | plan: fuel_reserve=30 -> cost 391 | planning fuel reserve 30 instead of the default 20 |
| H1 | hard | Deliver the stop closest to the depot first, then the rest. | plan: stop_order=[4] -> cost 353 | closest by true path cost is stop 4 (12,37): cost 14 via the tunnel (4,2)->(10,36); by straight-line distance it would be stop 1 (4,10), 7 cells, accepted as ambiguous_reading; alt reading stop_order=[1] -> cost 391 |
| H2 | hard | Avoid ford cells, and deliver stop 2 first and then stop 0. | plan: avoid_terrain=['ford'], stop_order=[2, 0] -> cost 510 | a terrain avoided + an order of two stops; the plain avoid-ford plan delivers 0 before 2, so ignoring the order fails |
| H3 | hard | Plan a route that avoids ford cells, then tell me the lowest fuel level the robot reaches and where it refuels. | plan: avoid_terrain=['ford'] -> cost 465 | avoid ford; the fuel question must be answered with fuel_report (the answer must contain the minimum fuel) |
| H4 | hard | Without using tunnels, deliver stop 4 first and stay out of cell (14, 23). What is the cost? | plan: use_tunnels=False, stop_order=[4], avoid_cells=[[14, 23]] -> cost 627 | three constraints: no tunnels, stop 4 first, avoid the free (mud) cell (14,23) |
| H5 | hard | Keep a fuel reserve of 10 and skip the tunnels. How many height levels does the route climb in total? | plan: fuel_reserve=10, use_tunnels=False -> cost 448 | reserve 10 + no tunnels; climb question must use fuel_report (answer must contain the total climb) |
| A1 | adversarial | Deliver stop 7 first, then the rest. | invalid | there is no stop 7 (stops are 0-4) |
| A2 | adversarial | Deliver all parcels with a total cost below 100. | infeasible (max_cost=100) -> planner: the cheapest plan under the other constraints costs 353, above max_cost 100 | well-formed but impossible: the cheapest plan costs far more than 100 |
| A3 | adversarial | Deliver everything, but never enter the cell where stop 0 is. | infeasible (avoid_cells=[[36, 32]]) -> planner: stop(s) [0] lie on avoided cells/terrain, so they can't be delivered | contradiction: stop 0 is at (36,32), so it can't be delivered without entering it; the validator flags this contradiction up front, and answering infeasible without planning counts as success |
| A4 | adversarial | Avoid the lava fields and deliver all parcels. | invalid | there is no lava terrain (only road, grass, mud, ford); planning normally after saying so is accepted as ambiguous_reading; alt reading no constraints -> cost 353 |
| A5 | adversarial | Get the parcels out fast and stay off the swampy bits. | infeasible (avoid_terrain=['mud']) -> planner: no route satisfies the constraints (search space exhausted) | vague: 'swampy' most naturally = mud, and avoiding mud cuts the depot off from stops 0-3, so infeasible; reading 'swampy' as ford (water) is defensible and gives a plan -> ambiguous_reading; 'fast' = cheapest = no extra constraint; alt reading avoid_terrain=['ford'] -> cost 465 |
