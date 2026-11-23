"""The stochastic "real world" that a plan is executed in (separate from the planning model).

Differences from DeliveryProblem:
  * slip: with probability cfg.slip a N/S/E/W move goes in a random PERPENDICULAR direction
    instead (TUNNEL jumps never slip);
  * a rival "blocker" robot moves one cell after every agent step; the rival's cell is a wall
    for the agent and the agent's cell is a wall for the rival;
  * a move that fails (slip into a wall/rival, or blocked plan step) leaves the agent where it
    is, burns no fuel but still costs cfg.failed_move_cost (a wasted time step).
Successful moves go through problem.result(), i.e. the SAME fuel/hill/tunnel rules the planner
uses, so the two can never disagree. Every random draw uses the rng passed in (reproducible).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from oel.world.problem import MOVES, TUNNEL

# a slip turns the intended move 90 degrees, left or right
PERPENDICULAR = {"N": ("E", "W"), "S": ("E", "W"), "E": ("N", "S"), "W": ("N", "S")}


@dataclass
class StepInfo:
    new_state: tuple
    intended: str
    actual: str            # the direction actually tried (differs from intended after a slip)
    slipped: bool
    failed: bool           # True if the agent could not move and stayed put
    cost: float
    fuel_used: int         # net fuel paid for the move (negative = regen); 0 for a failed move
    delivered_now: list    # stop indices delivered by this step
    rival_pos: tuple
    done: bool
    outcome: str           # "running", "win", "loss" or "draw"


@dataclass
class RunReport:
    outcome: str
    total_cost: float      # cost actually paid in the simulator
    planned_cost: float    # cost of the original plan in the perfect model
    extra_cost: float      # total_cost - planned_cost (price of slips + rival); NaN unless "win"
    steps: int
    slips: int
    failed_moves: int
    waits: int             # steps spent waiting for the rival to move out of the way
    end_reason: str = ""   # why the run ended, e.g. "stranded: no plan can finish from here"
    replans: list = field(default_factory=list)   # one dict per replan: step, kind, nodes, runtime_s
    agent_path: list = field(default_factory=list)  # cells visited by the agent
    rival_path: list = field(default_factory=list)  # cells visited by the rival

    @property
    def n_rejoin(self) -> int:
        return sum(1 for r in self.replans if r["kind"] == "rejoin")

    @property
    def n_full(self) -> int:
        return sum(1 for r in self.replans if r["kind"] == "full")


# ---------------------------------------------------------------- rival
def greedy_blocker(sim, lookahead: int = 3):
    """PLACEHOLDER rival policy: Ali replaces it with adversarial search in Turn 3.

    Aim for the cell `lookahead` steps along the straight line from the agent to its nearest
    undelivered stop (where the agent is probably heading), and take the one step that gets the
    rival closest to it. Returns "N"/"S"/"E"/"W", or None to stay put. Deterministic.
    """
    ar, ac, mask, _fuel = sim.state
    left = [s for i, s in enumerate(sim.problem.stops) if not mask >> i & 1]
    if not left:
        return None
    sr, sc = min(left, key=lambda s: abs(s[0] - ar) + abs(s[1] - ac))
    dist = abs(sr - ar) + abs(sc - ac)
    frac = min(1.0, lookahead / dist) if dist else 0.0
    target = (round(ar + frac * (sr - ar)), round(ac + frac * (sc - ac)))

    def gap(cell):
        return abs(cell[0] - target[0]) + abs(cell[1] - target[1])

    best_move, best_gap = None, gap(sim.rival_pos)   # staying put is allowed
    for move in MOVES:
        cell = sim.rival_target(move)
        if cell is not None and gap(cell) < best_gap:
            best_move, best_gap = move, gap(cell)
    return best_move


# ---------------------------------------------------------------- simulator
class Simulator:
    """Holds the agent state, the rival position and the step count."""

    def __init__(self, config, problem, rng, rival_policy=greedy_blocker, use_rival=True):
        self.cfg = config
        self.problem = problem
        self.rng = rng
        self.rival_policy = rival_policy
        self.use_rival = use_rival
        self.state = problem.initial_state()
        self.steps = 0
        self.total_cost = 0.0
        self.outcome = "running"
        self.end_reason = ""
        self.rival_pos = self._place_rival() if use_rival else None
        self.agent_path = [self.cell]
        self.rival_path = [self.rival_pos] if use_rival else []

    # ------------------------------------------------------------ small helpers
    @property
    def cell(self) -> tuple:
        return (self.state[0], self.state[1])

    @property
    def done(self) -> bool:
        return self.outcome != "running"

    def _place_rival(self) -> tuple:
        """A random reachable free cell that is not the depot, a stop, a station or a tunnel
        end, and at least 6 steps (Manhattan) from the depot so it doesn't start on top of us."""
        cfg = self.cfg
        special = {tuple(cfg.start), *map(tuple, cfg.stops), *map(tuple, cfg.stations)}
        for a, b in cfg.tunnels:
            special |= {tuple(a), tuple(b)}
        sr, sc = cfg.start
        candidates = [(int(r), int(c)) for r, c in np.argwhere(cfg.reachable_from_start())
                      if (int(r), int(c)) not in special and abs(r - sr) + abs(c - sc) >= 6]
        return candidates[int(self.rng.integers(len(candidates)))]

    def rival_target(self, move):
        """Cell the rival would enter with `move`, or None if that cell is a wall/off the map
        or holds the agent (the agent's cell is a wall for the rival)."""
        dr, dc = MOVES[move]
        cell = (self.rival_pos[0] + dr, self.rival_pos[1] + dc)
        if not self.cfg.is_free(cell) or cell == self.cell:
            return None
        return cell

    def legal_actions(self, state=None) -> list:
        """Planning-model actions that are also not blocked by the rival right now."""
        state = self.state if state is None else state
        legal = []
        for action in self.problem.actions(state):
            nxt, _cost, _use = self.problem.transition(state[:2], action)
            if nxt != self.rival_pos:
                legal.append(action)
        return legal

    # ------------------------------------------------------------ one step
    def step(self, action) -> StepInfo:
        """Try `action` in the real world, then let the rival move."""
        if self.done:
            raise RuntimeError(f"run is over ({self.outcome})")
        actual, slipped = action, False
        if action != TUNNEL and self.rng.random() < self.cfg.slip:
            # the 90-degree turn is also drawn from the seeded rng
            actual = PERPENDICULAR[action][int(self.rng.integers(2))]
            slipped = True

        old = self.state
        if actual in self.legal_actions():
            new = self.problem.result(old, actual)   # same rules as the planner
            cost = self.problem.step_cost(old, actual, new)
            fuel_used = self.problem.transition(old[:2], actual)[2]
            failed = False
        else:
            # wall, map edge, rival, or not enough fuel: stay put, burn nothing, lose a step
            new, cost, fuel_used, failed = old, self.cfg.failed_move_cost, 0, True

        self.state = new
        delivered_now = self.problem.delivered(new[2] & ~old[2])
        self._end_step(cost)
        return StepInfo(new, action, actual, slipped, failed, cost, fuel_used,
                        delivered_now, self.rival_pos, self.done, self.outcome)

    def wait(self) -> None:
        """Stay put on purpose for one step (the rival blocks the way). Like a failed move:
        no fuel burned, but it costs failed_move_cost and counts toward the step limit."""
        if self.done:
            raise RuntimeError(f"run is over ({self.outcome})")
        self._end_step(self.cfg.failed_move_cost)

    def _end_step(self, cost) -> None:
        """Book-keeping shared by step() and wait(): cost, step count, outcome, rival move."""
        new = self.state
        self.total_cost += cost
        self.steps += 1
        self.agent_path.append(self.cell)

        if self.problem.is_goal(new):
            self.outcome, self.end_reason = "win", "all parcels delivered"
        elif not self.problem.actions(new):
            # stuck even if the rival left (e.g. empty tank away from a station): a loss.
            # Being boxed in ONLY by the rival is not a loss: the rival moves and we can wait.
            self.outcome, self.end_reason = "loss", "no legal move (out of fuel)"
        elif self.steps >= self.cfg.max_steps:
            self.outcome, self.end_reason = "draw", "step limit reached"

        if self.use_rival and not self.done:
            move = self.rival_policy(self)
            if move is not None and self.rival_target(move) is not None:
                self.rival_pos = self.rival_target(move)
            self.rival_path.append(self.rival_pos)

    # ------------------------------------------------------------ executing a whole plan
    def predict(self, actions, state=None) -> list:
        """States the PLANNING model expects after each action: [state, s1, s2, ...]."""
        states = [self.state if state is None else state]
        for action in actions:
            states.append(self.problem.result(states[-1], action))
        return states

    def plan_cost(self, actions, state=None) -> float:
        states = self.predict(actions, state)
        return sum(self.problem.step_cost(s, a, n) for s, a, n in zip(states, actions, states[1:]))

    def run_plan(self, actions, replan_fn=None) -> RunReport:
        """Execute a plan until win/loss/draw.

        Blind mode (replan_fn=None): keep executing the planned actions whatever happens (the
        "no slip" assumption). A step that turns out illegal is a failed move. If the plan runs
        out before all parcels are delivered, the outcome is "draw".

        Replanning mode: before each step, if the agent is off the plan (a slip or failed move),
        the next planned step is blocked by the rival, or the plan is used up, call
        replan_fn(sim, plan, plan_states, i) -> (new_actions, kind, nodes) or None, and continue
        with the new plan. kind "wait" means: keep the plan and stay put for one step.
        None means no plan exists from here -> "loss".
        """
        plan = list(actions)
        plan_states = self.predict(plan)
        planned_cost = self.plan_cost(plan)
        cost_before = self.total_cost
        steps_before = self.steps
        slips = failed = waits = 0
        replans = []
        i = 0   # index of the next planned action

        while not self.done:
            if replan_fn is not None:
                off_plan = self.state != plan_states[i]
                used_up = i >= len(plan)
                blocked = not used_up and plan[i] not in self.legal_actions()
                if off_plan or used_up or blocked:
                    t0 = time.perf_counter()
                    new = replan_fn(self, plan, plan_states, i)
                    if new is None:
                        self.outcome, self.end_reason = "loss", "stranded: no plan can finish from here"
                        break
                    new_plan, kind, nodes = new
                    if kind == "wait":
                        self.wait()
                        waits += 1
                        continue
                    replans.append({"step": self.steps, "kind": kind, "nodes": nodes,
                                    "runtime_s": time.perf_counter() - t0})
                    plan = new_plan
                    plan_states = self.predict(plan)
                    i = 0
            if i >= len(plan):
                self.outcome, self.end_reason = "draw", "plan used up"  # blind mode
                break
            info = self.step(plan[i])
            slips += info.slipped
            failed += info.failed
            i += 1

        total = self.total_cost - cost_before
        # extra cost only means something for a finished delivery; a run that stopped early
        # paid LESS than the plan, which would look like a (meaningless) negative extra cost
        extra = total - planned_cost if self.outcome == "win" else float("nan")
        return RunReport(self.outcome, total, planned_cost, extra,
                         self.steps - steps_before, slips, failed, waits, self.end_reason, replans,
                         list(self.agent_path), list(self.rival_path))


