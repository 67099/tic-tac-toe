"""
gui.py - 3-Pieces Tic-Tac-Toe | Minimalist GUI
Imam Mohammad Ibn Saud Islamic University — CCIS
"""

import tkinter as tk
from tkinter import ttk, font
import threading
import time
from game import GameState
from alpha_beta import AlphaBetaAgent
from mcts import MCTSAgent


# ── Palette ───────────────────────────────────────────────
BG          = "#2A2A2A"       # dark gray background
PANEL_BG    = "#323232"       # slightly lighter panel
BOARD_BG    = "#C4B9A8"       # dark beige board
LINE_COLOR  = "#A89E8E"       # grid lines
X_COLOR     = "#F0EDE8"       # X pieces - off white (visible on beige)
O_COLOR     = "#2D7A4F"       # O pieces - deep apple green
OLDEST_X    = "#8A8580"       # oldest X piece (faded)
OLDEST_O    = "#5A9E78"       # oldest O piece (faded)
WIN_COLOR   = "#2D7A4F"       # winning line highlight
ACCENT      = "#2D7A4F"       # accent color
TEXT_DARK   = "#F0EDE8"
TEXT_MID    = "#AAAAAA"
TEXT_LIGHT  = "#777770"
BTN_START   = "#2D7A4F"       # start button - apple green
BTN_STOP    = "#8B3A3A"       # stop button - dark red
BTN_RESET   = "#444440"       # reset button
BTN_FG      = "#F0EDE8"
BTN_HOV_START = "#3A9A64"
BTN_HOV_STOP  = "#A04444"
BTN_HOV_RESET = "#555550"

