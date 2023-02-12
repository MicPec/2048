#!/usr/bin/env python
import argparse

from grid2048 import helpers
from grid2048.grid2048 import Grid2048
from players.cycle_player import CyclePlayer
from players.expectimax_player import ExpectimaxPlayer
from players.mcts_player import MCTSPlayer
from players.minimax_player import MinimaxPlayer
from players.player import PlayerFactory
from players.random_player import RandomPlayer

WIDTH = 4
HEIGHT = 4

player_factory = PlayerFactory()
player_factory.register("random", RandomPlayer)
player_factory.register("cycle", CyclePlayer)
player_factory.register("mcts", MCTSPlayer)
player_factory.register("expectimax", ExpectimaxPlayer)
player_factory.register("minimax", MinimaxPlayer)


stats = []


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--player", type=str, help="player type")
    parser.add_argument("-i", "--iter", type=str, help="number of iterations")
    args = parser.parse_args()
    ai_player = args.player or "random"
    iterations = args.iter or 10
    if ai_player not in player_factory.container.keys():
        raise ValueError(f"Invalid player type: {ai_player!r}")
    # Start game
    print(
        f"Starting {iterations} games with {WIDTH}x{HEIGHT} grid and {ai_player!r} player"
    )
    for i in range(iterations):
        grid = Grid2048(WIDTH, HEIGHT)
        player = player_factory.create(ai_player, grid)
        while not grid.no_moves:
            print(f"Game: {i+1} | score: {grid.score} \r", end="")
            player.play()
        stats.append(
            {
                "no": i + 1,
                "player": ai_player,
                "score": grid.score,
                "max_tile": helpers.max_tile(grid),
                "moves": grid.moves,
            }
        )
        print(
            f"\nGame {i+1} is over. Score: {grid.score} in {grid.moves} moves, max tile: {helpers.max_tile(grid)}"
        )
    print("*" * 80)
    print(f"Total games: {len(stats)}")
    print(f"Max tile: {max(s['max_tile'] for s in stats)}")
    print(f"Max score: {max(s['score'] for s in stats)}")
    print(f"Min score: {min(s['score'] for s in stats)}")
    print(f"Average score: {sum(s['score'] for s in stats) / len(stats)}")
    print(f"Average moves: {sum(s['moves'] for s in stats) / len(stats)}")
    print(f"Wins count: {len([s for s in stats if s['max_tile'] == 2048])}")
    print(
        f"Percentage of wins: {len([s for s in stats if s['max_tile'] == 2048]) / len(stats) * 100}%"
    )


if __name__ == "__main__":
    main()