# ---------------------------------------------------------------- replanning strategy
def fuel_needed(problem, plan, plan_states) -> list:
    """need[k] = the least fuel the agent must have at plan step k for the REST of the plan
    (plan[k:]) to never run out. Computed backwards from the end of the plan:
      - at the end nothing more is needed: need[last] = 0;
      - a move into a refuel point only needs its own net use (the tank is full afterwards);
      - any other move needs its own net use PLUS what is needed after it.
    need[k] is never more than the fuel the plan itself had at step k."""
    need = [0] * (len(plan) + 1)
    for k in range(len(plan) - 1, -1, -1):
        nxt, _cost, use = problem.transition(plan_states[k][:2], plan[k])
        if problem.is_refuel_point(nxt):
            need[k] = max(use, 0)
        else:
            need[k] = max(use + need[k + 1], 0)
    return need


class RejoinReplanner:
    """replan_fn for Simulator.run_plan: rejoin the plan if possible, else wait or full replan.

    Rejoin: a small search (only cells within cfg.rejoin_radius of the agent, rival = wall) for
    the cheapest way back to a state on the REMAINING plan with the same delivered set and at
    least the fuel the rest of the plan needs from there (fuel_needed). More fuel is always fine:
    every move that is legal with less fuel is still legal with more, and refuelling fills both
    to capacity. So after a rejoin the rest of the plan can't run out of fuel.
    Wait: if we are still ON the plan and only the rival blocks the next step (and no short
    detour exists), stay put one step; the rival moves every step. Cheaper than a full replan.
    Full replan: full_planner on the whole map from the current state (rival = wall).
    full_planner is pluggable (stand-in UCS now; Laiba's A* later) to compare strategies.
    """

    def __init__(self, full_planner, rejoin_planner, radius: int, rejoin_max_nodes: int = 20000):
        self.full_planner = full_planner
        self.rejoin_planner = rejoin_planner   # must accept is_goal= and max_nodes=
        self.radius = radius
        self.rejoin_max_nodes = rejoin_max_nodes

    def __call__(self, sim, plan, plan_states, i):
        on_plan = i < len(plan) and sim.state == plan_states[i]
        rejoin = self._rejoin(sim, plan, plan_states, i, on_plan)
        if rejoin is not None:
            return rejoin
        if on_plan:
            # on the plan, so only the rival is in the way: wait for it to move
            return list(plan), "wait", 0
        return self._full(sim)

    def _rejoin(self, sim, plan, plan_states, i, on_plan):
        # If the next step is blocked (agent still ON the plan), we must rejoin at least one
        # step further along, otherwise "rejoin where I am" would repeat the blocked step.
        first_k = i + 1 if on_plan else i
        need = fuel_needed(sim.problem, plan, plan_states)
        # (row, col, mask) -> list of (k, fuel needed at step k)
        targets = {}
        for k in range(first_k, len(plan_states)):
            r, c, m, _f = plan_states[k]
            targets.setdefault((r, c, m), []).append((k, need[k]))
        if not targets:
            return None

        def back_on_plan(s):
            return any(s[3] >= f for _k, f in targets.get(s[:3], ()))

        ar, ac = sim.cell
        far = {(int(r), int(c)) for r, c in np.argwhere(sim.cfg.grid != -1)
               if abs(r - ar) + abs(c - ac) > self.radius}
        walls = far | ({sim.rival_pos} if sim.rival_pos else set())
        local = sim.problem.replan_from(sim.state, extra_blocked=walls)
        res = self.rejoin_planner(local, is_goal=back_on_plan, max_nodes=self.rejoin_max_nodes)
        if not res.solved:
            return None
        end = res.path[-1]
        # continue from the LATEST matching plan step (skips any loop the slip short-cut)
        k = max(k for k, f in targets[end[:3]] if end[3] >= f)
        return res.actions + list(plan[k:]), "rejoin", res.nodes_expanded

    def _full(self, sim):
        walls = {sim.rival_pos} if sim.rival_pos else set()
        res = self.full_planner(sim.problem.replan_from(sim.state, extra_blocked=walls))
        if not res.solved and walls:
            # the rival may be sealing a corridor: plan as if it will move away (it will)
            res = self.full_planner(sim.problem.replan_from(sim.state))
        if not res.solved:
            return None
        return list(res.actions), "full", res.nodes_expanded
