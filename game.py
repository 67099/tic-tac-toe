"""
game.py - 3-Pieces Tic-Tac-Toe Core Logic
"""

from collections import deque
import copy


class GameState:
    """Represents the full state of a 3-Pieces Tic-Tac-Toe game."""

    WIN_CONDITIONS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6),              # diagonals
    ]

    MAX_PIECES = 3

    def __init__(self):
        self.board = [None] * 9          # None, 'X', or 'O'
        self.current_player = 'X'
        self.piece_history = {'X': deque(), 'O': deque()}  # tracks placement order
        self.move_count = 0
        self.winner = None
        self.game_over = False

    def clone(self):
        """Deep copy the game state."""
        new = GameState()
        new.board = self.board[:]
        new.current_player = self.current_player
        new.piece_history = {
            'X': deque(self.piece_history['X']),
            'O': deque(self.piece_history['O']),
        }
        new.move_count = self.move_count
        new.winner = self.winner
        new.game_over = self.game_over
        return new

    def get_legal_moves(self):
        """Return list of empty cell indices."""
        if self.game_over:
            return []
        return [i for i, cell in enumerate(self.board) if cell is None]

    def apply_move(self, position):
        """
        Place a piece at position for the current player.
        If player already has 3 pieces, the oldest is removed first.
        Returns True if move was applied successfully.
        """
        if self.board[position] is not None or self.game_over:
            return False

        player = self.current_player
        history = self.piece_history[player]

        # Remove oldest piece if at limit
        if len(history) >= self.MAX_PIECES:
            oldest = history.popleft()
            self.board[oldest] = None

        # Place new piece
        self.board[position] = player
        history.append(position)
        self.move_count += 1

        # Check win
        if self.check_winner(player):
            self.winner = player
            self.game_over = True
        else:
            self.current_player = 'O' if player == 'X' else 'X'

        return True

    def check_winner(self, player):
        """Check if the given player has three in a row."""
        for a, b, c in self.WIN_CONDITIONS:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return True
        return False

    def get_winning_line(self):
        """Return the winning triple of indices, or None."""
        if self.winner is None:
            return None
        for a, b, c in self.WIN_CONDITIONS:
            if self.board[a] == self.board[b] == self.board[c] == self.winner:
                return (a, b, c)
        return None

    def is_terminal(self):
        return self.game_over

    def get_oldest_piece(self, player):
        """Return the index of the oldest piece for a player, or None."""
        if self.piece_history[player]:
            return self.piece_history[player][0]
        return None

    def __repr__(self):
        symbols = {None: '.', 'X': 'X', 'O': 'O'}
        rows = []
        for r in range(3):
            row = ' '.join(symbols[self.board[r * 3 + c]] for c in range(3))
            rows.append(row)
        return '\n'.join(rows)
