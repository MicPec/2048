"""Cycle player class. Cycles through the directions and makes a move."""
from itertools import cycle

from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import PlayerInterface


class CyclePlayer(PlayerInterface):
    """Cycle player class. Cycles through the directions and makes a move."""

    cyc = cycle(list(DIRECTION))

    def __init__(self, grid: Grid2048):
        super().__init__(grid)

    def play(self) -> bool:
        move = MoveFactory.create(next(self.cyc))
        return self.grid.move(move)
