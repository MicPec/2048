""" Random player class. Randomly chooses a direction and makes a move. """
from itertools import cycle
from random import choices

from grid2048 import Grid2048
from players.player import PlayerInterface


class RandomPlayer(PlayerInterface):
    """Random player class. Randomly chooses a direction and makes a move.""" ""

    dirs = ["u", "d", "l", "r"]

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[choices(self.dirs, weights=[0.5, 0.5, 1, 0.01], k=1)[0]]()


class CyclePlayer(PlayerInterface):
    """Cycle player class. Cycles through the directions and makes a move."""

    dirs = ["u", "r", "d", "l"]
    cyc = cycle(dirs)

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[next(self.cyc)]()
