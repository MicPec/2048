import enum
import itertools
from copy import deepcopy
from random import choice

STATES = enum.Enum("STATE", "IDLE RUNNING")


class Grid2048:
    state = STATES.IDLE

    def __init__(self, width=4, height=4):
        self.width = width
        self.height = height
        self.reset()

    def __str__(self):
        # Find the length of the longest number
        val = 0
        for row in self._grid:
            val = max(row) if max(row) > val else val
        # Create the string
        l = len(str(val))
        s = "\n" + "-" * (l + 1) * self.width + "-\n"
        for row in self._grid:
            s += "|"
            for col in row:
                strcol = str(col).center(l) if col > 0 else " "
                s += f"{strcol:{l}}|"
            s += "\n" + "-" * (l + 1) * self.width + "-\n"
        return s

    def __repr__(self):
        return f"Grid2048({self.width}, {self.height}): {self._grid}"

    def __getitem__(self, key):
        return self._grid[key]

    def __setitem__(self, key, value):
        self._grid[key] = value

    @property
    def data(self) -> list[list[int]]:
        return self._grid

    @data.setter
    def data(self, value: list[list[int]]):
        if not all(isinstance(row, list) for row in value):
            raise TypeError("Grid data must be a list of lists")
        if len(value) != self.height or len(value[0]) != self.width:
            raise ValueError(
                f"Invalid grid dimensions:{self.width}x{self.height} != {len(value)}x{len(value[0])}"
            )
        self._grid = value

    def reset(self) -> None:
        """Reset the grid"""
        self._grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.moves = 0
        self.add_random_tile(self.get_empty_fields())
        self.state = STATES.IDLE

    def get_empty_fields(self) -> list[tuple[int, int]]:
        """Return a list of tuples containing the coordinates of empty fields"""
        return [
            (row, col)
            for row, col in itertools.product(range(self.height), range(self.width))
            if self._grid[row][col] == 0
        ]

    def add_random_tile(self, empty_fields: list) -> None:
        """Add a random tile to the grid"""
        if empty_fields:
            row, col = choice(empty_fields)
            self._grid[row][col] = 2

    def combine_tiles(self, temp: list[int]) -> list[int]:
        """Combine the tiles and count the score"""
        i = 0
        while i < len(temp) - 1:
            if temp[i] == temp[i + 1]:
                temp[i] *= 2
                temp.pop(i + 1)
                self.score += temp[i]
            i += 1
        return temp

    def no_moves(self) -> bool:
        """Check if there are any moves left"""
        for col, row in itertools.product(range(self.width), range(self.height)):
            if self._grid[row][col] == 0:
                return False
            if (
                row < self.height - 1
                and self._grid[row][col] == self._grid[row + 1][col]
            ):
                return False
            if (
                col < self.width - 1
                and self._grid[row][col] == self._grid[row][col + 1]
            ):
                return False
        return True

    def moved(self, shifted: list[list[int]], *args, **kwargs) -> bool:
        """Check if the grid has been shifted and add a new tile"""
        if shifted != self._grid:
            self._grid = deepcopy(shifted)
            if kwargs.get("add_tile", True):
                self.add_random_tile(self.get_empty_fields())
            self.moves += 1
            self.state = STATES.IDLE
            return True
        self.state = STATES.IDLE
        return False

    def shift_up(self, *args, **kwargs) -> bool:
        self.state = STATES.RUNNING
        cmp = deepcopy(self._grid)
        for col in range(self.width):
            # Create a temporary list to store the non-zero tiles
            temp = [cmp[row][col] for row in range(self.height) if cmp[row][col] != 0]
            # Combine the tiles
            temp = self.combine_tiles(temp)

            # Rebuild the column
            for i in range(self.height):
                cmp[i][col] = 0
            j = 0
            for row in range(self.height):
                if j < len(temp) and temp[j] != 0:
                    cmp[row][col] = temp[j]
                    j += 1
        return bool(self.moved(cmp, *args, add_tile=True))

    def shift_down(self, *args, **kwargs) -> bool:
        self.state = STATES.RUNNING
        cmp = deepcopy(self._grid)
        for col in range(self.width):
            # Create a temporary list to store the non-zero tiles
            temp = [
                cmp[row][col]
                for row in range(self.height - 1, -1, -1)
                if cmp[row][col] != 0
            ]
            # Combine the tiles
            temp = self.combine_tiles(temp)
            # Rebuild the column
            for k in range(self.height):
                cmp[k][col] = 0
            j = 0
            for row in range(self.height - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    cmp[row][col] = temp[j]
                    j += 1
        return bool(self.moved(cmp, *args, add_tile=True))

    def shift_left(self, *args, **kwargs) -> bool:
        self.state = STATES.RUNNING
        cmp = deepcopy(self._grid)
        for row in range(self.height):
            # Create a temporary list to store the non-zero tiles
            temp = [cmp[row][col] for col in range(self.width) if cmp[row][col] != 0]
            # Combine the tiles
            temp = self.combine_tiles(temp)
            # Rebuild the row
            for k in range(self.width):
                cmp[row][k] = 0
            j = 0
            for col in range(self.width):
                if j < len(temp) and temp[j] != 0:
                    cmp[row][col] = temp[j]
                    j += 1
        return bool(self.moved(cmp, *args, add_tile=True))

    def shift_right(self, *args, **kwargs) -> bool:
        self.state = STATES.RUNNING
        cmp = deepcopy(self._grid)
        for row in range(self.height):
            # Create a temporary list to store the non-zero tiles
            temp = [
                cmp[row][col]
                for col in range(self.width - 1, -1, -1)
                if cmp[row][col] != 0
            ]
            # Combine the tiles
            temp = self.combine_tiles(temp)
            # Rebuild the row
            for k in range(self.width):
                cmp[row][k] = 0
            j = 0
            for col in range(self.width - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    cmp[row][col] = temp[j]
                    j += 1
        return bool(self.moved(cmp, *args, add_tile=True))
