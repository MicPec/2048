"""Grid2048 module. Contains the Grid2048 class and the Move class."""
from enum import Enum
from random import choice, choices
from typing import Any, Callable, TypeVar

import numpy as np

STATE = Enum("STATE", "IDLE RUNNING")
DIRECTION = Enum("DIRECTION", "UP DOWN LEFT RIGHT")

# Grid2048 = TypeVar("Grid2048")
Move = TypeVar("Move")


class Grid2048:
    """2048 grid class"""

    def __init__(self, width=4, height=4):
        self.state = STATE.IDLE
        self._last_move = None
        self.width = width
        self.height = height
        self._grid = np.array([])
        self.reset()

    def __str__(self):
        # Find the length of the longest number
        val = np.max(self._grid)
        # Create the string
        l = len(str(val))
        s = "\n" + "-" * (l + 1) * self.width + "-\n"
        for row in self._grid:
            s += "|"
            for tile in row:
                strtile = f"{tile: ^{l}}" if tile > 0 else " "
                s += f"{strtile:{l}}|"
            s += "\n" + "-" * (l + 1) * self.width + "-\n"
        return s

    def __repr__(self):
        return f"Grid2048({self.width}, {self.height}): {self._grid}"

    def __getitem__(self, key):
        return self._grid[key]

    def __setitem__(self, key, value):
        self._grid[key] = value

    def __eq__(self, other):
        return np.array_equal(self._grid, other._grid)

    @property
    def data(self) -> np.ndarray:
        return self._grid

    @property
    def last_move(self) -> Move:
        if self._last_move is None:
            raise ValueError("No move has been made yet")
        return self._last_move

    @data.setter
    def data(self, value: np.ndarray) -> None:
        if not isinstance(value, np.ndarray):
            raise TypeError("Grid data must be a numpy array of integers")
        if value.shape != (self.height, self.width):
            raise ValueError(
                f"Invalid grid dimensions:{self.width}x{self.height} != {value.shape}"
            )
        self._grid = value

    def reset(self) -> None:
        """Reset the grid"""
        self._grid = np.zeros((self.height, self.width), int)
        self.score = 0
        self.moves = 0
        self.add_random_tile(self.get_empty_fields())
        self.add_random_tile(self.get_empty_fields())
        self.state = STATE.IDLE

    def get_empty_fields(self) -> list[tuple[Any]]:
        """Return a list of tuples containing the coordinates of empty fields"""
        return list(zip(*np.nonzero(self._grid == 0)))

    def add_random_tile(self, empty_fields: list) -> None:
        """Add a random tile to the grid"""
        if empty_fields:
            row, col = choice(empty_fields)
            self._grid[row, col] = choices([2, 4], [0.9, 0.1])[0]

    @property
    def no_moves(self) -> bool:
        """Check if there are any moves left"""
        for row, col in np.ndindex(self.height, self.width):
            if self._grid[row, col] == 0:
                return False
            if (
                row < self.height - 1
                and self._grid[row, col] == self._grid[row + 1, col]
            ):
                return False
            if (
                col < self.width - 1
                and self._grid[row, col] == self._grid[row, col + 1]
            ):
                return False
        return True

    def move(self, move: Move, add_tile: bool = True) -> bool:
        """Execute a move and return True if the move is valid."""
        if self.state == STATE.RUNNING or self.no_moves:
            return False
        self.state = STATE.RUNNING
        move(self)
        self._last_move = move
        self.score += move.score
        if move.is_valid:
            self.moves += 1
            if add_tile:
                self.add_random_tile(self.get_empty_fields())
        self.state = STATE.IDLE
        return move.is_valid


class Move:
    """Move class. Makes a move in a given direction."""

    def __init__(self, direction, dir_fn: Callable):
        self._direction = direction
        self.score = 0
        self.dir_fn = dir_fn
        self._called = False
        self._is_valid = False

    def __call__(self, grid: Grid2048) -> Grid2048:
        """Execute the move"""
        cmp = np.copy(grid.data)
        self.dir_fn(self, grid)
        self._called = True
        # It`s done this way, because I could not find a better/faster way to do it.
        self._is_valid = not np.array_equal(grid.data, cmp)
        return grid

    @property
    def direction(self) -> DIRECTION:
        """Return the direction of the move"""
        return self._direction

    @property
    def is_valid(self) -> bool:
        """Return True if the move is valid. Call after the move has been executed."""
        if not self._called:
            raise ValueError("Move has not been called yet")
        return self._is_valid

    def shift_up(self, grid: Grid2048) -> Grid2048:
        """Shift the grid up combining tiles"""
        matrix = grid.data
        for col in range(len(matrix[0])):
            # Create a temporary list to store the non-zero tiles
            lst = matrix[:, col]
            temp = list(lst[lst != 0])
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            if temp:
                matrix[:, col] = 0
                matrix[: len(temp), col] = temp
        return grid

    def shift_down(self, grid: Grid2048) -> Grid2048:
        """Shift the grid down combining tiles"""
        matrix = grid.data
        for col in range(len(matrix[0])):
            # Create a temporary list to store the non-zero tiles
            lst = matrix[:, col]
            temp = list(lst[lst != 0])
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            if temp:
                matrix[::-1, col] = 0
                matrix[-len(temp) :, col] = temp
        return grid

    def shift_left(self, grid: Grid2048) -> Grid2048:
        """Shift the grid left combining tiles"""
        matrix = grid.data
        for col in range(matrix.shape[0]):
            # Create a temporary list to store the non-zero tiles
            lst = matrix[col, :]
            temp = list(lst[lst != 0])
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            if temp:
                matrix[col, :] = 0
                matrix[col, : len(temp)] = temp
        return grid

    def shift_right(self, grid: Grid2048) -> Grid2048:
        """Shift the grid right combining tiles"""
        matrix = grid.data
        for col in range(matrix.shape[0]):
            # Create a temporary list to store the non-zero tiles
            lst = matrix[col, ::-1]
            temp = list(lst[lst != 0])
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            if temp:
                matrix[col, :] = 0
                matrix[col, -len(temp) :] = temp[::-1]
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
    def create(cls, direction: DIRECTION):
        try:
            return Move(direction, cls.move_directions[direction.name])
        except KeyError as exc:
            raise ValueError("Invalid direction") from exc
        except Exception as exc:
            raise exc
