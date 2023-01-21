""" Random player class. Randomly chooses a direction and makes a move. """
from random import choices

from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import PlayerInterface


class RandomPlayer(PlayerInterface):
    """Random player class. Randomly chooses a direction and makes a move.""" ""

    def __init__(self, grid: Grid2048):
        super().__init__(grid)

    def play(self) -> bool:
        move = MoveFactory.create(
            choices(list(DIRECTION), weights=[0.6, 0.4, 1, 0.01], k=1)[0]
        )
        return self.grid.move(move)
