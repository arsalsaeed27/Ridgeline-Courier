_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

# Part D: LLM dispatcher (draft, M. Arsal Saeed)

## What was built
An English-language dispatcher for the delivery agent. The LLM never plans: it translates a
request into calls to our own tools and reports the outcome.

- **Tools** (`oel/llm/tools.py`): `get_instance_info` (stops 0-4 with cell, terrain, height,
  straight-line and path-cost distance from the depot; stations; tunnels; costs; algorithms),
  `plan_route` (our planner with optional constraints), `simulate` (slip + rival + replanning),
  and `fuel_report`, our twist-specific tool (fuel after each move, refuels, downhill regeneration,
  minimum fuel, total climb).
- **Constraints in the search** (`oel/world/constraints.py`): stop order (a stop counts as
  delivered only once the stops before it are delivered; a bitmask check inside the transition,
  so the state stays `(row, col, mask, fuel)`), avoided terrain/cells (walls), no tunnels, a
  planning fuel reserve and a cost cap. `verify_plan` re-checks a plan independently by replaying it
  on the unconstrained map.
- **Agent** (`oel/llm/agent.py`): our own ReAct loop on Groq's native tool calling (temperature 0,
  at most 8 tool calls): Thought (the model's reasoning) → Action (one tool call) → Observation
  (tool result or validator error). It ends with `RESULT: plan_id=… / infeasible / invalid`.
- **Validation layer** (`oel/llm/validator.py`): pydantic schemas (no invented argument names) +
  checks against our map (stop exists, cell on the grid and not a wall, terrain and algorithm
  exist, sane ranges, no duplicate stops) + a contradiction pre-check (avoiding a stop's own cell or
  terrain → "infeasible"). A rejected call is not executed; the message returns to the LLM.
- **Reproducibility**: LLM replies, plans and simulations are cached on disk under content hashes
  and committed; `run_all.py` replays the whole evaluation without an API key.

## Evaluation design
20 requests in four tiers (easy, medium, hard, adversarial) with gold answers written by us
(`docs/llm_gold_answers.md`). Grading is **outcome-based**: a plan request succeeds if the final
plan passes `verify_plan` against the gold constraints and costs at most 1% more than the direct
planner on the gold constraints; an infeasible/invalid request succeeds if the RESULT word
matches. Argument differences only assign labels. Defensible alternative readings of vague
requests are reported as `ambiguous_reading`; API failures are reported separately and not graded.

## Results (gpt-oss family on Groq)
| model / validation | graded | success (95% Wilson CI) | ambiguous | lost to API errors | tool calls | rejections |
|---|---|---|---|---|---|---|
| direct planner (gold) | 18 | 18 (82–100%) | – | – | – | – |
| gpt-oss-120b OFF / ON | 20 | 20 (84–100%) | 0 | 0 | 1.60 | 0 |
| gpt-oss-20b OFF / ON | 19 | 19 (83–100%) | 1 | 0 | 1.95 | 0 |
| gpt-oss-safeguard-20b OFF / ON | 13 | 13 (77–100%) | 1 | 6 | 1.60 | 0 |

- No model produced an argument the validator would reject, so validation ON followed the same
  conversation as OFF. The models differ only on the vague request H1 ("the stop closest to the
  depot first"): 120b chose stop 4 by path cost (14, via a tunnel; plan 353), both 20B models chose
  stop 1 by straight-line distance (7 cells; plan 391, +10.8%). See `part_d_traces.md`.
- safeguard-20b: our tier allows 2,000 tokens/minute, a request needs ~2,400 (HTTP 413).
- Map facts the planner revealed: avoiding mud cuts the depot off from stops 0–3 (so "stay off the
  swampy bits" is infeasible), while avoiding ford is feasible (cost 465).

## Validator fault injection (no LLM)
The 18 gold `plan_route` calls, each corrupted in 10 ways (180 calls), run without and with the
validator:

| without validation | count | | with validation |
|---|---|---|---|
| crash | 53 | | caught 180 / 180 (100%) |
| silent ignore (nonsense dropped, nobody told) | 30 | | |
| silent wrong plan (e.g. reserve −5 → fuel below 0) | 15 | | |
| wasted search (≥ 5 s, then "infeasible") | 18 | | |
| misleading "infeasible" (wrong reason) | 39 | | |
| correct error | 25 | | |

671 s of planning would be spent on calls the validator rejects up front. (One call per fault type
is request A3, whose gold call already contains a contradiction, and A2/A5 are infeasible anyway;
those explain most `correct_error`/wasted entries that the fault itself did not cause.)

## Discussion
On our 20 requests the validator was a safety net that never fired; fault injection shows what it
prevents regardless of model quality: crashes, silent wrong plans and wasted search. The real
difficulty for the LLM was vague wording, not argument syntax. Limitations: 20 requests, one
model family, temperature 0 (one sample per request).
