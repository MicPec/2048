"""Abstract base class for players and AI players"""
from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import product
from typing import Callable

from grid2048 import Grid2048


class PlayerInterface(ABC):
    """Abstract base class for players"""

    def __init__(self, grid: Grid2048):
        self.grid = grid

    @abstractmethod
    def play(self, *args, **kwargs) -> bool:
        # make a move and return True if the grid has changed
        # eg. return self.grid.shift_left()
        ...


class AIPlayer(PlayerInterface):
    """Abstract base class for AI players"""

    @abstractmethod
    def evaluate(self, grid):
        """Returns the score of the grid."""
        ...

    def move(
        self, grid, direction: str, add_tile: bool = False
    ) -> tuple[Grid2048, bool]:
        new_grid = deepcopy(grid)
        moved = False
        if direction == "u":
            moved = new_grid.shift_up(add_tile=add_tile)
        elif direction == "d":
            moved = new_grid.shift_down(add_tile=add_tile)
        elif direction == "l":
            moved = new_grid.shift_left(add_tile=add_tile)
        elif direction == "r":
            moved = new_grid.shift_right(add_tile=add_tile)
        return (new_grid, moved) if moved else (grid, False)

    def normalize(self, values: list[any]) -> list[float]:
        """Normalize a list of numbers"""
        maxval = max(values)
        minval = min(values)
        return [(x - minval) / (maxval - minval) for x in values]

    def zeros(self, grid):
        """Returns the number of empty cells in the grid.
        Values are normalized to be between 0 and 1."""
        return len(
            [cell for row in grid.data for cell in row if cell == 0]
        ) / self.grid_size(grid)

    def monotonicity(self, grid):
        """Returns the number of monotonic rows and columns in the grid.
        It shows how well the numbers are ordered,
        either increasing, decreasing or equal in each row and column.
        For small values, result is small, so this affects the big values more."""
        score = 0
        for row in grid.data:
            for i in range(len(row) - 1):
                if (
                    row[i] == row[i + 1]
                    or row[i] == row[i + 1] * 2
                    or row[i] == row[i + 1] // 2
                    and row[i] != 0
                ):
                    score += row[i]

        for col in zip(*grid.data):
            for i in range(len(col) - 1):
                if (
                    col[i] == col[i + 1]
                    or col[i] == col[i + 1] * 2
                    or col[i] == col[i + 1] // 2
                    and col[i] != 0
                ):
                    score += col[i]
        return score / self.grid_size(grid)

    def smoothness(self, grid):
        """Returns the smoothness of the grid.
        It works by iterating through the grid, and comparing each element
        with its neighbors, and adding the absolute difference between them.
        Values are normalized to be between 0 and 1."""
        smoothness_count = 0
        for i, j in product(range(grid.height - 1), range(grid.width - 1)):
            if grid[i][j] != grid[i + 1][j] and grid[i][j] != 0 and grid[i + 1][j] != 0:
                smoothness_count += abs(grid[i][j] - grid[i + 1][j])
            if grid[i][j] != grid[i][j + 1] and grid[i][j] != 0 and grid[i][j + 1] != 0:
                smoothness_count += abs(grid[i][j] - grid[i][j + 1])
        return 1 / smoothness_count if smoothness_count != 0 else 0

    def pairs(self, grid):
        """Returns the sum of the pairs in the grid.
        That includes pairs with holes in between."""
        pairs_count = 0
        for col in range(grid.width):
            tmp = [x for x in grid.data[col] if x != 0]
            for val in range(len(tmp) - 1):
                if tmp[val] == tmp[val + 1]:
                    pairs_count += tmp[val]
        for row in range(grid.height):
            tmp = [x for x in grid.data[row] if x != 0]
            for val in range(len(tmp) - 1):
                if tmp[val] == tmp[val + 1]:
                    pairs_count += tmp[val]
        return pairs_count / self.grid_size(grid)

    def flatness(self, grid):
        """Returns the flatness of the grid.
        It works by iterating through the grid and adding
        the absolute difference between each tile and the max
        tile of its row. Higher values are better."""
        flatness_count = 0
        for row in grid.data:
            for cell in row:
                if cell != 0:
                    flatness_count += abs(cell - max(row))
        return flatness_count / self.grid_size(grid)

    def high_vals_on_edge(self, grid, divider=256):
        """Returns the number of high values that are on the edge the grid.
        Values are normalized to be between 0 and 1."""
        high_vals = 0
        for i, j in product(range(grid.height), range(grid.width)):
            if grid[i][j] == 0:
                continue
            if grid[i][j] >= divider:
                if i == 0 or j == 0 or i == grid.height - 1 or j == grid.width - 1:
                    high_vals += 1
        return high_vals / ((2 * (grid.width - 1)) + (2 * (grid.height - 1)))

    def high_to_low(self, grid, divider=256) -> float:
        """Returns the ratio beteen the high and low values in the grid.
        Values are normalized to be between 0 and 1."""
        high_vals = 0
        low_vals = 0
        for i, j in product(range(grid.height), range(grid.width)):
            if grid[i][j] == 0:
                continue
            if grid[i][j] >= divider:
                high_vals += 1
            else:
                low_vals += 1
        ratio = high_vals / low_vals if low_vals != 0 else high_vals
        return ratio / (high_vals + low_vals)

    def low_to_high(self, grid, divider=256) -> float:
        """Returns the ratio beteen the low and high values in the grid.
        Values are normalized to be between 0 and 1."""
        high_vals = 0
        low_vals = 0
        for i, j in product(range(grid.height), range(grid.width)):
            if grid[i][j] == 0:
                continue
            if grid[i][j] >= divider:
                high_vals += 1
            else:
                low_vals += 1
        ratio = low_vals / high_vals if high_vals != 0 else low_vals
        return ratio / (high_vals + low_vals)

    def zero_field(self, grid):
        """Returns the number of empty fields that are surrounded by empty fields.
        Values are normalized to be between 0 and 1."""
        field = 0
        for i, j in product(range(grid.height - 1), range(grid.width - 1)):
            if grid[i][j] != 0:
                continue
            if (
                grid[i][j] == grid[i + 1][j] == grid[i][j + 1]
                or grid[i][j] == grid[i + 1][j] == grid[i + 1][j + 1]
                or grid[i][j] == grid[i][j + 1] == grid[i + 1][j + 1]
            ):
                field += 1
        return field / ((grid.width - 1) * (grid.height - 1))

    def shifted_sum(self, grid):
        """Returns the sum of the shifted grid."""
        shifted = 0
        for col in range(grid.width):
            tmp = [x for x in grid.data[col] if x != 0]
            shifted += sum(grid.combine_tiles(tmp))
        for row in range(grid.height):
            tmp = [x for x in grid.data[row] if x != 0]
            shifted += sum(grid.combine_tiles(tmp))
        return shifted

    def max_tile(self, grid):
        """Returns the maximum tile in the grid."""
        return max(cell for row in grid.data for cell in row)

    def grid_sum(self, grid):
        """Returns the sum of all cells in the grid."""
        return sum(cell for row in grid.data for cell in row)

    def grid_size(self, grid):
        """Returns the number of cells in the grid."""
        return grid.height * grid.width

    def grid_mean(self, grid):
        """Returns the mean of all cells in the grid."""
        return self.grid_sum(grid) / self.grid_size(grid)

    def values_mean(self, grid):
        """Returns the mean of all non-zero cells in the grid."""
        return self.grid_sum(grid) / len(
            [cell for row in grid.data for cell in row if cell != 0]
        )

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
