"""Part C: the REDUCED game that Minimax / Alpha-Beta search (Turn 3).

Searching the whole 40x40 map with both robots is far too big, so we play a small game in a
W x W WINDOW (default 9 x 9) centred on our agent:

    game = Game(root_state, width=9)        # root_state: a GameState (oel/game/state.py)
    game.moves(state)        -> legal moves of the player to move, in a FIXED order
    game.result(state, move) -> the next GameState
    game.is_terminal(state)  -> (True/False, reason)
    game.evaluate(state)     -> Laiba's evaluate(state, weights): higher = better for us

Rules, and why each one exists:
- Players: our agent is MAX, the rival (blocker) is MIN. The game is zero-sum on our
  evaluation: the rival wants exactly what is worst for us. They alternate: agent, rival, agent...
  Depth is counted in PLIES (one move by one player), so depth 6 = 3 moves each.
- The window is fixed at the ROOT of a search (centred on our agent there) and does not move
  during that search. Cells outside it count as walls for BOTH players: that is what makes the
  game small. The evaluation at the leaves still knows the whole map (remaining route, fuel to
  the nearest station), so the window limits what is SEARCHED, not what is KNOWN.
- Agent moves: N / S / E / W with the real DeliveryProblem rules (terrain cost, fuel, hills,
  refuelling, delivering on entry), using the REAL fuel limit (tank down to 0, like the
  simulator; the planning reserve is only a margin for route planning).
    * Never into the rival's cell (the simulator treats it as a wall).
    * TUNNEL only if the exit is inside the window (our tunnels are long, so in practice this is
      rare): a jump out of the window would leave the game.
    * WAIT is always allowed: against a blocker the best move is sometimes to let it move away.
      Like the simulator's wait(): no fuel, the position stays the same.
- Rival moves: N / S / E / W or WAIT (a blocker often wants to stay where it is).
    * Never into our cell.
    * ASSUMPTION: the rival uses no fuel and ignores terrain cost (every free cell is one step).
      This is exactly how the simulator moves the placeholder rival (Simulator.rival_target).
- Terminal states:
    * our agent delivers its next TARGET stop (the reason we are in this game): good, scored by
      evaluate() (a delivery is worth +2, the last one +1000);
    * Laiba's is_terminal(): all delivered (win), stranded = no legal move even without the
      rival (loss, -1000), step limit (draw);
    * otherwise the depth limit decides, and evaluate() scores the position.
  Being boxed in ONLY by the rival is not terminal (we can always WAIT; the rival must move),
  the same rule as the simulator and the evaluation (low mobility, interference -1).
"""
from __future__ import annotations

from oel.game.evaluation import DEFAULT_WEIGHTS, evaluate
from oel.game.state import GameState, after_agent_move, after_rival_move, is_terminal
from oel.world.problem import MOVES, TUNNEL

WAIT = "WAIT"
DIRECTIONS = ("N", "E", "S", "W")             # base order (see Game.agent_moves for ours)
AGENT_ORDER = DIRECTIONS + (TUNNEL, WAIT)
RIVAL_ORDER = DIRECTIONS + (WAIT,)
DEFAULT_WIDTH = 9


class Game:
    """The window game around one root position. See the module docstring for the rules."""

    def __init__(self, root: GameState, width: int = DEFAULT_WIDTH, weights: dict | None = None):
        if width < 3 or width % 2 == 0:
            raise ValueError("the window width must be odd and at least 3")
        self.root = root
        self.ctx = root.ctx
        self.world = root.ctx.world                # real-world rules (fuel down to 0)
        self.cfg = root.ctx.problem.cfg
        self.width = width
        self.weights = DEFAULT_WEIGHTS if weights is None else weights
        half = width // 2
        r, c = root.agent
        self.rows = (r - half, r + half)           # inclusive bounds, may stick out of the map
        self.cols = (c - half, c + half)
        self.target = root.target_stop            # the stop this game is about
        self.root_mask = root.delivered_mask

    # ------------------------------------------------------------ the board
    def in_window(self, cell) -> bool:
        return self.rows[0] <= cell[0] <= self.rows[1] and self.cols[0] <= cell[1] <= self.cols[1]

    def open_cell(self, cell) -> bool:
        """Free on the real map AND inside the window (outside = a wall in this game)."""
        return self.in_window(cell) and self.cfg.is_free(cell)

    # ------------------------------------------------------------ moves
    def plan_move(self, state: GameState):
        """The move that follows our A* plan (into state.path[0]), or None if it isn't a single
        move from here (e.g. a slip pushed us off the plan)."""
        if not state.path:
            return None
        for action in DIRECTIONS + (TUNNEL,):
            t = self.world.transition(state.agent, action)
            if t is not None and t[0] == state.path[0]:
                return action
        return None

    def agent_moves(self, state: GameState) -> list:
        """Our legal moves in a fixed, deterministic order:
            the plan's next move, then WAIT, then the rest of N, E, S, W, TUNNEL.
        Why this order: Minimax keeps the FIRST of several equally good moves (ties only matter at
        the root). Our evaluation scores where we END UP, not the cost or fuel paid on the way, so
        against a blocker that just stays put, "wait" and "wander off and come back" score the
        same. In the real simulator they don't: a wait costs 1 step and no fuel, a move costs
        terrain and fuel. So on a tie we follow the plan, and if the plan's step is blocked we
        wait, the cheapest option. A move is only chosen over these if it is STRICTLY better."""
        legal = set()
        for action in self.world.actions(state.agent_state):      # real rules: walls, fuel, tunnels
            nxt = self.world.transition(state.agent, action)[0]
            if self.in_window(nxt) and nxt != state.rival:
                legal.add(action)
        first = self.plan_move(state)
        order = ([first] if first in legal else []) + [WAIT] + [m for m in AGENT_ORDER if m != WAIT and m != first]
        return [m for m in order if m in legal or m == WAIT]

    def rival_moves(self, state: GameState) -> list:
        """The rival's legal moves, in the fixed order N, E, S, W, WAIT."""
        out = []
        if state.rival is not None:
            for move in DIRECTIONS:
                dr, dc = MOVES[move]
                cell = (state.rival[0] + dr, state.rival[1] + dc)
                if self.open_cell(cell) and cell != state.agent:
                    out.append(move)
        out.append(WAIT)
        return out

    def moves(self, state: GameState) -> list:
        return self.agent_moves(state) if state.to_move == "agent" else self.rival_moves(state)

    def result(self, state: GameState, move) -> GameState:
        """The position after `move` by the player to move (the move must be legal)."""
        if state.to_move == "agent":
            if move == WAIT:
                return after_agent_move(state, state.agent_state)          # stay put, no fuel
            return after_agent_move(state, self.world.result(state.agent_state, move))
        if move == WAIT:
            return after_rival_move(state, None)
        dr, dc = MOVES[move]
        return after_rival_move(state, (state.rival[0] + dr, state.rival[1] + dc))

    # ------------------------------------------------------------ end of the game
    def target_delivered(self, state: GameState) -> bool:
        return (self.target is not None and state.delivered_mask >> self.target & 1
                and not self.root_mask >> self.target & 1)

    def is_terminal(self, state: GameState) -> tuple:
        """(True, reason) when this game is over; the depth limit is the search's business."""
        if self.target_delivered(state):
            return True, "target delivered"
        done, outcome = is_terminal(state)
        if done:
            return True, outcome
        return False, "running"

    def evaluate(self, state: GameState) -> float:
        """Laiba's evaluation, unchanged: from OUR side, +-1000 for a won / lost game."""
        return evaluate(state, self.weights)
