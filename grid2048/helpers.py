"""Helper functions for computing the score of a grid."""
from dataclasses import dataclass
from itertools import product

from grid2048.grid2048 import Grid2048


@dataclass
class Heuristic:
    name: str
    weight: float
    value: float


class Evaluator:
    def __init__(self):
        self.heuristics = {}

    def register(self, name: str, weight: float):
        self.heuristics[name] = Heuristic(name, weight, 0.0)

    def __str__(self):
        result = ""
        for name, val in self.heuristics.items():
            result += f"{name!r}: {val.value * val.weight:.2f} \n"
        return result

    def __setitem__(self, name: str, value: float):
        if name not in self.heuristics:
            self.register(name, 1.0)
        self.heuristics[name].value = value

    def __getitem__(self, name: str) -> float:
        if name not in self.heuristics:
            raise KeyError(f"Unknown heuristic: {name!r}")
        return self.heuristics[name].value * self.heuristics[name].weight

    def get_weight(self, name: str) -> float:
        if name not in self.heuristics:
            raise KeyError(f"Unknown heuristic: {name!r}")
        return self.heuristics[name].weight

    def set_weight(self, name: str, weight: float):
        if name not in self.heuristics:
            raise KeyError(f"Unknown heuristic: {name!r}")
        self.heuristics[name].weight = weight

    def evaluate(self) -> float:
        return sum(val.value * val.weight for val in self.heuristics.values())


def normalize(values: list[any]) -> list[float]:
    """Normalize a list of numbers"""
    maxval = max(values)
    minval = min(values)
    return [(x - minval) / (maxval - minval) for x in values]


def zeros(grid: Grid2048) -> float:
    """Returns the number of empty cells in the grid."""
    return len([cell for row in grid.data for cell in row if cell == 0])


def monotonicity(grid: Grid2048) -> float:
    """Returns the number of monotonic rows and columns in the grid.
    It shows how well the numbers are ordered,
    either increasing, decreasing or equal in each row and column.
    For small values, result is small, so this affects the big values more."""
    score = 0
    for row in grid.data:
        for i in range(len(row) - 1):
            if (
                row[i] == row[i + 1] * 2
                or row[i] == row[i + 1] // 2
                # or row[i] == row[i + 1]
                and row[i] != 0
            ):
                score += row[i]

    for col in zip(*grid.data):
        for i in range(len(col) - 1):
            if (
                col[i] == col[i + 1] * 2
                or col[i] == col[i + 1] // 2
                # or col[i] == col[i + 1]
                and col[i] != 0
            ):
                score += col[i]
    return 1 / grid_size(grid) * score


def smoothness(grid: Grid2048) -> float:
    """Returns the smoothness of the grid.
    It works by iterating through the grid, and comparing each element
    with its neighbors, and adding the absolute difference between them.
    In this case, the smaller the difference, the better, so final result
    is square of the grid size divided by the smoothness."""
    smoothness_count = 0
    for i, j in product(range(grid.height - 1), range(grid.width - 1)):
        if grid[i][j] != grid[i + 1][j] and grid[i][j] != 0 and grid[i + 1][j] != 0:
            smoothness_count += abs(grid[i][j] - grid[i + 1][j])
        if grid[i][j] != grid[i][j + 1] and grid[i][j] != 0 and grid[i][j + 1] != 0:
            smoothness_count += abs(grid[i][j] - grid[i][j + 1])
    return (grid_size(grid) ** 2 / smoothness_count) if smoothness_count != 0 else 0


def pairs(grid: Grid2048, values: list[int] = None) -> float:
    """Returns the sum of the pairs in the grid
    divided by the number of cells in the grid.
    That includes pairs with holes in between."""
    if values is None:
        values = [2**x for x in range(1, 16)]
    pairs_count = 0
    tmp = []
    for row in grid.data:
        tmp.extend(
            row[i] for i in range(len(row) - 1) if row[i] != 0 and row[i] in values
        )
        for i in range(len(tmp) - 1):
            if tmp[i] == tmp[i + 1]:
                pairs_count += tmp[i]
        tmp = []

    for col in zip(*grid.data):
        for i in range(len(col) - 1):
            if col[i] != 0 and col[i] in values:
                tmp.append(col[i])
        for i in range(len(tmp) - 1):
            if tmp[i] == tmp[i + 1]:
                pairs_count += tmp[i]
        tmp = []

    return pairs_count / grid_size(grid)


def flatness(grid: Grid2048) -> float:
    """Returns the flatness of the grid.
    It works by iterating through the grid and adding
    the absolute difference between each tile and the max
    tile of its row. Divided by the number of cells in the grid.
    Higher values are better."""
    flatness_count = 0
    for row in grid.data:
        for cell in row:
            if cell != 0:
                flatness_count += abs(cell - max(row))
    return flatness_count / grid_size(grid)


