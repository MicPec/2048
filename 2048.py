#!/usr/bin/env python
"""2048 game using the grid2048 library"""
import argparse

from grid2048 import Grid2048
from players import player_factory

WIDTH = 4
HEIGHT = 4


class Game:
    """2048 game class"""

    def __init__(self, width: int, height: int, player_type: str) -> None:
        self.grid = Grid2048(width, height)
        self.player = player_factory.create(player_type, self.grid)

    def game_over(self) -> bool:
        """Check if the game is over"""
        return self.grid.no_moves


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cols", "--width", type=int, help="width of the grid")
    parser.add_argument("-r", "--rows", "--height", type=int, help="height of the grid")
    parser.add_argument("-p", "--player", type=str, help="player type")
    args = parser.parse_args()
    width = args.cols or WIDTH
    height = args.rows or HEIGHT
    player = args.player or "user"
    if player not in player_factory.container:
        raise ValueError(f"Invalid player type: {player!r}")

    print(f"Starting game with {width}x{height} grid and {player!r} player")
    # Start game
    game = Game(width, height, player)
    print("\033[H\033[J")
    while not game.game_over():
        print("\033[H\033[J")
        # print("\x1b[H")
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
