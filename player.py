from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import cycle, product
from random import choices, choice
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
        return len([cell for row in grid._grid for cell in row if cell == 0]) / (
            grid.height * grid.width
        )

    def monotonicity(self, grid):
        """Returns the number of monotonic rows and columns in the grid.
        It shows how well the numbers are ordered,
        either increasing or decreasing in each row and column.
        Values are normalized to be between 0 and 1."""
        score = 0
        for row in grid._grid:
            for i in range(len(row) - 1):
                if (
                    row[i] == row[i + 1]
                    or row[i] == row[i + 1] * 2
                    or row[i] == row[i + 1] // 2
                    and row[i] != 0
                ):
                    score += 1

        for col in zip(*grid._grid):
            for i in range(len(col) - 1):
                if (
                    col[i] == col[i + 1]
                    or col[i] == col[i + 1] * 2
                    or col[i] == col[i + 1] // 2
                    and col[i] != 0
                ):
                    score += 1
        return score / (grid.height * 2 * (grid.width - 1))

    def smoothness(self, grid):
        """Returns the smoothness of the grid.
        It works by iterating through the grid, and comparing each element
        with its neighbors, and adding the absolute difference between them.
        Lower values meam more smoothness."""
        smoothness_count = 0
        for i, j in product(range(grid.height - 1), range(grid.width - 1)):
            if grid[i][j] != grid[i + 1][j] and grid[i][j] != 0 and grid[i + 1][j] != 0:
                smoothness_count += abs(grid[i][j] - grid[i + 1][j])
            if grid[i][j] != grid[i][j + 1] and grid[i][j] != 0 and grid[i][j + 1] != 0:
                smoothness_count += abs(grid[i][j] - grid[i][j + 1])
        return smoothness_count / 10000

    def pairs(self, grid):
        """Returns the sum of the pairs in the grid.
        Values are normalized to be between 0 and 1."""
        pairs_count = 0
        for i, j in product(range(grid.height), range(grid.width)):
            if grid[i][j] == 0:
                continue
            if i < grid.height - 1 and grid[i][j] == grid[i + 1][j]:
                pairs_count += 1

            if j < grid.width - 1 and grid[i][j] == grid[i][j + 1]:
                pairs_count += 1
        return pairs_count / (grid.height * 2 * (grid.width - 1))

    def flatness(self, grid):
        """Returns the flatness of the grid.
        It works by iterating through the grid and adding
        the absolute difference between each tile and the max
        tile of its row.
        The higher the count the less flat the grid is."""
        flatness_count = 0
        for row in grid._grid:
            for cell in row:
                if cell != 0:
                    flatness_count += abs(cell - max(row))
        return flatness_count / 10000

    def high_vals_outside(self, grid, divider=256):
        """Returns the number of high values that are outside the grid.
        Values are normalized to be between 0 and 1."""
        high_vals = sum(
            grid[i][j] >= divider
            and (i == 0 or j == 0 or i == grid.height - 1 or j == grid.width - 1)
            for i, j in product(range(grid.height), range(grid.width))
        )
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

    def max_tile(self, grid):
        """Returns the maximum tile in the grid."""
        return max(cell for row in grid._grid for cell in row)

    def grid_sum(self, grid):
        """Returns the sum of all cells in the grid."""
        return sum(cell for row in grid._grid for cell in row)

    def grid_size(self, grid):
        """Returns the number of cells in the grid."""
        return grid.height * grid.width

    def grid_mean(self, grid):
        """Returns the mean of all cells in the grid."""
        return self.grid_sum(grid) / self.grid_size(grid)

    def values_mean(self, grid):
        """Returns the mean of all non-zero cells in the grid."""
        return self.grid_sum(grid) / len(
            [cell for row in grid._grid for cell in row if cell != 0]
        )

    def grid_variance(self, grid):
        """Returns the variance of all cells in the grid.
        The higher the variance, the more spread out the tiles in the grid are."""
        mean = self.grid_mean(grid)
        return (
            sum((cell - mean) ** 2 for row in grid._grid for cell in row)
            / self.grid_size(grid)
            / 10000
        )


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    dirs = ["l", "u", "d", "r"]
    max_depth = 20  # maximum depth to simulate
    n_sim = 30  # number of simulations to run for each move

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[self.get_best_move(self.grid)]()

    def get_best_move(self, grid):
        # Initialize a dictionary to store the number of wins for each move
        wins = {"u": 0, "d": 0, "l": 0, "r": 0}

        for move, _ in wins.items():
            for _ in range(self.n_sim):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                if self.move(sim_grid, move):
                    result = self.simulate(sim_grid)
                    wins[move] += result
        return max(wins, key=wins.get)

    def move(self, grid, direction, add_tile: bool = False):
        moved = False
        if direction == "u":
            moved = grid.shift_up(add_tile=add_tile)
        elif direction == "d":
            moved = grid.shift_down(add_tile=add_tile)
        elif direction == "l":
            moved = grid.shift_left(add_tile=add_tile)
        elif direction == "r":
            moved = grid.shift_right(add_tile=add_tile)
        return moved

    def evaluate(self, grid):
        """Return the score of the grid"""
        val = [
            0.01 * grid.score,
            # 0.1 * self.grid_sum(grid),
            0.85 * self.zeros(grid),
            self.pairs(grid),
            # 0.001 * self.monotonicity(grid) * self.grid_sum(grid),
            1.25 / (self.smoothness(grid) + 1),
            0.01 * self.max_tile(grid),
            0.005 * self.zero_field(grid) * self.max_tile(grid),
            0.25 * self.monotonicity(grid),
            # 0.01 * self.values_mean(grid),
            0.7 * self.high_vals_outside(grid),
        ]
        # print(val)
        return sum(val)

    def simulate(self, grid):

        depth = 0
        while depth < self.max_depth:
            depth += 1
            # select a random move
            move = choice(self.dirs)
            moved = self.move(grid, move, True)
            if not moved or grid.no_moves():
                break
        # return score
        return self.evaluate(grid)


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    dirs = ["l", "u", "d", "r"]
    depth = 3

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[self.get_best_move(self.grid)]()

    def get_best_move(self, grid):
        best_value = float("-inf")
        best_move = None

        for move in self.dirs:
            new_grid, moved = self.move(grid, move, True)
            if new_grid.no_moves():
                return move
            if not moved:
                continue
            value = self.expectimax(new_grid, self.depth, "ai")
            if value > best_value:
                best_value = value
                best_move = move
        return best_move

    def expectimax(self, grid, depth, player):
        if depth == 0 or grid.no_moves():
            return self.evaluate(grid)
        if player == "ai":
            best_value = float("-inf")
            for move in self.dirs:
                new_grid, moved = self.move(grid, move, True)
                if not moved:
                    continue
                value = self.expectimax(new_grid, depth - 1, "random")
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            for move in self.dirs:
                new_grid, moved = self.move(grid, move, True)
                if not moved:
                    continue
                values.append(self.expectimax(new_grid, depth - 1, "ai"))
            return sum(values) / len(values)

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = self.max_tile(grid)
        val = [
            0.01 * grid.score,
            # 0.1 * self.grid_sum(grid),
            1.0 * self.zeros(grid),
            1.0 * self.pairs(grid),
            # 0.001 * self.monotonicity(grid) * self.grid_sum(grid),
            1.25 / (self.smoothness(grid) + 1),
            0.01 * self.max_tile(grid),
            0.005 * self.zero_field(grid) * self.max_tile(grid),
            0.25 * self.monotonicity(grid),
            # 0.01 * self.values_mean(grid),
            0.5 * self.high_vals_outside(grid),
        ]
        print(val)
        return sum(val)


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    dirs = ["l", "u", "d", "r"]
    depth = 3

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[self.get_best_move(self.grid)]()

    def get_best_move(self, grid):
        best_score = float("-inf")
        best_move = None
        for move in self.dirs:
            new_grid, moved = self.move(grid, move)
            if new_grid.no_moves():
                return move
            if not moved:
                continue
            score = self.minimax(new_grid, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, grid, depth, maximizing):
        if grid.no_moves() or depth == 0:
            return self.evaluate(grid)
        if maximizing:
            best_score = float("-inf")
            for move in self.dirs:
                new_grid, moved = self.move(grid, move)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, False)
                best_score = max(best_score, score)
        else:
            best_score = float("inf")
            for move in self.dirs:
                new_grid, moved = self.move(grid, move, True)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, True)
                best_score = min(best_score, score)
        return best_score

    def evaluate(self, grid):
        """Return the score of the grid"""
        val = [
            0.1 * grid.score,
            # 0.01 * self.max_tile(grid),
            0.01 * self.grid_sum(grid),
            2 * self.zeros(grid),
            # 0.002 * self.monotonicity(grid),
            -0.0005 * self.smoothness(grid),
            0.35 * self.pairs(grid),
            # -0.002 * self.flatness(grid),
            # 0.1 * self.grid_mean(grid),
            0.002 * self.values_mean(grid),
            # -0.0001 * self.grid_variance(grid),
        ]
        # print(val)
        return sum(val)


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