def high_vals_on_edge(grid: Grid2048, divider=256) -> float:
    """Returns the sum of high values (greater or equal to divider)
    that are on the edge the grid.
    Result is divided by the number of cells in the grid."""
    high_vals = 0
    for i, j in product(range(grid.height), range(grid.width)):
        if grid[i][j] == 0:
            continue
        if grid[i][j] >= divider:
            if i == 0 or j == 0 or i == grid.height - 1 or j == grid.width - 1:
                high_vals += grid[i][j]
    return high_vals / grid_size(grid)


def high_vals_in_corner(grid: Grid2048, divider=256) -> float:
    """Returns the sum of high values (greater or equal to divider)
    that are in the cornes of the grid.
    Result is divided by the number of cells in the grid."""
    corner_vals = 0
    if grid[0][0] >= divider:
        corner_vals += grid[0][0]
    if grid[0][grid.width - 1] >= divider:
        corner_vals += grid[0][grid.width - 1]
    if grid[grid.height - 1][0] >= divider:
        corner_vals += grid[grid.height - 1][0]
    if grid[grid.height - 1][grid.width - 1] >= divider:
        corner_vals += grid[grid.height - 1][grid.width - 1]
    return corner_vals / grid_size(grid)


def higher_on_edge(grid: Grid2048) -> float:
    """Returns the sum of the edge values that are higher than their neighbors inside the grid.
    Result is divided by the number of cells in the grid."""
    higher = 0
    for i, j in product(range(grid.height), range(grid.width)):
        if grid[i][j] == 0:
            continue
        if i == 0 and grid[i][j] > grid[i + 1][j]:
            higher += grid[i][j]
        if i == grid.height - 1 and grid[i][j] > grid[i - 1][j]:
            higher += grid[i][j]
        if j == 0 and grid[i][j] > grid[i][j + 1]:
            higher += grid[i][j]
        if j == grid.width - 1 and grid[i][j] > grid[i][j - 1]:
            higher += grid[i][j]
    return higher / grid_size(grid)


def high_to_low(grid: Grid2048, divider=256) -> float:
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


def low_to_high(grid: Grid2048, divider: int = 256) -> float:
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


def count_vals_eq(grid: Grid2048, eq: int) -> float:
    """Returns the number of values equal to the given value."""
    eq_vals = 0
    for i, j in product(range(grid.height), range(grid.width)):
        if grid[i][j] == 0:
            continue
        if grid[i][j] == eq:
            eq_vals += 1
    return eq_vals


def count_vals_lte(grid: Grid2048, divider: int = 8) -> float:
    """Returns the number of values lesser than or equal to the divider."""
    lte_vals = 0
    for i, j in product(range(grid.height), range(grid.width)):
        if grid[i][j] == 0:
            continue
        if grid[i][j] <= divider:
            lte_vals += 1
    return lte_vals


def count_vals_gte(grid: Grid2048, divider: int = 256) -> float:
    """Returns the number of values greater than or equal to the divider."""
    gte_vals = 0
    for i, j in product(range(grid.height), range(grid.width)):
        if grid[i][j] == 0:
            continue
        if grid[i][j] >= divider:
            gte_vals += 1
    return gte_vals


def zero_field(grid: Grid2048) -> float:
    """Returns the number of empty fields that are surrounded by empty fields."""
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
    return field


def shift_score(grid: Grid2048) -> int:
    """Returns the sum of the shifted grid."""

    def combine_tiles(cell: list[int]) -> int:
        """Combine tiles subfunction."""
        i = 0
        score = 0
        while i < len(cell) - 1:
            if cell[i] == cell[i + 1]:
                cell[i] *= 2
                cell.pop(i + 1)
                score += cell[i]
            i += 1
        return score

    shifted = 0
    for col in range(grid.width):
        tmp = [x for x in grid.data[col] if x != 0]
        shifted += combine_tiles(tmp)
    for row in range(grid.height):
        tmp = [x for x in grid.data[row] if x != 0]
        shifted += combine_tiles(tmp)
    return shifted


def max_tile(grid: Grid2048) -> int:
    """Returns the maximum tile in the grid."""
    return max(cell for row in grid.data for cell in row)


def grid_sum(grid: Grid2048) -> int:
    """Returns the sum of all cells in the grid."""
    return sum(cell for row in grid.data for cell in row)


def grid_size(grid: Grid2048) -> int:
    """Returns the number of cells in the grid."""
    return grid.height * grid.width


def grid_mean(grid: Grid2048) -> float:
    """Returns the mean of all cells in the grid."""
    return grid_sum(grid) / grid_size(grid)


def values_mean(grid: Grid2048) -> float:
    """Returns the mean of all non-zero cells in the grid."""
    return grid_sum(grid) / len(
        [cell for row in grid.data for cell in row if cell != 0]
    )
