"""Abstract base class for players and AI players"""
from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import product
from typing import Callable

from grid2048.grid2048 import Grid2048


class PlayerInterface(ABC):
    """Abstract base class for players"""

    def __init__(self, grid: Grid2048):
        self.grid = grid

    @abstractmethod
    def play(self, *args, **kwargs) -> bool:
        # make a move and return True if the grid has changed
        # eg. return self.grid.shift_left()
        raise NotImplementedError


class AIPlayer(PlayerInterface):
    """Abstract base class for AI players"""

    @abstractmethod
    def evaluate(self, grid, move):
        """Returns the score of the grid."""
        raise NotImplementedError

    # def move(
    #     self, grid, direction: str, add_tile: bool = False
    # ) -> tuple[Grid2048, bool]:
    #     new_grid = deepcopy(grid)
    #     moved = False
    #     if direction == "u":
    #         moved = new_grid.shift_up(add_tile=add_tile)
    #     elif direction == "d":
    #         moved = new_grid.shift_down(add_tile=add_tile)
    #     elif direction == "l":
    #         moved = new_grid.shift_left(add_tile=add_tile)
    #     elif direction == "r":
    #         moved = new_grid.shift_right(add_tile=add_tile)
    #     return (new_grid, moved) if moved else (grid, False)

    # def grid_variance(self, grid):
    #     """Returns the variance of all cells in the grid.
    #     Values are normalized to be between 0 and 1.
    #     Higher values mean a more even distribution of values."""
    #     mean = self.grid_mean(grid)
    #     variance = sum((cell - mean) ** 2 for row in grid.data for cell in row)
    #     return 1000 / variance if variance != 0 else 0


class PlayerFactory:
    """Factory for creating players"""

    register_fn: dict[str, Callable[..., PlayerInterface]] = {}

    def register(self, player_type: str, fn: Callable[..., PlayerInterface]) -> None:
        PlayerFactory.register_fn[player_type] = fn

    def create(self, player_type: str, grid: Grid2048) -> PlayerInterface:
        try:
            return PlayerFactory.register_fn[player_type](grid)
        except KeyError:
            raise ValueError(f"Invalid player type: {player_type!r}") from None
