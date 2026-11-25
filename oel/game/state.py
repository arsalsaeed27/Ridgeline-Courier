"""Part C: the game state that Minimax / Alpha-Beta (Turn 3) search over, and the map context it
carries. Built in Turn 2 so the game code has a fixed interface.

    ctx = GameContext.for_problem(problem)          # map facts, cached per map
    s = from_simulator(sim)                         # the current situation as a GameState
    done, outcome = is_terminal(s)                  # ("win" / "loss" / "draw" / "running")
    s2 = after_agent_move(s, new_agent_state)       # bookkeeping after OUR move
    s3 = after_rival_move(s2, new_rival_cell)       # bookkeeping after the RIVAL's move

GameState holds positions on the FULL map. The reduced game (a window around the agent, Ali's
window.py) decides which moves are allowed; these helpers only do the bookkeeping (turn, step
count, delivered stops, fuel, the plan's remaining cells) so every search builds states the
same way.

Rules (the same as the simulator, oel/world/simulator.py):
  - a turn = our move, then the rival's move; `step` counts OUR moves;
  - win  = every stop delivered;
  - loss = "stranded": no legal move even if the rival left (out of fuel away from a station),
           or "unreachable": some undelivered stop can't be reached at all;
  - draw = the step limit (cfg.max_steps) is reached;
  - being boxed in ONLY by the rival is NOT terminal (the rival moves; the simulator waits), so
    the evaluation punishes it (mobility, interference) instead.
"""
from __future__ import annotations

import dataclasses
import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from oel.search.distance_fields import _signature
from oel.search.heuristics import h_ours
from oel.world.problem import MOVES, TUNNEL

PATH_LEN = 8          # how many upcoming plan cells a GameState keeps (k)

_CONTEXTS = {}        # map signature -> GameContext (one per map + constraints)


# ---------------------------------------------------------------- distance fields for the game
def _step_field(free, target, tunnel_exit) -> np.ndarray:
    """Fewest MOVES from every cell to `target` (BFS backwards from the target).
    Moves between neighbours are two-way, and so are tunnels, so a plain BFS from the target is
    enough (no reversed edges needed: step counts don't depend on hills)."""
    dist = np.full(free.shape, np.inf)
    dist[target] = 0
    queue = deque([target])
    while queue:
        cell = queue.popleft()
        neighbours = [(cell[0] + dr, cell[1] + dc) for dr, dc in MOVES.values()]
        if cell in tunnel_exit:
            neighbours.append(tunnel_exit[cell])
        for nxt in neighbours:
            if 0 <= nxt[0] < free.shape[0] and 0 <= nxt[1] < free.shape[1] and free[nxt] \
                    and math.isinf(dist[nxt]):
                dist[nxt] = dist[cell] + 1
                queue.append(nxt)
    return dist


def _fuel_need_field(problem) -> np.ndarray:
    """need[cell] = the least fuel we must have at `cell` to reach the nearest refuel point
    (a station or the depot) without the tank ever going below 0. Hills included.

    The rule is the simulator's own (fuel_after with reserve 0): a move u -> v with net fuel use
    `use` needs need(u) = max(use + need(v), 0), and need = 0 at a refuel point.
    `use` can be NEGATIVE (downhill regen), so Dijkstra is not safe here; we use a
    label-correcting search instead: whenever a cell's need improves, its predecessors are
    re-checked (a queue of cells to update). It ends because no loop can gain fuel: going up and
    back down always loses fuel overall (REGEN < UP_FUEL, asserted in config.py), so needs can only
    fall a limited number of times."""
    n = problem.cfg.n
    need = np.full((n, n), np.inf)
    reverse = {}                                  # v -> list of (u, use) for real moves u -> v
    for u, options in problem._trans.items():
        for _action, (v, _cost, use) in options.items():
            reverse.setdefault(v, []).append((u, use))
    queue = deque()
    for cell in problem.cfg.refuel_cells():
        cell = tuple(cell)
        if cell in problem._trans:
            need[cell] = 0
            queue.append(cell)
    in_queue = set(queue)
    while queue:
        v = queue.popleft()
        in_queue.discard(v)
        for u, use in reverse.get(v, ()):
            candidate = max(use + need[v], 0)
            if candidate < need[u]:
                need[u] = candidate
                if u not in in_queue:
                    queue.append(u)
                    in_queue.add(u)
    return need


