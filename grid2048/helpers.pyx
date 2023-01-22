"""Helper functions for computing the score of a grid."""
from itertools import product

from grid2048.grid2048 import Grid2048

cdef float zeros(Grid2048 grid):
    """Returns the number of empty cells in the grid.
    Values are normalized to be between 0 and 1."""
    cdef int count = 0
    for row in grid.data:
        for cell in row:
            if cell == 0:
                count += 1

    return count / grid_size(grid)