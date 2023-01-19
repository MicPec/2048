#!/usr/bin/env python
import argparse

from grid2048.grid2048 import Grid2048
from players.cycle_player import CyclePlayer
from players.expectimax_player import ExpectimaxPlayer
from players.mcts_player import MCTSPlayer
from players.minimax_player import MinimaxPlayer
from players.player import PlayerFactory
from players.random_player import RandomPlayer
from players.user_player import UserPlayer

WIDTH = 4
HEIGHT = 4

player_factory = PlayerFactory()
player_factory.register("user", UserPlayer)
player_factory.register("random", RandomPlayer)
player_factory.register("cycle", CyclePlayer)
player_factory.register("mcts", MCTSPlayer)
player_factory.register("expectimax", ExpectimaxPlayer)
player_factory.register("minimax", MinimaxPlayer)


class Game:
    def __init__(self, width: int, height: int, player_type: str) -> None:
        self.grid = Grid2048(width, height)
        self.player = player_factory.create(player_type, self.grid)

    def game_over(self) -> bool:
        return self.grid.no_moves


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cols", "--width", type=int, help="width of the grid")
    parser.add_argument("-r", "--rows", "--height", type=int, help="height of the grid")
    parser.add_argument("-p", "--player", type=str, help="player type")
    args = parser.parse_args()
    width = args.cols or 4
    height = args.rows or 4
    player = args.player or "user"
    if player not in player_factory.container.keys():
        raise ValueError(f"Invalid player type: {player!r}")
    print(f"Starting game with {width}x{height} grid and {player!r} player")
    # Start game
    game = Game(width, height, player)
    while not game.game_over():
        print(game.grid)
        print(f"score: {game.grid.score}")
        moved = game.player.play()
        if not moved:
            print("Invalid move")
    print("\n#############\n# GAME OVER #\n#############\n")
    print("Your score: ", game.grid.score)
    print("in ", game.grid.moves, " moves")
    print(game.grid)


if __name__ == "__main__":
    main()