@dataclass
class GameContext:
    """Everything about the MAP that the evaluation needs (computed once per map, then shared).
    Not part of a GameState's identity: two states are equal if their positions are equal."""
    problem: object                # DeliveryProblem (planning view; its stops, map, twists)
    world: object                  # the same problem with reserve 0 (the real legality rule)
    h_start: float                 # h_ours at the depot with nothing delivered (scale for progress)
    agent_steps: list              # agent_steps[i][cell] = fewest moves to stop i (tunnels allowed)
    rival_steps: list              # rival_steps[i][cell] = fewest moves for the rival (no tunnels)
    fuel_need: np.ndarray          # least fuel needed at a cell to reach a refuel point

    @classmethod
    def for_problem(cls, problem) -> "GameContext":
        key = (_signature(problem, True, True), problem.capacity, problem.cfg.use_fuel)
        if key not in _CONTEXTS:
            cfg = problem.cfg
            agent_free = np.zeros((cfg.n, cfg.n), dtype=bool)
            for cell in problem._trans:
                agent_free[cell] = True               # free and not avoided by a constraint
            rival_free = cfg.grid != -1               # the rival ignores our constraints
            tunnels = dict(problem._tunnel_exit)
            start = (cfg.start[0], cfg.start[1], 0, problem.capacity)
            _CONTEXTS[key] = cls(
                problem=problem, world=problem.with_reserve(0),
                h_start=max(h_ours(start, problem), 1.0),
                agent_steps=[_step_field(agent_free, s, tunnels) for s in problem.stops],
                rival_steps=[_step_field(rival_free, s, {}) for s in problem.stops],
                fuel_need=_fuel_need_field(problem) if cfg.use_fuel else np.zeros((cfg.n, cfg.n)))
        return _CONTEXTS[key]


# ---------------------------------------------------------------- the state
@dataclass(frozen=True)
class GameState:
    """One position of the agent-vs-rival game. Frozen, so it is hashable (usable as a dict key,
    e.g. a transposition table). `ctx` is left out of == and hash()."""
    agent: tuple                   # our cell (row, col)
    rival: tuple | None            # the rival's cell, None if there is no rival
    delivered_mask: int            # bit i = stop i delivered
    fuel: int
    step: int                      # our moves so far
    target_stop: int | None        # index of the next stop our plan delivers (None = all done)
    path: tuple                    # the next PATH_LEN cells of our plan (may be shorter)
    to_move: str = "agent"         # "agent" or "rival"
    ctx: GameContext = field(default=None, compare=False, hash=False, repr=False)

    @property
    def agent_state(self) -> tuple:
        """The DeliveryProblem state (row, col, mask, fuel), for problem.actions() etc."""
        return (self.agent[0], self.agent[1], self.delivered_mask, self.fuel)

    @property
    def undelivered(self) -> list:
        return [i for i in range(len(self.ctx.problem.stops)) if not self.delivered_mask >> i & 1]


def nearest_target(ctx: GameContext, cell, mask) -> int | None:
    """The undelivered stop with the fewest moves from `cell` (used when no plan says which)."""
    left = [i for i in range(len(ctx.problem.stops)) if not mask >> i & 1]
    if not left:
        return None
    return min(left, key=lambda i: (ctx.agent_steps[i][cell], i))


def _plan_target(plan_states, index, mask) -> int | None:
    """The stop that the plan delivers next, looking from plan_states[index] on."""
    for s in plan_states[index:]:
        new = s[2] & ~mask
        if new:
            return (new & -new).bit_length() - 1          # lowest new bit
    return None


