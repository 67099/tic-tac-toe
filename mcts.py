"""
mcts.py - Monte Carlo Tree Search Agent
"""

import math
import random
import time


class MCTSNode:
    """A node in the MCTS tree."""

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move          # move that led to this node
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legal_moves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.is_terminal()

    def ucb1(self, exploration=1.414):
        """Upper Confidence Bound for Trees."""
        if self.visits == 0:
            return math.inf
        exploitation = self.wins / self.visits
        exploration_term = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration_term

    def best_child(self, exploration=1.414):
        return max(self.children, key=lambda c: c.ucb1(exploration))

    def add_child(self, move, state):
        child = MCTSNode(state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child


class MCTSAgent:
    """
    AI agent using Monte Carlo Tree Search.

    Parameters:
    - simulations: number of MCTS iterations (default 500)
      More simulations = stronger play but slower.
    - exploration: UCB1 exploration constant (default sqrt(2) ≈ 1.414)
      Higher = more exploration, lower = more exploitation.
    - time_limit: max seconds per move (optional cap)
    """

    def __init__(self, player, simulations=500, exploration=1.414, time_limit=5.0):
        self.player = player
        self.simulations = simulations
        self.exploration = exploration
        self.time_limit = time_limit
        self.nodes_explored = 0
        self.time_taken = 0.0

    def choose_move(self, state):
        """Run MCTS and return the best move."""
        start = time.time()
        self.nodes_explored = 0

        root = MCTSNode(state.clone())

        for _ in range(self.simulations):
            if time.time() - start > self.time_limit:
                break

            # 1. Selection
            node = self._select(root)

            # 2. Expansion
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)

            # 3. Simulation
            result = self._simulate(node.state.clone())

            # 4. Backpropagation
            self._backpropagate(node, result)
            self.nodes_explored += 1

        self.time_taken = time.time() - start

        if not root.children:
            legal = state.get_legal_moves()
            return random.choice(legal) if legal else None

        # Choose child with most visits (robust best child)
        best = max(root.children, key=lambda c: c.visits)
        return best.move

    def _select(self, node):
        """Traverse tree using UCB1 until a non-fully-expanded or terminal node."""
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child(self.exploration)
        return node

    def _expand(self, node):
        """Add one new child node."""
        move = random.choice(node.untried_moves)
        new_state = node.state.clone()
        new_state.apply_move(move)
        return node.add_child(move, new_state)

    def _simulate(self, state):
        """
        Random rollout from state until terminal.
        Returns 1 if self.player wins, -1 if opponent wins, 0 for draw/limit.
        """
        MAX_MOVES = 50  # safety cap to avoid infinite loops
        moves_made = 0

        while not state.is_terminal() and moves_made < MAX_MOVES:
            legal = state.get_legal_moves()
            if not legal:
                break
            move = random.choice(legal)
            state.apply_move(move)
            moves_made += 1

        if state.winner == self.player:
            return 1
        elif state.winner is not None:
            return -1
        return 0

    def _backpropagate(self, node, result):
        """Propagate result up the tree."""
        while node is not None:
            node.visits += 1
            # Win from the perspective of the node's player
            if node.state.current_player != self.player:
                node.wins += max(0, result)
            else:
                node.wins += max(0, -result)
            node = node.parent
