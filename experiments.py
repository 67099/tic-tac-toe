"""
experiments.py - Run AI vs AI experiments and collect statistics
"""

import time
from game import GameState
from alpha_beta import AlphaBetaAgent
from mcts import MCTSAgent


def run_game(agent_x, agent_o, max_moves=200, verbose=False):
    """
    Run a single game between two agents.
    Returns dict with result info.
    """
    state = GameState()
    agents = {'X': agent_x, 'O': agent_o}
    move_times = {'X': [], 'O': []}
    nodes = {'X': 0, 'O': 0}
    total_moves = 0

    while not state.is_terminal() and total_moves < max_moves:
        player = state.current_player
        agent = agents[player]

        t0 = time.time()
        move = agent.choose_move(state)
        elapsed = time.time() - t0

        move_times[player].append(elapsed)
        nodes[player] += getattr(agent, 'nodes_explored', 0)

        if move is None:
            break

        state.apply_move(move)
        total_moves += 1

        if verbose:
            print(f"\nMove {total_moves}: Player {player} → cell {move}")
            print(state)

    winner = state.winner
    return {
        'winner': winner,
        'total_moves': total_moves,
        'avg_time_x': sum(move_times['X']) / len(move_times['X']) if move_times['X'] else 0,
        'avg_time_o': sum(move_times['O']) / len(move_times['O']) if move_times['O'] else 0,
        'nodes_x': nodes['X'],
        'nodes_o': nodes['O'],
        'draw': winner is None,
    }


def run_experiment(agent_x_factory, agent_o_factory, num_games=20, label="Experiment"):
    """
    Run multiple games and aggregate statistics.
    Factories are callables that return new agent instances.
    """
    results = {'X': 0, 'O': 0, 'draw': 0}
    all_times_x, all_times_o = [], []
    all_moves = []

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"  Games: {num_games}")
    print(f"{'='*50}")

    for i in range(num_games):
        ax = agent_x_factory()
        ao = agent_o_factory()
        result = run_game(ax, ao)

        if result['winner'] == 'X':
            results['X'] += 1
        elif result['winner'] == 'O':
            results['O'] += 1
        else:
            results['draw'] += 1

        all_times_x.append(result['avg_time_x'])
        all_times_o.append(result['avg_time_o'])
        all_moves.append(result['total_moves'])

        print(f"  Game {i+1:02d}: Winner={result['winner'] or 'Draw'} | "
              f"Moves={result['total_moves']} | "
              f"Time X={result['avg_time_x']:.4f}s | "
              f"Time O={result['avg_time_o']:.4f}s")

    print(f"\n  Results → X wins: {results['X']} | O wins: {results['O']} | Draws: {results['draw']}")
    print(f"  Avg moves/game: {sum(all_moves)/len(all_moves):.1f}")
    print(f"  Avg time X: {sum(all_times_x)/len(all_times_x):.4f}s")
    print(f"  Avg time O: {sum(all_times_o)/len(all_times_o):.4f}s")

    return {
        'label': label,
        'results': results,
        'avg_moves': sum(all_moves) / len(all_moves),
        'avg_time_x': sum(all_times_x) / len(all_times_x),
        'avg_time_o': sum(all_times_o) / len(all_times_o),
    }


def run_all_experiments(num_games=20):
    """Run all required experiment matchups."""
    experiments = []

    # Alpha-Beta k=2 vs Alpha-Beta k=2
    experiments.append(run_experiment(
        lambda: AlphaBetaAgent('X', depth=2),
        lambda: AlphaBetaAgent('O', depth=2),
        num_games=num_games,
        label="Alpha-Beta (k=2) vs Alpha-Beta (k=2)"
    ))

    # Alpha-Beta k=5 vs Alpha-Beta k=5
    experiments.append(run_experiment(
        lambda: AlphaBetaAgent('X', depth=5),
        lambda: AlphaBetaAgent('O', depth=5),
        num_games=num_games,
        label="Alpha-Beta (k=5) vs Alpha-Beta (k=5)"
    ))

    # Alpha-Beta k=10 vs Alpha-Beta k=10
    experiments.append(run_experiment(
        lambda: AlphaBetaAgent('X', depth=10),
        lambda: AlphaBetaAgent('O', depth=10),
        num_games=num_games,
        label="Alpha-Beta (k=10) vs Alpha-Beta (k=10)"
    ))

    # Alpha-Beta k=5 vs MCTS
    experiments.append(run_experiment(
        lambda: AlphaBetaAgent('X', depth=5),
        lambda: MCTSAgent('O', simulations=500),
        num_games=num_games,
        label="Alpha-Beta (k=5) vs MCTS (500 sims)"
    ))

    # MCTS vs MCTS
    experiments.append(run_experiment(
        lambda: MCTSAgent('X', simulations=300),
        lambda: MCTSAgent('O', simulations=500),
        num_games=num_games,
        label="MCTS (300 sims) vs MCTS (500 sims)"
    ))

    return experiments


if __name__ == "__main__":
    print("Running all experiments (20 games each)...")
    run_all_experiments(num_games=20)
