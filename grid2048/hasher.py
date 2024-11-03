import itertools
from math import log


class Hasher:
    def __init__(self, grid):
        if not isinstance(grid, (list, tuple)) or not all(
            isinstance(row, (list, tuple)) for row in grid
        ):
            raise TypeError("Grid must be a 2D list or tuple")
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0
        if not all(len(row) == self.width for row in grid):
            raise ValueError("All rows must have the same length")

    def hash(self) -> str:
        """Hash the grid into a string representation"""
        h = [hex(self.height)[2:], hex(self.width)[2:]]
        for row, col in itertools.product(range(self.height), range(self.width)):
            tile = self.grid[row][col]
            if not isinstance(tile, (int, float)) and tile is not None:
                raise TypeError(f"Invalid tile value at ({row}, {col}): {tile}")
            # Handle zero, negative numbers, and None values
            if tile is None or tile <= 0:
                h.append("0")
            else:
                try:
                    h.append(hex(int(log(tile, 2)))[2:])
                except ValueError as e:
                    raise ValueError(
                        f"Cannot compute log of {tile} at ({row}, {col})"
                    ) from e
        return "".join(h)

    def dehash(self, hashed: str) -> list[list[int]]:
        """Convert a hash string back to a grid"""
        if not isinstance(hashed, str):
            raise TypeError("Hash must be a string")
        if len(hashed) < 4:
            raise ValueError("Invalid hash length")

        try:
            height = int(hashed[:2], 16)
            width = int(hashed[2:4], 16)
        except ValueError as e:
            raise ValueError("Invalid dimensions in hash") from e

        if height <= 0 or width <= 0:
            raise ValueError("Invalid grid dimensions in hash")

        grid = [[0 for _ in range(width)] for _ in range(height)]
        hashed = hashed[4:]
        while len(hashed) < height * width:
            hashed = f"0{hashed}"

        for row, col in itertools.product(range(height), range(width)):
            try:
                h = int(hashed[row * width + col], 16)
                grid[row][col] = 2**h if h > 0 else 0
            except (ValueError, IndexError) as e:
                raise ValueError(
                    f"Invalid hash value at position {row * width + col}"
                ) from e

        return grid

    def __eq__(self, other):
        if not isinstance(other, Hasher):
            return False
        return self.hash() == other.hash()

    def __hash__(self):
        return hash(self.hash())
