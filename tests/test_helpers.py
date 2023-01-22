import unittest

from grid2048.grid2048 import Grid2048
from grid2048.helpers import (
    count_vals_eq,
    count_vals_gte,
    count_vals_lte,
    flatness,
    grid_mean,
    grid_sum,
    high_to_low,
    high_vals_on_edge,
    higher_on_edge,
    low_to_high,
    max_tile,
    monotonicity,
    normalize,
    pairs,
    smoothness,
    values_mean,
    zero_field,
    zeros,
)


class TestHelpers(unittest.TestCase):
    def test_normalize(self):
        values = [1, 2, 3, 4]
        normalized_values = normalize(values)
        for i, value in enumerate(normalized_values):
            self.assertAlmostEqual(value, i / 3)

    def test_zeros(self):
        grid = Grid2048(4, 4)
        grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(zeros(grid), 16)
        grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(zeros(grid), 8)
        grid.data = [[2 for _ in range(4)] for _ in range(4)]
        self.assertEqual(zeros(grid), 0)

    def test_monotonicity(self):
        grid = Grid2048(4, 4)
        grid.data = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(2):
            for j in range(4):
                grid[i][j] = 2 ** (i + j + 2)
        # assertEqual(grid.data, None)
        self.assertEqual(monotonicity(grid), 9)

    def test_smoothness(self):
        grid = Grid2048(4, 4)
        for i in range(4):
            for j in range(4):
                grid[i][j] = 2 ** (i + j + 1)
        self.assertAlmostEqual(smoothness(grid), 0.08, 1)

    def test_pairs(self):
        grid = Grid2048(4, 4)
        grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(pairs(grid), 0)
        grid.data = [[2, 0, 2, 0], [0, 2, 0, 2], [2, 0, 2, 0], [0, 2, 0, 2]]
        self.assertEqual(pairs(grid), 0.5)
        grid.data = [[2, 0, 2, 4], [2, 4, 2, 0], [2, 4, 2, 0], [2, 0, 2, 4]]
        self.assertEqual(pairs(grid), 1)

    def test_flatness(self):
        grid = Grid2048(4, 4)
        grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(flatness(grid), 0)
        grid.data = [
            [1024, 256, 1024, 256],
            [256, 512, 256, 512],
            [512, 256, 512, 256],
            [256, 1024, 256, 1024],
        ]
        # grid.data = [[2 ** randrange(12) for _ in range(4)] for _ in range(4)]
        self.assertEqual(flatness(grid), 256)

    def test_max_tile(self):
        grid = Grid2048(4, 4)
        grid.data = [
            [2, 0, 2048, 0],
            [0, 1024, 0, 4],
            [8, 0, 512, 0],
            [0, 256, 0, 16],
        ]
        self.assertEqual(max_tile(grid), 2048)

    def test_grid_sum(self):
        grid = Grid2048(4, 4)
        grid.data = [
            [2, 0, 2048, 0],
            [0, 1024, 0, 4],
            [8, 0, 512, 0],
            [0, 256, 0, 16],
        ]
        self.assertEqual(grid_sum(grid), 3870)

    def test_grid_mean(self):
        grid = Grid2048(4, 4)
        grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
        self.assertEqual(grid_mean(grid), 2)
        grid.data = [[8, 8, 8, 8], [2, 2, 2, 2], [0, 0, 0, 0], [2, 2, 2, 2]]
        self.assertEqual(grid_mean(grid), 3)

    def test_values_mean(self):
        grid = Grid2048(4, 4)
        grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
        self.assertEqual(grid_mean(grid), 2)
        grid.data = [[8, 8, 8, 8], [2, 2, 2, 2], [0, 0, 0, 0], [2, 2, 2, 2]]
        self.assertEqual(values_mean(grid), 4)

    def test_zero_field(self):
        grid = Grid2048(4, 4)
        grid.data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(zero_field(grid), 9)
        grid.data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 2, 2, 0], [2, 0, 0, 2]]
        self.assertEqual(zero_field(grid), 5)

    def test_high_vals_on_edge(self):
        grid = Grid2048(4, 4)
        grid.data = [[2, 0, 0, 4], [8, 0, 0, 16], [32, 0, 0, 64], [128, 0, 0, 0]]
        self.assertEqual(high_vals_on_edge(grid), 0)
        grid.data = [
            [256, 256, 256, 512],
            [512, 0, 0, 512],
            [256, 2, 2, 1024],
            [2048, 256, 256, 4096],
        ]
        self.assertEqual(high_vals_on_edge(grid), 640)

    def test_higher_on_edge(self):
        grid = Grid2048(4, 4)
        grid.data = [[0, 0, 0, 0], [0, 8, 16, 0], [0, 32, 64, 0], [0, 0, 0, 0]]
        self.assertEqual(higher_on_edge(grid), 0)
        grid.data = [
            [256, 128, 128, 256],
            [512, 256, 256, 512],
            [1024, 0, 0, 1024],
            [128, 64, 64, 128],
        ]
        self.assertEqual(higher_on_edge(grid), 248)

    def test_higt_to_low(self):
        grid = Grid2048(4, 4)
        grid.data = [
            [2, 2, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.assertEqual(high_to_low(grid), 0)
        grid.data = [
            [1024, 1024, 1024, 1024],
            [256, 256, 256, 256],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        self.assertEqual(high_to_low(grid), 0.0625)
        grid.data = [
            [1024, 1024, 1024, 1024],
            [256, 256, 256, 256],
            [512, 512, 512, 512],
            [2048, 2048, 2048, 2048],
        ]
        self.assertEqual(high_to_low(grid), 1)

    def test_low_to_high(self):
        grid = Grid2048(4, 4)
        grid.data = [[4, 4, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(low_to_high(grid), 1)
        grid.data = [
            [256, 256, 256, 256],
            [256, 256, 256, 256],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        self.assertEqual(low_to_high(grid), 0.0625)

    def test_count_vals_eq(self):
        grid = Grid2048(4, 4)
        grid.data = [[4, 4, 4, 4], [0, 0, 0, 0], [2, 2, 2, 2], [8, 8, 8, 8]]
        self.assertEqual(count_vals_eq(grid, 4), 4)
        grid.data = [
            [512, 512, 512, 512],
            [256, 256, 256, 256],
            [4, 4, 4, 4],
            [2, 2, 2, 2],
        ]
        self.assertEqual(count_vals_eq(grid, 256), 4)

    def test_count_vals_lte(self):
        grid = Grid2048(4, 4)
        grid.data = [[4, 4, 4, 4], [0, 0, 0, 0], [2, 2, 2, 2], [8, 8, 8, 8]]
        self.assertEqual(count_vals_lte(grid, 4), 8)
        grid.data = [
            [512, 512, 512, 512],
            [256, 256, 256, 256],
            [4, 4, 4, 4],
            [2, 2, 2, 2],
        ]
        self.assertEqual(count_vals_lte(grid, 256), 12)

    def test_count_vals_gte(self):
        grid = Grid2048(4, 4)
        grid.data = [[4, 4, 4, 4], [0, 0, 0, 0], [2, 2, 2, 2], [8, 8, 8, 8]]
        self.assertEqual(count_vals_gte(grid, 4), 8)
        grid.data = [
            [512, 512, 512, 512],
            [256, 256, 256, 256],
            [4, 4, 4, 4],
            [2, 2, 2, 2],
        ]
        self.assertEqual(count_vals_gte(grid, 256), 8)

    # def test_shift_sum(self):
    #     grid.data = [[4, 0, 2, 0], [0, 4, 0, 2], [2, 0, 4, 0], [0, 2, 0, 4]]
    #     assertEqual(shifted_sum(grid), 48)
    #     grid.data = [[4, 0, 4, 0], [0, 4, 0, 4], [4, 0, 4, 0], [0, 4, 0, 4]]
    #     assertEqual(shifted_sum(grid), 64)
    #     grid.data = [[2, 4, 4, 2], [2, 4, 4, 2], [2, 4, 4, 2], [2, 4, 4, 2]]
    #     assertEqual(shifted_sum(grid), 96)
