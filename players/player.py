"""Abstract base classes for players and AI players"""
from abc import ABC, abstractmethod
from typing import Callable

from grid2048.grid2048 import Grid2048, Move


class PlayerInterface(ABC):
    """Abstract base class for players"""

    def __init__(self, grid: Grid2048):
        self.grid = grid

    @abstractmethod
    def play(self, *args, **kwargs) -> bool:
        """Make a move and return True if the grid has changed"""
        # example:
        # move = MoveFactory.create(MOVES.UP)
        # return self.grid.move(move)
        raise NotImplementedError


class AIPlayer(PlayerInterface):
    """Abstract base class for AI players"""

    @abstractmethod
    def evaluate(self, grid: Grid2048, move: Move = None, *args, **kwargs):
        """Returns the score of the grid."""
        raise NotImplementedError


class PlayerFactory:
    """Factory for creating players"""

    container: dict[str, Callable[..., PlayerInterface]] = {}

    def register(self, player_type: str, fn: Callable[..., PlayerInterface]) -> None:
        PlayerFactory.container[player_type] = fn

    def create(self, player_type: str, grid: Grid2048) -> PlayerInterface:
        try:
            return PlayerFactory.container[player_type](grid)
        except KeyError:
            raise ValueError(f"Invalid player type: {player_type!r}") from None
