"""
alpha_beta.py - Minimax with Alpha-Beta Pruning (depth-limited)
"""

import math
import time


class AlphaBetaAgent:
    """
    AI agent using Minimax with Alpha-Beta pruning.
    Uses a heuristic evaluation function for non-terminal states.
    """

    def __init__(self, player, depth=5):
        self.player = player          # 'X' or 'O'
        self.opponent = 'O' if player == 'X' else 'X'
        self.depth = depth
        self.nodes_explored = 0
        self.time_taken = 0.0

    def choose_move(self, state):
        """Return the best move index for the current state."""
        start = time.time()
        self.nodes_explored = 0

        legal = state.get_legal_moves()
        if not legal:
            return None

        best_move = None
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf

        for move in legal:
            child = state.clone()
            child.apply_move(move)
            score = self._minimax(child, self.depth - 1, alpha, beta, False)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        self.time_taken = time.time() - start
        return best_move

    def _minimax(self, state, depth, alpha, beta, is_maximizing):
        self.nodes_explored += 1

        if state.is_terminal():
            return self._terminal_score(state)

        if depth == 0:
            return self._evaluate(state)

        legal = state.get_legal_moves()

        if is_maximizing:
            value = -math.inf
            for move in legal:
                child = state.clone()
                child.apply_move(move)
                value = max(value, self._minimax(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            return value
        else:
            value = math.inf
            for move in legal:
                child = state.clone()
                child.apply_move(move)
                value = min(value, self._minimax(child, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha cutoff
            return value

    def _terminal_score(self, state):
        """Score for terminal states."""
        if state.winner == self.player:
            return 1000
        elif state.winner == self.opponent:
            return -1000
        return 0

    def _evaluate(self, state):
        """
        Heuristic evaluation for non-terminal states.
        Scores lines based on piece counts for each player.
        """
        score = 0
        for line in state.WIN_CONDITIONS:
            score += self._evaluate_line(state, line)
        # Bonus: center control
        if state.board[4] == self.player:
            score += 3
        elif state.board[4] == self.opponent:
            score -= 3
        return score

    def _evaluate_line(self, state, line):
        """Score a single line (3 cells)."""
        player_count = sum(1 for i in line if state.board[i] == self.player)
        opp_count = sum(1 for i in line if state.board[i] == self.opponent)

        # Line is blocked if both players have pieces in it
        if player_count > 0 and opp_count > 0:
            return 0

        if player_count == 3:
            return 100
        elif player_count == 2:
            return 10
        elif player_count == 1:
            return 1

        if opp_count == 3:
            return -100
        elif opp_count == 2:
            return -10
        elif opp_count == 1:
            return -1

        return 0
