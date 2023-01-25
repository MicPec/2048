import itertools
from math import log

from grid2048 import Grid2048


class Hasher:
    def __init__(self, grid: Grid2048):
        if grid.height != 4 or grid.width != 4:
            raise ValueError("Hasher only works with 4x4 grids")
        self.grid = grid

    def hash(self):
        h = []
        for row, col in itertools.product(range(4), range(4)):
            tile = self.grid[row][col]
            h.append(hex(int(log(tile if tile > 0 else 1, 2)))[2:])
        return "".join(h)

    def dehash(self, hashed):
        grid = [[0 for _ in range(4)] for _ in range(4)]
        hashed = hex(hashed)[2:]
        while len(hashed) < 16:
            hashed = f"0{hashed}"
        print(hashed)
        for row, col in itertools.product(range(4), range(4)):
            h = int(hashed[row * 4 + col], 16)
            grid[row][col] = 2**h if h > 0 else 0
        return grid

    def __eq__(self, other):
        return self.hash() == other.hash()

    def __hash__(self):
        return hash(self.hash())