CELL_SIZE   = 120
PADDING     = 20
BOARD_SIZE  = CELL_SIZE * 3


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("3-Pieces Tic-Tac-Toe")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.option_add('*TCombobox*Listbox.background', '#3A3A3A')
        self.option_add('*TCombobox*Listbox.foreground', '#F0EDE8')

        self.state = GameState()
        self.agents = {'X': None, 'O': None}
        self.human_turn = False
        self.game_running = False
        self.ai_thread = None
        self.move_log = []

        self._build_fonts()
        self._build_ui()
        self._reset_game()

    # ── Fonts ──────────────────────────────────────────────
    def _build_fonts(self):
        self.font_title   = tk.font.Font(family="Georgia", size=15, weight="bold")
        self.font_sub     = tk.font.Font(family="Georgia", size=9, slant="italic")
        self.font_piece   = tk.font.Font(family="Georgia", size=38, weight="bold")
        self.font_label   = tk.font.Font(family="Courier New", size=9)
        self.font_status  = tk.font.Font(family="Courier New", size=10, weight="bold")
        self.font_btn     = tk.font.Font(family="Courier New", size=10, weight="bold")
        self.font_small   = tk.font.Font(family="Courier New", size=8)
        self.font_log     = tk.font.Font(family="Courier New", size=8)

    # ── UI Layout ──────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill='x', padx=30, pady=(22, 0))

        tk.Label(header, text="3-Pieces Tic-Tac-Toe",
                 font=self.font_title, bg=BG, fg=TEXT_DARK).pack()
        tk.Label(header, text="Imam Mohammad Ibn Saud Islamic University  ·  CCIS",
                 font=self.font_sub, bg=BG, fg=TEXT_LIGHT).pack(pady=(2, 0))

        divider = tk.Frame(self, bg="#444440", height=1)
        divider.pack(fill='x', padx=30, pady=12)

        # Main content row
        content = tk.Frame(self, bg=BG)
        content.pack(padx=30, pady=0)

        self._build_left_panel(content)
        self._build_board(content)
        self._build_right_panel(content)

        # Status bar
        self._build_status_bar()

    def _build_left_panel(self, parent):
        panel = tk.Frame(parent, bg=BG, width=200)
        panel.pack(side='left', fill='y', padx=(0, 20))
        panel.pack_propagate(False)

        # Mode selection
        tk.Label(panel, text="GAME MODE", font=self.font_label,
                 bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(0, 4))

        self.mode_var = tk.StringVar(value="ai_vs_ai")
        modes = [
            ("AI  vs  AI",    "ai_vs_ai"),
            ("Human  vs  AI", "human_vs_ai"),
        ]
        for text, val in modes:
            rb = tk.Radiobutton(panel, text=text, variable=self.mode_var,
                                value=val, command=self._on_mode_change,
                                font=self.font_label, bg=BG, fg=TEXT_DARK,
                                selectcolor=BG, activebackground=BG,
                                activeforeground=O_COLOR,
                                cursor="hand2")
            rb.pack(anchor='w')

        tk.Frame(panel, bg="#444440", height=1).pack(fill='x', pady=10)

        # Player X settings
        tk.Label(panel, text="PLAYER  X", font=self.font_label,
                 bg=BG, fg=X_COLOR).pack(anchor='w', pady=(0, 4))

        self.x_type_var = tk.StringVar(value="Alpha-Beta")
        self.x_type_menu = ttk.Combobox(panel, textvariable=self.x_type_var,
                                         values=["Alpha-Beta", "MCTS"],
                                         state="readonly", width=14,
                                         font=self.font_label)
        self.x_type_menu.pack(anchor='w')
        self.x_type_menu.bind("<<ComboboxSelected>>", lambda e: self._on_agent_change())

        tk.Label(panel, text="Depth / Simulations",
                 font=self.font_small, bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(6, 2))
        self.x_param_var = tk.StringVar(value="5")
        self.x_param_menu = ttk.Combobox(panel, textvariable=self.x_param_var,
                                          values=["2", "5", "10"],
                                          state="readonly", width=14,
                                          font=self.font_label)
        self.x_param_menu.pack(anchor='w')

        tk.Frame(panel, bg="#444440", height=1).pack(fill='x', pady=10)

        # Player O settings
        tk.Label(panel, text="PLAYER  O", font=self.font_label,
                 bg=BG, fg=O_COLOR).pack(anchor='w', pady=(0, 4))

        self.o_type_var = tk.StringVar(value="MCTS")
        self.o_type_menu = ttk.Combobox(panel, textvariable=self.o_type_var,
                                         values=["Alpha-Beta", "MCTS"],
                                         state="readonly", width=14,
                                         font=self.font_label)
        self.o_type_menu.pack(anchor='w')
        self.o_type_menu.bind("<<ComboboxSelected>>", lambda e: self._on_agent_change())

        tk.Label(panel, text="Depth / Simulations",
                 font=self.font_small, bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(6, 2))
        self.o_param_var = tk.StringVar(value="500")
        self.o_param_menu = ttk.Combobox(panel, textvariable=self.o_param_var,
                                          values=["100", "300", "500", "1000"],
                                          state="readonly", width=14,
                                          font=self.font_label)
        self.o_param_menu.pack(anchor='w')

        tk.Frame(panel, bg="#444440", height=1).pack(fill='x', pady=10)

        # Speed slider
        tk.Label(panel, text="MOVE DELAY (ms)", font=self.font_label,
                 bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(0, 4))
        self.delay_var = tk.IntVar(value=600)
        tk.Scale(panel, variable=self.delay_var, from_=100, to=2000,
                 orient='horizontal', length=170, bg=BG, fg=TEXT_DARK,
                 highlightthickness=0, troughcolor=PANEL_BG,
                 font=self.font_small).pack(anchor='w')

        tk.Frame(panel, bg="#444440", height=1).pack(fill='x', pady=10)

        # Buttons row — Start + Stop
        btn_row = tk.Frame(panel, bg=BG)
        btn_row.pack(fill='x', pady=(0, 6))

        self.start_btn = tk.Button(
            btn_row, text="▶  START",
            font=self.font_btn, bg=BTN_START, fg=BTN_FG,
            relief='flat', cursor="hand2",
            padx=14, pady=16,
            command=self._start_game
        )
        self.start_btn.pack(side='left', padx=(0, 6), fill='x', expand=True)

        self.stop_btn = tk.Button(
            btn_row, text="■  STOP",
            font=self.font_btn, bg=BTN_STOP, fg=BTN_FG,
            relief='flat', cursor="hand2",
            padx=14, pady=16,
            command=self._stop_game,
            state='disabled'
        )
        self.stop_btn.pack(side='left', fill='x', expand=True)

        self.reset_btn = tk.Button(
            panel, text="↺  RESET",
            font=self.font_btn, bg=BTN_RESET, fg=BTN_FG,
            relief='flat', cursor="hand2",
            padx=14, pady=8,
            command=self._reset_game
        )
        self.reset_btn.pack(fill='x', pady=(0, 4))

        # Hover effects
        for btn, norm, hov in [
            (self.start_btn, BTN_START, BTN_HOV_START),
            (self.stop_btn,  BTN_STOP,  BTN_HOV_STOP),
            (self.reset_btn, BTN_RESET, BTN_HOV_RESET),
        ]:
            btn.bind("<Enter>", lambda e, b=btn, h=hov: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, n=norm: b.config(bg=n))

    def _build_board(self, parent):
        board_frame = tk.Frame(parent, bg=BG)
        board_frame.pack(side='left')

        self.canvas = tk.Canvas(board_frame,
                                width=BOARD_SIZE + PADDING * 2,
                                height=BOARD_SIZE + PADDING * 2,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

        # Piece counters below board
        counter_frame = tk.Frame(board_frame, bg=BG)
        counter_frame.pack(pady=(8, 0))

        tk.Label(counter_frame, text="X pieces:", font=self.font_small,
                 bg=BG, fg=TEXT_MID).grid(row=0, column=0, padx=4)
        self.x_count_var = tk.StringVar(value="0 / 3")
        tk.Label(counter_frame, textvariable=self.x_count_var,
                 font=self.font_label, bg=BG, fg=X_COLOR).grid(row=0, column=1, padx=4)

        tk.Label(counter_frame, text="O pieces:", font=self.font_small,
                 bg=BG, fg=TEXT_MID).grid(row=0, column=2, padx=(20, 4))
        self.o_count_var = tk.StringVar(value="0 / 3")
        tk.Label(counter_frame, textvariable=self.o_count_var,
                 font=self.font_label, bg=BG, fg=O_COLOR).grid(row=0, column=3, padx=4)

        self._draw_board()

    def _build_right_panel(self, parent):
        panel = tk.Frame(parent, bg=BG, width=180)
        panel.pack(side='left', fill='y', padx=(20, 0))
        panel.pack_propagate(False)

        tk.Label(panel, text="MOVE LOG", font=self.font_label,
                 bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(0, 4))

        log_frame = tk.Frame(panel, bg=PANEL_BG, relief='flat')
        log_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(log_frame, font=self.font_log,
                                bg=PANEL_BG, fg=TEXT_MID,
                                relief='flat', state='disabled',
                                wrap='word', width=20,
                                highlightthickness=0)
        self.log_text.pack(fill='both', expand=True, padx=6, pady=6)

        tk.Frame(panel, bg="#444440", height=1).pack(fill='x', pady=8)

        # Score board
        tk.Label(panel, text="SCORE", font=self.font_label,
                 bg=BG, fg=TEXT_LIGHT).pack(anchor='w', pady=(0, 4))

        score_frame = tk.Frame(panel, bg=PANEL_BG)
        score_frame.pack(fill='x')

        self.score = {'X': 0, 'O': 0, 'D': 0}
        self.score_vars = {
            'X': tk.StringVar(value="0"),
            'O': tk.StringVar(value="0"),
            'D': tk.StringVar(value="0"),
        }

        for col, (key, label, color) in enumerate([
            ('X', 'X', X_COLOR), ('D', 'D', TEXT_LIGHT), ('O', 'O', O_COLOR)
        ]):
            f = tk.Frame(score_frame, bg=PANEL_BG)
            f.grid(row=0, column=col, padx=8, pady=6)
            tk.Label(f, text=label, font=self.font_small,
                     bg=PANEL_BG, fg=color).pack()
            tk.Label(f, textvariable=self.score_vars[key],
                     font=self.font_status, bg=PANEL_BG, fg=color).pack()

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=PANEL_BG)
        bar.pack(fill='x', padx=0, pady=(14, 0))

        self.status_var = tk.StringVar(value="Ready — press START")
        tk.Label(bar, textvariable=self.status_var,
                 font=self.font_status, bg=PANEL_BG, fg=TEXT_DARK,
                 pady=8, padx=20).pack(side='left')

        self.turn_indicator = tk.Label(bar, text="",
                                       font=self.font_label, bg=PANEL_BG,
                                       fg=TEXT_MID, pady=8, padx=20)
        self.turn_indicator.pack(side='right')

    # ── Board Drawing ──────────────────────────────────────
    def _draw_board(self):
        c = self.canvas
        c.delete("all")
        o = PADDING

        # Outer board background (dark gray = window bg)
        # Board cell background (beige)
        c.create_rectangle(o, o, o + BOARD_SIZE, o + BOARD_SIZE,
                            fill=BOARD_BG, outline=LINE_COLOR, width=2)

        # Grid lines
        for i in range(1, 3):
            x = o + i * CELL_SIZE
            c.create_line(x, o, x, o + BOARD_SIZE,
                          fill="#7A6E60", width=3)
            y = o + i * CELL_SIZE
            c.create_line(o, y, o + BOARD_SIZE, y,
                          fill="#7A6E60", width=3)

        # Cell indices (darker and more visible)
        for i in range(9):
            r, col = divmod(i, 3)
            cx = o + col * CELL_SIZE + CELL_SIZE // 2
            cy = o + r * CELL_SIZE + CELL_SIZE // 2
            c.create_text(cx + 44, cy - 44, text=str(i),
                          font=self.font_small, fill="#6A5E50")

    def _render_state(self):
        state = self.state
        c = self.canvas
        o = PADDING

        self._draw_board()

        oldest_x = state.piece_history['X'][0] if state.piece_history['X'] else -1
        oldest_o = state.piece_history['O'][0] if state.piece_history['O'] else -1

        # Draw pieces
        for i, cell in enumerate(state.board):
            if cell is None:
                continue
            r, col = divmod(i, 3)
            cx = o + col * CELL_SIZE + CELL_SIZE // 2
            cy = o + r * CELL_SIZE + CELL_SIZE // 2

            if cell == 'X':
                is_oldest = (i == oldest_x and len(state.piece_history['X']) >= 3)
                color = OLDEST_X if is_oldest else X_COLOR
                # Draw X
                d = 28
                c.create_line(cx-d, cy-d, cx+d, cy+d,
                              fill=color, width=4, capstyle='round')
                c.create_line(cx+d, cy-d, cx-d, cy+d,
                              fill=color, width=4, capstyle='round')
                if is_oldest:
                    c.create_text(cx, cy + 38, text="oldest",
                                  font=self.font_small, fill=OLDEST_X)
            else:  # O
                is_oldest = (i == oldest_o and len(state.piece_history['O']) >= 3)
                color = OLDEST_O if is_oldest else O_COLOR
                r_circle = 28
                c.create_oval(cx-r_circle, cy-r_circle,
                              cx+r_circle, cy+r_circle,
                              outline=color, width=4)
                if is_oldest:
                    c.create_text(cx, cy + 38, text="oldest",
                                  font=self.font_small, fill=OLDEST_O)

        # Winning line
        if state.winner:
            line = state.get_winning_line()
            if line:
                positions = []
                for idx in line:
                    r2, col2 = divmod(idx, 3)
                    positions.append((o + col2 * CELL_SIZE + CELL_SIZE // 2,
                                      o + r2 * CELL_SIZE + CELL_SIZE // 2))
                c.create_line(positions[0][0], positions[0][1],
                              positions[2][0], positions[2][1],
                              fill=WIN_COLOR, width=4, capstyle='round')

        # Update piece counters
        self.x_count_var.set(f"{len(state.piece_history['X'])} / 3")
        self.o_count_var.set(f"{len(state.piece_history['O'])} / 3")

    # ── Game Control ───────────────────────────────────────
    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "human_vs_ai":
            self.x_type_menu.config(state="disabled")
            self.x_param_menu.config(state="disabled")
        else:
            self.x_type_menu.config(state="readonly")
            self.x_param_menu.config(state="readonly")

    def _on_agent_change(self):
        x_type = self.x_type_var.get()
        o_type = self.o_type_var.get()
        if x_type == "Alpha-Beta":
            self.x_param_menu.config(values=["2", "5", "10"])
            self.x_param_var.set("5")
        else:
            self.x_param_menu.config(values=["100", "300", "500", "1000"])
            self.x_param_var.set("500")
        if o_type == "Alpha-Beta":
            self.o_param_menu.config(values=["2", "5", "10"])
            self.o_param_var.set("5")
        else:
            self.o_param_menu.config(values=["100", "300", "500", "1000"])
            self.o_param_var.set("500")

    def _make_agent(self, player, agent_type, param):
        param = int(param)
        if agent_type == "Alpha-Beta":
            return AlphaBetaAgent(player, depth=param)
        else:
            return MCTSAgent(player, simulations=param)

    def _reset_game(self):
        if self.ai_thread and self.ai_thread.is_alive():
            self.game_running = False
            self.ai_thread.join(timeout=1)

        self.state = GameState()
        self.game_running = False
        self.human_turn = False
        self.move_log = []
        self._render_state()
        self._clear_log()
        self.status_var.set("Ready — press START")
        self.turn_indicator.config(text="")
        if hasattr(self, 'stop_btn'):
            self.stop_btn.config(state='disabled')
        if hasattr(self, 'start_btn'):
            self.start_btn.config(state='normal')

    def _start_game(self):
        self._reset_game()
        mode = self.mode_var.get()

        self.stop_btn.config(state='normal')
        self.start_btn.config(state='disabled')

        if mode == "human_vs_ai":
            self.agents['X'] = None
            self.agents['O'] = self._make_agent('O', self.o_type_var.get(),
                                                 self.o_param_var.get())
            self.human_turn = True
            self.status_var.set("Your turn — click a cell")
            self.turn_indicator.config(text="X → Human", fg=X_COLOR)
        else:
            self.agents['X'] = self._make_agent('X', self.x_type_var.get(),
                                                 self.x_param_var.get())
            self.agents['O'] = self._make_agent('O', self.o_type_var.get(),
                                                 self.o_param_var.get())
            self.game_running = True
            self.ai_thread = threading.Thread(target=self._ai_vs_ai_loop, daemon=True)
            self.ai_thread.start()

    def _stop_game(self):
        self.game_running = False
        self.human_turn = False
        self.status_var.set("Stopped — press START to play again")
        self.turn_indicator.config(text="", fg=TEXT_MID)
        self.stop_btn.config(state='disabled')
        self.start_btn.config(state='normal')

    def _ai_vs_ai_loop(self):
        move_num = 0
        while self.game_running and not self.state.is_terminal():
            player = self.state.current_player
            agent = self.agents[player]

            self.after(0, lambda p=player: self.status_var.set(
                f"Thinking... Player {p}"))
            self.after(0, lambda p=player: self.turn_indicator.config(
                text=f"{p} thinking…",
                fg=X_COLOR if p == 'X' else O_COLOR))

            move = agent.choose_move(self.state)
            if move is None:
                break

            self.state.apply_move(move)
            move_num += 1
            elapsed = getattr(agent, 'time_taken', 0)

            log_entry = f"#{move_num:02d} {player}→{move} ({elapsed:.3f}s)"
            self.move_log.append(log_entry)

            self.after(0, self._render_state)
            self.after(0, self._update_log)
            self.after(0, self._update_turn_status)

            time.sleep(self.delay_var.get() / 1000)

        self.after(0, self._on_game_over)

    def _on_click(self, event):
        if not self.human_turn or self.state.is_terminal():
            return
        if self.mode_var.get() != "human_vs_ai":
            return

        o = PADDING
        col = (event.x - o) // CELL_SIZE
        row = (event.y - o) // CELL_SIZE
        if not (0 <= col < 3 and 0 <= row < 3):
            return

        cell = row * 3 + col
        if self.state.board[cell] is not None:
            return

        self.human_turn = False
        self.state.apply_move(cell)
        move_num = len(self.move_log) + 1
        self.move_log.append(f"#{move_num:02d} X→{cell} (human)")
        self._render_state()
        self._update_log()

        if self.state.is_terminal():
            self._on_game_over()
            return

        # AI responds
        self.status_var.set("AI thinking...")
        self.turn_indicator.config(text="O thinking…", fg=O_COLOR)
        threading.Thread(target=self._ai_respond, daemon=True).start()

    def _ai_respond(self):
        agent = self.agents['O']
        move = agent.choose_move(self.state)
        if move is not None:
            self.state.apply_move(move)
            elapsed = getattr(agent, 'time_taken', 0)
            move_num = len(self.move_log) + 1
            self.move_log.append(f"#{move_num:02d} O→{move} ({elapsed:.3f}s)")
            self.after(0, self._render_state)
            self.after(0, self._update_log)

        if self.state.is_terminal():
            self.after(0, self._on_game_over)
        else:
            self.human_turn = True
            self.after(0, lambda: self.status_var.set("Your turn — click a cell"))
            self.after(0, lambda: self.turn_indicator.config(
                text="X → Human", fg=X_COLOR))

    def _update_turn_status(self):
        if self.state.is_terminal():
            return
        player = self.state.current_player
        color = X_COLOR if player == 'X' else O_COLOR
        self.status_var.set(f"Player {player}'s turn")
        self.turn_indicator.config(text=f"→ {player}", fg=color)

    def _on_game_over(self):
        self.game_running = False
        self.stop_btn.config(state='disabled')
        self.start_btn.config(state='normal')
        winner = self.state.winner
        if winner:
            self.score[winner] += 1
            self.score_vars[winner].set(str(self.score[winner]))
            color = X_COLOR if winner == 'X' else O_COLOR
            self.status_var.set(f"Player {winner} wins! 🎉")
            self.turn_indicator.config(text=f"{winner} wins", fg=color)
        else:
            self.score['D'] += 1
            self.score_vars['D'].set(str(self.score['D']))
            self.status_var.set("Draw — no winner")
            self.turn_indicator.config(text="draw", fg=TEXT_LIGHT)
        self._render_state()
        self.human_turn = False

    # ── Log ───────────────────────────────────────────────
    def _update_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        for entry in self.move_log[-30:]:
            self.log_text.insert('end', entry + "\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def _clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')


if __name__ == "__main__":
    app = App()
    app.mainloop()
