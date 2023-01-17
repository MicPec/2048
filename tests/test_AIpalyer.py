from random import random, randrange
import unittest
from copy import deepcopy
from unittest.mock import MagicMock

from grid2048.grid2048 import Grid2048
from players.player import AIPlayer


class TestPlayer(AIPlayer):
    def evaluate(self, grid):
        """Returns the score of the grid."""
        pass

    def play(self, *args, **kwargs) -> bool:
        return True


class TestAIPlayer(unittest.TestCase):
    def setUp(self):
        self.grid = Grid2048(4, 4)
        self.player = TestPlayer(self.grid)

    def test_normalize(self):
        values = [1, 2, 3, 4]
        normalized_values = self.player.normalize(values)
        for i, value in enumerate(normalized_values):
            self.assertAlmostEqual(value, i / 3)

    def test_zeros(self):
        grid = Grid2048(4, 4)
        grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(self.player.zeros(grid), 1)
        grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(self.player.zeros(grid), 0.5)
        grid.data = [[2 for _ in range(4)] for _ in range(4)]
        self.assertEqual(self.player.zeros(grid), 0)

    def test_monotonicity(self):
        self.grid.data = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(2):
            for j in range(4):
                self.grid[i][j] = 2 ** (i + j + 2)
        # self.assertEqual(grid.data, None)
        self.assertEqual(self.player.monotonicity(self.grid), 9)

    def test_smoothness(self):
        for i in range(4):
            for j in range(4):
                self.grid[i][j] = 2 ** (i + j + 1)
        self.assertAlmostEqual(self.player.smoothness(self.grid), 0.02, 1)

    def test_pairs(self):
        self.grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(self.player.pairs(self.grid), 0)
        self.grid.data = [[2, 0, 2, 0], [0, 2, 0, 2], [2, 0, 2, 0], [0, 2, 0, 2]]
        self.assertEqual(self.player.pairs(self.grid), 1)
        self.grid.data = [[2, 0, 2, 4], [2, 4, 2, 0], [2, 4, 2, 0], [2, 0, 2, 4]]
        self.assertEqual(self.player.pairs(self.grid), 0.5)

    def test_flatness(self):
        self.grid.data = [[0 for _ in range(4)] for _ in range(4)]
        self.assertEqual(self.player.flatness(self.grid), 0)
        self.grid.data = [
            [1024, 256, 1024, 256],
            [256, 512, 256, 512],
            [512, 256, 512, 256],
            [256, 1024, 256, 1024],
        ]
        # self.grid.data = [[2 ** randrange(12) for _ in range(4)] for _ in range(4)]
        self.assertEqual(self.player.flatness(self.grid), 256)

    def test_max_tile(self):
        self.grid.data = [
            [2, 0, 2048, 0],
            [0, 1024, 0, 4],
            [8, 0, 512, 0],
            [0, 256, 0, 16],
        ]
        self.assertEqual(self.player.max_tile(self.grid), 2048)

    def test_grid_sum(self):
        self.grid.data = [
            [2, 0, 2048, 0],
            [0, 1024, 0, 4],
            [8, 0, 512, 0],
            [0, 256, 0, 16],
        ]
        self.assertEqual(self.player.grid_sum(self.grid), 3870)

    def test_grid_mean(self):
        self.grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
        self.assertEqual(self.player.grid_mean(self.grid), 2)
        self.grid.data = [[8, 8, 8, 8], [2, 2, 2, 2], [0, 0, 0, 0], [2, 2, 2, 2]]
        self.assertEqual(self.player.grid_mean(self.grid), 3)

    def test_values_mean(self):
        self.grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
        self.assertEqual(self.player.grid_mean(self.grid), 2)
        self.grid.data = [[8, 8, 8, 8], [2, 2, 2, 2], [0, 0, 0, 0], [2, 2, 2, 2]]
        self.assertEqual(self.player.values_mean(self.grid), 4)

    # def test_grid_variance(self):
    #     self.grid.data = [[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
    #     self.assertEqual(self.player.grid_variance(self.grid), 0)
    #     for i in range(4):
    #         for j in range(4):
    #             self.grid[i][j] = 2 ** (i + j * 2 + 1)
    #     self.assertAlmostEqual(self.player.grid_variance(self.grid), 0.92, 1)

    def test_zero_field(self):
        self.grid.data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(self.player.zero_field(self.grid), 1)
        self.grid.data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 2, 2, 0], [2, 0, 0, 2]]
        self.assertAlmostEqual(self.player.zero_field(self.grid), 0.55555555)

    def test_high_vals_outside(self):
        self.grid.data = [[2, 0, 0, 4], [8, 0, 0, 16], [32, 0, 0, 64], [128, 0, 0, 0]]
        self.assertEqual(self.player.high_vals_on_edge(self.grid), 0)
        self.grid.data = [
            [256, 256, 256, 512],
            [512, 0, 0, 512],
            [256, 2, 2, 1024],
            [2048, 256, 256, 4096],
        ]
        self.assertEqual(self.player.high_vals_on_edge(self.grid), 1)

    def test_higt_to_low(self):
        self.grid.data = [
            [2, 2, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.assertEqual(self.player.high_to_low(self.grid), 0)
        self.grid.data = [
            [256, 256, 256, 256],
            [256, 256, 256, 256],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        self.assertEqual(self.player.high_to_low(self.grid), 0.0625)

    def test_low_to_high(self):
        self.grid.data = [[4, 4, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(self.player.low_to_high(self.grid), 1)
        self.grid.data = [
            [256, 256, 256, 256],
            [256, 256, 256, 256],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        self.assertEqual(self.player.low_to_high(self.grid), 0.0625)

    def test_shift_sum(self):
        self.grid.data = [[4, 0, 2, 0], [0, 4, 0, 2], [2, 0, 4, 0], [0, 2, 0, 4]]
        self.assertEqual(self.player.shifted_sum(self.grid), 48)
        self.grid.data = [[4, 0, 4, 0], [0, 4, 0, 4], [4, 0, 4, 0], [0, 4, 0, 4]]
        self.assertEqual(self.player.shifted_sum(self.grid), 64)
        self.grid.data = [[2, 4, 4, 2], [2, 4, 4, 2], [2, 4, 4, 2], [2, 4, 4, 2]]
        self.assertEqual(self.player.shifted_sum(self.grid), 96)
