"""User player class and kivy player class"""
from grid2048 import Grid2048
from players.player import PlayerInterface


class UserPlayer(PlayerInterface):
    """User player class"""

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
        while True:
            direction = input("Enter a direction (u,d,l,r): ")
            if direction in self.dirs:
                break
            print("Invalid direction")
        return self.moves[direction]()


class KivyPlayer(PlayerInterface):
    """User player class for kivy app"""

    dirs = [273, 274, 276, 275]

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            273: self.grid.shift_up,
            274: self.grid.shift_down,
            276: self.grid.shift_left,
            275: self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        while True:
            direction = kwargs.get("dir")
            if direction in self.dirs:
                break
            print("Invalid direction")
        return self.moves[direction]()
