"""Unit tests for the Grid2048 helper functions."""

import unittest
import numpy as np
from grid2048.grid2048 import Grid2048, DIRECTION, MoveFactory
from grid2048.helpers import (
    get_valid_moves,
    normalize,
    zeros,
    monotonicity,
    smoothness,
    pairs,
    flatness,
    high_vals_on_edge,
    high_vals_in_corner,
    higher_on_edge,
    high_to_low,
    low_to_high,
    count_vals_eq,
    count_vals_lte,
    count_vals_gte,
    zero_field,
    move_score,
    max_tile,
    grid_sum,
    grid_size,
    grid_mean,
    values_mean,
)


class TestHelpers(unittest.TestCase):
    """Test cases for Grid2048 helper functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.empty_grid = Grid2048(4, 4)
        self.empty_grid.data = np.zeros((4, 4), dtype=int)

        self.test_grid = Grid2048(4, 4)
        self.test_grid.data = np.array(
            [
                [2, 4, 8, 16],
                [0, 2, 4, 8],
                [0, 0, 2, 4],
                [0, 0, 0, 2],
            ]
        )

        self.blocked_grid = Grid2048(2, 2)
        self.blocked_grid.data = np.array([[2, 4], [4, 2]])
        self.move_score_grid = Grid2048(2, 2)
        self.move_score_grid.data = np.array([[2, 2], [4, 4]])

    def test_get_valid_moves(self):
        """Test getting valid moves."""
        # Empty grid should have no valid moves
        self.assertEqual(get_valid_moves(self.empty_grid), [])

        # Test grid should have valid moves
        valid_moves = get_valid_moves(self.test_grid)
        self.assertIn(DIRECTION.LEFT, valid_moves)
        self.assertIn(DIRECTION.DOWN, valid_moves)

        self.assertNotIn(DIRECTION.UP, valid_moves)

        # Blocked grid should have no valid moves
        self.assertEqual(get_valid_moves(self.blocked_grid), [])

    def test_normalize(self):
        """Test normalizing values."""
        # Empty list
        self.assertEqual(normalize([]), [])

        # Single value
        self.assertEqual(normalize([5]), [1.0])

        # Multiple values
        result = normalize([0, 5, 10])
        self.assertEqual(result, [0.0, 0.5, 1.0])

        # Same values
        self.assertEqual(normalize([4, 4, 4]), [1.0, 1.0, 1.0])

    def test_zeros(self):
        """Test counting zeros."""
        self.assertEqual(zeros(self.empty_grid), 16)  # 4x4 empty grid
        self.assertEqual(zeros(self.test_grid), 6)  # Test grid has 6 zeros
        self.assertEqual(zeros(self.blocked_grid), 0)  # Blocked grid has no zeros

    def test_monotonicity(self):
        """Test monotonicity calculation."""
        self.assertEqual(monotonicity(self.empty_grid), 0)

        # Create a perfectly monotonic grid
        mono_grid = Grid2048(4, 4)
        mono_grid.data = np.array(
            [
                [16, 8, 4, 2],
                [8, 4, 2, 0],
                [4, 2, 0, 0],
                [2, 0, 0, 0],
            ]
        )
        self.assertGreater(monotonicity(mono_grid), 0)

        # Test grid should have some monotonicity
        self.assertGreater(monotonicity(self.test_grid), 0)

    def test_smoothness(self):
        """Test smoothness calculation."""
        self.assertEqual(smoothness(self.empty_grid), 0)

        # Create a smooth grid
        smooth_grid = Grid2048(4, 4)
        smooth_grid.data = np.array(
            [
                [4, 2, 4, 2],
                [2, 4, 2, 2],
                [2, 2, 2, 2],
                [0, 2, 4, 2],
            ]
        )
        self.assertGreater(smoothness(smooth_grid), smoothness(self.test_grid))

    def test_pairs(self):
        """Test pairs calculation."""
        self.assertEqual(pairs(self.empty_grid), 0)

        # Create a grid with pairs
        pairs_grid = Grid2048(4, 4)
        pairs_grid.data = np.array(
            [
                [2, 2, 4, 4],
                [2, 2, 16, 16],
                [0, 0, 4, 0],
                [0, 0, 4, 0],
            ]
        )
        self.assertGreater(pairs(pairs_grid), pairs(self.test_grid))

        # Test with specific values
        self.assertEqual(pairs(pairs_grid, [2]), 0.5)

    def test_flatness(self):
        """Test flatness calculation."""
        self.assertEqual(flatness(self.empty_grid), 0)

        flat_grid = Grid2048(4, 4)
        flat_grid.data = np.array(
            [[2, 2, 2, 2], [4, 4, 4, 4], [8, 8, 8, 8], [16, 16, 16, 16]]
        )
        self.assertEqual(flatness(flat_grid), 0)
        self.assertGreater(flatness(self.test_grid), 0)

    def test_high_vals_on_edge(self):
        """Test high values on edge calculation."""
        self.assertEqual(high_vals_on_edge(self.empty_grid), 0)

        edge_grid = Grid2048(4, 4)
        edge_grid.data = np.array(
            [[256, 2, 2, 512], [2, 2, 2, 2], [2, 2, 2, 2], [1024, 2, 2, 256]]
        )
        self.assertGreater(high_vals_on_edge(edge_grid), 0)

    def test_high_vals_in_corner(self):
        """Test high values in corner calculation."""
        self.assertEqual(high_vals_in_corner(self.empty_grid), 0)

        corner_grid = Grid2048(4, 4)
        corner_grid.data = np.array(
            [[256, 2, 2, 512], [2, 2, 2, 2], [2, 2, 2, 2], [1024, 2, 2, 256]]
        )
        self.assertGreater(high_vals_in_corner(corner_grid), 0)

    def test_higher_on_edge(self):
        """Test higher values on edge calculation."""
        self.assertEqual(higher_on_edge(self.empty_grid), 0)
        self.assertGreater(higher_on_edge(self.test_grid), 0)

    def test_high_to_low(self):
        """Test high to low ratio calculation."""
        self.assertEqual(high_to_low(self.empty_grid), 0)
        self.assertEqual(high_to_low(self.test_grid), 0)  # No values >= 256

        high_low_grid = Grid2048(4, 4)
        high_low_grid.data = np.array(
            [[256, 2, 2, 512], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]
        )
        self.assertGreater(high_to_low(high_low_grid), 0)

    def test_low_to_high(self):
        """Test low to high ratio calculation."""
        self.assertEqual(low_to_high(self.empty_grid), 0)
        self.assertGreater(low_to_high(self.test_grid), 0)  # All values < 256

    def test_count_vals_eq(self):
        """Test counting equal values."""
        self.assertEqual(count_vals_eq(self.empty_grid, 2), 0)
        self.assertEqual(count_vals_eq(self.test_grid, 2), 4)
        self.assertEqual(count_vals_eq(self.test_grid, 4), 3)

    def test_count_vals_lte(self):
        """Test counting values less than or equal."""
        self.assertEqual(count_vals_lte(self.empty_grid), 0)
        self.assertEqual(count_vals_lte(self.test_grid, 4), 7)  # 2s and 4s

    def test_count_vals_gte(self):
        """Test counting values greater than or equal."""
        self.assertEqual(count_vals_gte(self.empty_grid), 0)
        self.assertEqual(count_vals_gte(self.test_grid, 8), 3)  # 8s and 16

    def test_zero_field(self):
        """Test zero field calculation."""
        self.assertEqual(zero_field(self.empty_grid), 9)  # 3x3 possible fields
        self.assertGreater(zero_field(self.test_grid), 0)

    def test_move_score(self):
        """Test move score calculation."""
        self.assertEqual(move_score(self.empty_grid), 0)
        self.assertGreater(move_score(self.move_score_grid), 0)

    def test_max_tile(self):
        """Test maximum tile calculation."""
        self.assertEqual(max_tile(self.empty_grid), 0)
        self.assertEqual(max_tile(self.test_grid), 16)

    def test_grid_sum(self):
        """Test grid sum calculation."""
        self.assertEqual(grid_sum(self.empty_grid), 0)
        self.assertEqual(grid_sum(self.test_grid), 52)  # Sum of all values

    def test_grid_size(self):
        """Test grid size calculation."""
        self.assertEqual(grid_size(self.empty_grid), 16)  # 4x4
        self.assertEqual(grid_size(self.blocked_grid), 4)  # 2x2

    def test_grid_mean(self):
        """Test grid mean calculation."""
        self.assertEqual(grid_mean(self.empty_grid), 0)
        self.assertEqual(grid_mean(self.test_grid), 3.25)  # 52/16

    def test_values_mean(self):
        """Test non-zero values mean calculation."""
        self.assertEqual(values_mean(self.empty_grid), 0)
        self.assertEqual(values_mean(self.test_grid), 5.2)  # 52/10 (10 non-zero values)


if __name__ == "__main__":
    unittest.main()
