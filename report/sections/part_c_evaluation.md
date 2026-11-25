_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part C: our evaluation function for the game against the blocker (draft)

## Where it is used
In the adversarial part, our agent and the rival "blocker" take turns: our move, then the rival's. Minimax / Alpha-Beta (Turn 3) search a few turns ahead in a window around the agent and need a score for the positions where the search stops. That score is our evaluation function:

> **eval(s) = Σ wᵢ · fᵢ(s)** for a non-terminal state;
> **+1000 / −1000 / 0** for a won / lost / drawn state.

The score is seen from **our** side (higher = better for us). The blocker, as the minimising player, prefers low scores. All six features are scaled to about −1…1 (or 0…1), so the weights can be compared directly.
Code: `oel/game/evaluation.py` (features, weights) and `oel/game/state.py` (the game state).

## The features

| # | feature | definition | sign | default weight |
|---|---|---|---|---:|
| 1 | progress | −h_ours(cell, delivered) ÷ h_ours(start) | higher = less left to do | 4 |
| 2 | delivered | parcels delivered ÷ 5 | + | 10 |
| 3 | interference | −max over the next 8 plan cells of (1 − j/8) · max(0, 1 − d(rival, cell)/4) | − (rival on our route) | 2 |
| 4 | race | (rival's moves to our next stop − our moves) ÷ 20, clipped to ±1 | + (we arrive first) | 1.5 |
| 5 | mobility | ½ · legal moves/4 + ½ · free cells within 2 moves/12 (rival's cell excluded) | + | 0.5 |
| 6 | fuel safety | (fuel − fuel needed to reach the nearest station or depot) ÷ capacity, clipped to ±1 | + | 3 |

### 1. Progress: the remaining *lower-bound* cost
- **What it measures:** how much route cost is still left, using our admissible heuristic h_ours. That is the MST over the undelivered stops in the relaxed map, with tunnel jumps and uphill costs built in (Part B).
- **Why it matters on our map:** a textbook "distance to the goal" (Manhattan to the nearest parcel) would be badly wrong here:
  - a tunnel can make a stop 20+ cells away only 8 cost away;
  - hills make A→B cost more than B→A;
  - there are five stops, not one goal.

  h_ours knows about all of that, and it never overestimates (proven in Part B), so the agent is never lured away by a fake shortcut.
- **Why it matters against a blocker:** when the rival blocks a corridor, the cheaper option is often a detour through a tunnel or downhill. h_ours ranks those detours correctly.
- **Sign:** a smaller remaining cost means a higher score.

### 2. Delivered: the actual goal
- **What it measures:** how many parcels are done.
- **Why it needs its own feature:** progress alone is not enough. Delivering a stop removes it from the MST, but the MST can then grow towards a far-away stop, so h can *rise* at the moment of a delivery (h_ours is not consistent, Part B). It really does: on the default route, h_ours goes from 276 to 291 at the first delivery and from 228 to 229 at the second. Without this feature, a short search could refuse a delivery. With weight 10, each parcel is worth 2 points, more than any one-step change of the other features.
- **Why it matters against a blocker:** a blocker's best trick is to park on our next stop. The large delivered weight makes the search grab a parcel whenever it can, instead of manoeuvring.

### 3. Interference: the rival on *our* route
- **What it measures:** how close the rival is to the next 8 cells of our current A\* plan. A cell we will reach sooner counts more.
  - The rival standing on our very next cell gives −1.
  - The rival 4 or more cells from every path cell gives 0.
- **Why it matters against a blocker:** a *blocker* doesn't try to catch us. It tries to stand where we need to go, which costs us waits, failed moves and replans. Plain "distance to the rival", the usual chase or evade feature, would be wrong:
  - a rival right next to us but behind us is harmless;
  - a rival 3 cells ahead on our path is a problem.

  Measuring closeness to the *path* captures exactly the blocker's threat.
- **Why the path, specifically on our map:** corridors between walls (28.5% of cells are blocked) and tunnel entrances are chokepoints. A blocker sitting on one forces a long detour, and the A\* path tells us exactly which chokepoints we're about to use.

### 4. Race: who reaches our next stop first
- **What it measures:** (the rival's moves to the stop our plan delivers next − our moves), counted in **moves**, not cost.
- **Why moves, not cost:** both robots move one cell per turn whatever the terrain, so who arrives first is decided by the number of moves. A mud or ford cell is expensive for our budget but doesn't slow us down in the race.
- **Specific to our map:** our move counts include tunnel jumps, and the rival's do not (it can only move N/S/E/W). That is a real advantage on our map, and the feature rewards using it.
- **Why it matters against a blocker:** if the rival arrives first, it can park on the stop. The placeholder rival does exactly that, and it caused most of our draws.
- **Sign:** positive when we win the race.

### 5. Mobility: room to manoeuvre
- **What it measures:** our legal moves now (fuel included, the rival's cell excluded) and the free cells within 2 moves.
- **Why it matters:** in a corridor, a blocker can box us in against a wall, and slips (25%) need room to recover.
- **Why a small weight:** mobility is a tie-breaker, not a goal. Open ground is not better than the route itself.
- **"Trapped" is deliberately not a loss.** Our simulator (and so the game) does not count "boxed in only by the rival" as a loss: the rival must move, and we can wait. So instead of a terminal value, the evaluation gives such a position low mobility and strong interference.

### 6. Fuel safety: can we still reach a station?
- **What it measures:** the fuel we would have left after driving to the *nearest* refuel point (a station or the depot), as a share of the tank. Negative means we can no longer reach any of them, and a stranding is coming.
- **How "fuel needed" is computed** (`state.py: _fuel_need_field`): it is the least fuel we must have at a cell to reach a refuel point without the tank ever dropping below 0. It uses the simulator's own fuel rule, with hills: climbing burns +3 per level, descending gives back 1 per level. Because of that regen, a move can have *negative* fuel use, so Dijkstra is not safe. We use a label-correcting search instead, which is guaranteed to finish because no loop can gain fuel (REGEN < UP_FUEL). A test checks that the field satisfies its own equation exactly.
- **Why it matters on our map against a blocker:**
  - Our only real losses are strandings (session 3), and a blocker makes them likelier: every wait, block and detour burns fuel the plan didn't budget for.
  - A textbook game evaluation has no resource feature at all.
  - With hills, "far from a station" is not the same as "many cells away": a station downhill is cheap to reach and one uphill is expensive. The field captures that.

### Terminal states
- **Win** (all delivered): +1000 − 0.001·steps.
- **Loss** (stranded: no legal move even without the rival; or a stop that can't be reached at all): −1000 + 0.001·steps.
- **Draw** (step limit): 0.

The small step term makes the search prefer faster wins and later losses. ±1000 is far above anything the features can add up to: |Σ weights| ≈ 21, so a win always beats every non-terminal state (tested).

## Default weights and why
| feature | weight | reason |
|---|---:|---|
| delivered | 10 | the main goal: 2 points per parcel, so a delivery is never traded for position |
| progress | 4 | the route is what wins; the whole remaining route is worth 4 points |
| fuel safety | 3 | stranding was our main real loss; a negative margin must outweigh a little progress |
| interference | 2 | a blocker on our path costs waits and replans, but it moves away again |
| race | 1.5 | losing the race lets the rival park on the stop, but a few moves rarely decide the game |
| mobility | 0.5 | a tie-breaker against being cornered |

These are starting values. Ali tunes them in Turn 3 with `oel/game/tuning.py` (grid search and coordinate ascent over real games, with Wilson CIs).

## How it differs from the textbook evaluation
A typical pursuit/delivery evaluation is "−distance to goal (+ distance from the opponent)". Ours differs in five ways:
1. **Distance is a proven lower bound on the real cost** (h_ours: MST over five stops, tunnels and hills), not Manhattan to one goal. Manhattan is inadmissible next to our tunnels (Part B: it overestimates by up to 34).
2. **The opponent term is about our route, not about us** (interference), because a blocker blocks rather than chases.
3. **A race term in moves, with tunnels for us only:** an asymmetry specific to our map.
4. **A resource term** (fuel safety) with hill-aware fuel and regen. Textbook game evaluations have no notion of a resource that can run out.
5. **Delivered parcels are scored separately,** because our progress estimate is not consistent and can rise at a delivery.

## Sanity checks (no Minimax needed)
**Unit tests** (`tests/test_game_eval.py`, 12 tests): every feature moves the right way.
- Closer to the stop → higher score.
- The rival on our path → lower; on the very next cell → interference = −1.
- Low fuel at the cell farthest from any refuel point → fuel safety < 0 and a lower score.
- One more delivered parcel → a higher score, for each of the 5 stops.
- The rival next to the stop → a worse race; the rival next to us → less mobility.
- A win beats every non-terminal state of a whole simulated run.
- The fuel-need field satisfies its own equation, and every feature stays within its range.

**Along two simulated runs** (`results/figures/eval_along_route.png`, table `eval_along_route`): the default A\* plan with slips, the placeholder rival and replanning, recording the state after every step.

| | default seed 952097431 | seed 952097432 (first winning seed) |
|---|---|---|
| outcome | loss (stranded), 321 steps, 92 slips | win, 278 steps, 68 slips |
| score: start → last non-terminal | 0.14 → 9.41 | −0.46 → 9.71 |
| mean change: delivery / slip / other step | +1.41 / −0.10 / +0.06 | +1.10 / −0.04 / +0.04 |
| min interference | 0 (the rival never came near our path) | **−1.0** (the rival on our path around steps 205–265) |
| min fuel safety | **−0.03** (at the end) | 0.19 |

What the figure shows:
- **The score rises step by step** (+0.04 to +0.06 per normal step), **drops on slips** (−0.04 to −0.10: a slip pushes us off the route, so progress falls), and **jumps at every delivery** (+1.1 to +1.4).
- **In the winning run** the rival comes onto our path after the 4th delivery. Interference goes down to −1, and the score visibly stalls and dips until we get past it.
- **In the losing run** fuel safety falls steadily before the stranding: 0.14 ten steps before the end, then 0.12, 0.08 … 0.02, 0.00, −0.01, −0.03. Earlier, at about step 140, it had already touched 0 before a just-in-time recharge, and the score dipped there too.
- **The honest limit:** in the losing run the *total* score still rises to 9.4, because progress and deliveries outweigh the falling fuel margin. A one-step evaluation sees the danger (the feature is there), but with the default weights it doesn't override the route by itself. Two things should fix that: Minimax looking several moves ahead (it will see fuel safety go negative a few moves on), and tuning the fuel-safety weight. That is exactly what Turn 3 tunes.