def from_simulator(sim, plan_states=None, k: int = PATH_LEN) -> GameState:
    """The simulator's current situation as a GameState (our turn).

    plan_states: the predicted states of our current plan (default: the plan the simulator is
    executing, sim.plan_states). The path is the next k planned cells after the state the plan
    expects us to be in now; if a slip pushed us off the plan, it is still the PLAN's cells
    (that is where the replanner will try to take us back to)."""
    ctx = GameContext.for_problem(sim.problem)
    states = sim.plan_states if plan_states is None else plan_states
    index = sim.plan_index if plan_states is None else 0
    mask = sim.state[2]
    path = tuple((s[0], s[1]) for s in states[index + 1:index + 1 + k]) if states else ()
    target = _plan_target(states, index, mask) if states else None
    if target is None:
        target = nearest_target(ctx, sim.cell, mask)
    return GameState(agent=sim.cell, rival=sim.rival_pos, delivered_mask=mask, fuel=sim.state[3],
                     step=sim.steps, target_stop=target, path=path, to_move="agent", ctx=ctx)


def make_state(ctx: GameContext, agent, rival, delivered_mask=0, fuel=None, step=0,
               target_stop=None, path=(), to_move="agent") -> GameState:
    """Build a GameState by hand (tests, experiments). fuel defaults to a full tank; the target
    defaults to the nearest undelivered stop."""
    fuel = ctx.problem.capacity if fuel is None else fuel
    if target_stop is None:
        target_stop = nearest_target(ctx, tuple(agent), delivered_mask)
    return GameState(tuple(agent), None if rival is None else tuple(rival), delivered_mask, fuel,
                     step, target_stop, tuple(map(tuple, path)), to_move, ctx)


# ---------------------------------------------------------------- moving (bookkeeping only)
def after_agent_move(state: GameState, new_agent_state: tuple) -> GameState:
    """The state after OUR move. new_agent_state = (row, col, mask, fuel), e.g. from
    ctx.world.result(state.agent_state, action). Moves the turn to the rival, counts the step,
    trims the path (cells we have reached or skipped are dropped) and picks a new target when
    the old one was just delivered. Legality is the caller's job (Ali's window move generation)."""
    cell = (new_agent_state[0], new_agent_state[1])
    path = state.path
    if cell in path:
        path = path[path.index(cell) + 1:]           # reached (or short-cut to) a planned cell
    mask = new_agent_state[2]
    target = state.target_stop
    if target is None or mask >> target & 1:
        target = nearest_target(state.ctx, cell, mask)
    return dataclasses.replace(state, agent=cell, delivered_mask=mask, fuel=new_agent_state[3],
                               step=state.step + 1, target_stop=target, path=path, to_move="rival")


def after_rival_move(state: GameState, new_rival_cell) -> GameState:
    """The state after the RIVAL's move (None or the same cell = it stays). Back to our turn."""
    cell = state.rival if new_rival_cell is None else tuple(new_rival_cell)
    return dataclasses.replace(state, rival=cell, to_move="agent")


def agent_moves(state: GameState) -> list:
    """Our real-world legal actions in this state (fuel down to 0), minus a move into the rival.
    A convenience for Ali; the window game may restrict it further."""
    world = state.ctx.world
    out = []
    for action in world.actions(state.agent_state):
        nxt = world.transition(state.agent, action)[0]
        if nxt != state.rival:
            out.append(action)
    return out


# ---------------------------------------------------------------- terminal test
def is_terminal(state: GameState) -> tuple:
    """(True, "win" | "loss" | "draw") or (False, "running"). See the rules in the module doc."""
    ctx = state.ctx
    if state.delivered_mask == ctx.problem.goal_mask:
        return True, "win"
    if not ctx.world.actions(state.agent_state):
        return True, "loss"                          # stranded: stuck even without the rival
    if any(math.isinf(ctx.agent_steps[i][state.agent]) for i in state.undelivered):
        return True, "loss"                          # a stop we can never reach
    if state.step >= ctx.problem.cfg.max_steps:
        return True, "draw"
    return False, "running"


__all__ = ["PATH_LEN", "GameContext", "GameState", "from_simulator", "make_state", "is_terminal",
           "after_agent_move", "after_rival_move", "agent_moves", "nearest_target", "TUNNEL"]
