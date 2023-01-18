from enum import Enum
import itertools
from copy import deepcopy
from random import choice
from typing import Callable, TypeVar


STATES = Enum("STATE", "IDLE RUNNING")
MOVES = Enum("MOVES", "UP DOWN LEFT RIGHT")

Grid2048 = TypeVar("Grid2048")
Move = TypeVar("Move")


class Grid2048:
    state = STATES.IDLE

    def __init__(self, width=4, height=4):
        self.last_move = None
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

    def __eq__(self, other):
        return self._grid == other._grid

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

    @property
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

    def move(self, move: Move, add_tile: bool = True) -> bool:
        if self.state == STATES.RUNNING or self.no_moves:
            return False
        self.state = STATES.RUNNING
        move(self)
        self.score += move.score
        if move.is_valid:
            self.moves += 1
            if add_tile:
                self.add_random_tile(self.get_empty_fields())
        self.state = STATES.IDLE
        return bool(move.is_valid)


class Move:
    def __init__(self, dir_fn: Callable):
        self.score = 0
        self.dir_fn = dir_fn
        self._grid = None
        self._is_valid = False

    def __call__(self, grid: Grid2048) -> Grid2048:
        self._grid = self.dir_fn(self, grid)
        return grid

    @property
    def is_valid(self) -> bool:
        if self._grid is None:
            raise ValueError("Move has not been called yet")
        return self._is_valid

    def shift_up(self, grid: Grid2048) -> Grid2048:
        matrix = grid.data
        for col in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for row in range(len(matrix[0]))
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            for i in range(len(matrix[0])):
                matrix[i][col] = 0
            j = 0
            for row in range(len(matrix[0])):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
                    self._is_valid = True
        return grid

    def shift_down(self, grid: Grid2048) -> Grid2048:
        matrix = grid.data
        for col in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for row in range(len(matrix[0]) - 1, -1, -1)
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            for k in range(len(matrix[0])):
                matrix[k][col] = 0
            j = 0
            for row in range(len(matrix[0]) - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
                    self._is_valid = True
        return grid

    def shift_left(self, grid: Grid2048) -> Grid2048:
        matrix = grid.data
        for row in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for col in range(len(matrix[0]))
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the row
            for k in range(len(matrix[0])):
                matrix[row][k] = 0
            j = 0
            for col in range(len(matrix[0])):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
                    self._is_valid = True
        return grid

    def shift_right(self, grid: Grid2048) -> Grid2048:
        matrix = grid.data
        for row in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for col in range(len(matrix[0]) - 1, -1, -1)
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the row
            for k in range(len(matrix[0])):
                matrix[row][k] = 0
            j = 0
            for col in range(len(matrix[0]) - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
                    self._is_valid = True
        return grid

    def combine_tiles(self, temp: list[int]) -> int:
        """Combine the tiles and count the score"""
        i = 0
        score = 0
        while i < len(temp) - 1:
            if temp[i] == temp[i + 1]:
                temp[i] *= 2
                temp.pop(i + 1)
                score += temp[i]
                self._is_valid = True
            i += 1
        return score


class MoveFactory:
    """Factory class for creating Move objects"""

    move_directions = {
        "UP": Move.shift_up,
        "DOWN": Move.shift_down,
        "LEFT": Move.shift_left,
        "RIGHT": Move.shift_right,
    }

    def __init__(self, grid):
        self.grid = grid.data

    @classmethod
    def create(cls, direction: MOVES):
        try:
            return Move(cls.move_directions[direction.name])
        except KeyError:
            raise ValueError("Invalid direction")
        except Exception as e:
            raise e
