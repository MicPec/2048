"""Unit tests for the Grid2048 class using unittest framework."""

import unittest
import numpy as np
from grid2048.grid2048 import Grid2048, Move, MoveFactory, STATE, DIRECTION


class TestGrid2048(unittest.TestCase):
    """Test cases for Grid2048 class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.empty_grid = Grid2048(4, 4)
        self.empty_grid.data = np.zeros((4, 4), dtype=int)

        self.simple_grid = Grid2048(4, 4)
        self.simple_grid.data = np.array(
            [
                [2, 0, 0, 2],
                [2, 2, 0, 0],
                [4, 0, 2, 0],
                [0, 0, 0, 4],
            ]
        )

    def test_grid_initialization(self):
        """Test grid initialization."""
        grid = Grid2048(4, 4)
        self.assertEqual(grid.width, 4)
        self.assertEqual(grid.height, 4)
        self.assertEqual(grid.state, STATE.IDLE)
        self.assertEqual(grid.score, 0)
        self.assertEqual(grid.moves, 0)
        # Should have exactly two non-zero tiles
        self.assertEqual(np.count_nonzero(grid.data), 2)

    def test_grid_initialization_invalid(self):
        """Test grid initialization with invalid dimensions."""
        with self.assertRaises(ValueError):
            Grid2048(0, 4)
        with self.assertRaises(ValueError):
            Grid2048(4, 0)
        with self.assertRaises(ValueError):
            Grid2048(-1, 4)

    def test_grid_reset(self):
        """Test grid reset functionality."""
        self.empty_grid.score = 100
        self.empty_grid.moves = 10
        self.empty_grid.reset()
        self.assertEqual(self.empty_grid.score, 0)
        self.assertEqual(self.empty_grid.moves, 0)
        self.assertEqual(np.count_nonzero(self.empty_grid.data), 2)

    def test_grid_data_setter(self):
        """Test grid data setter validation."""
        grid = Grid2048(4, 4)

        # Test invalid type
        with self.assertRaises(TypeError):
            grid.data = [[1, 2], [3, 4]]

        # Test invalid dimensions
        with self.assertRaises(ValueError):
            grid.data = np.zeros((3, 3))

        # Test invalid data type
        with self.assertRaises(ValueError):
            grid.data = np.array([[1.5, 2], [3, 4]])

    def test_get_empty_fields(self):
        """Test getting empty fields."""
        empty_fields = self.simple_grid.get_empty_fields()
        self.assertEqual(len(empty_fields), 9)  # Count of zeros in simple_grid
        self.assertIn((0, 1), empty_fields)  # Check some specific empty positions
        self.assertIn((0, 2), empty_fields)

    def test_put_random_tile(self):
        """Test putting a random tile."""
        self.empty_grid.put_random_tile(0, 0)
        self.assertIn(self.empty_grid.data[0, 0], [2, 4])

        # Test invalid coordinates
        with self.assertRaises(ValueError):
            self.empty_grid.put_random_tile(4, 0)

        # Test non-empty cell
        with self.assertRaises(ValueError):
            self.empty_grid.put_random_tile(0, 0)

    def test_move_up(self):
        """Test upward move."""
        expected = np.array([[4, 2, 2, 2], [4, 0, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0]])
        move = MoveFactory.create(DIRECTION.UP)
        self.simple_grid.move(move, add_tile=False)
        np.testing.assert_array_equal(self.simple_grid.data, expected)

    def test_move_down(self):
        """Test downward move."""
        expected = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [4, 0, 0, 2], [4, 2, 2, 4]])
        move = MoveFactory.create(DIRECTION.DOWN)
        self.simple_grid.move(move, add_tile=False)
        np.testing.assert_array_equal(self.simple_grid.data, expected)

    def test_move_left(self):
        """Test leftward move."""
        expected = np.array([[4, 0, 0, 0], [4, 0, 0, 0], [4, 2, 0, 0], [4, 0, 0, 0]])
        move = MoveFactory.create(DIRECTION.LEFT)
        self.simple_grid.move(move, add_tile=False)
        np.testing.assert_array_equal(self.simple_grid.data, expected)

    def test_move_right(self):
        """Test rightward move."""
        expected = np.array([[0, 0, 0, 4], [0, 0, 0, 4], [0, 0, 4, 2], [0, 0, 0, 4]])
        move = MoveFactory.create(DIRECTION.RIGHT)
        self.simple_grid.move(move, add_tile=False)
        np.testing.assert_array_equal(self.simple_grid.data, expected)

    def test_move_scoring(self):
        """Test that moves are scored correctly."""
        # Move right to combine 2+2 tiles twice
        move = MoveFactory.create(DIRECTION.RIGHT)
        self.simple_grid.move(move, add_tile=False)
        self.assertEqual(move.score, 8)  # 2+2=4, 2+2=4, so total score is 8
        self.assertEqual(self.simple_grid.score, 8)

    def test_no_moves_detection(self):
        """Test detection of no available moves."""
        grid = Grid2048(2, 2)
        # Create a grid with no possible moves
        grid.data = np.array([[2, 4], [4, 2]])
        self.assertTrue(grid.no_moves)

        # Modify to allow moves
        grid.data = np.array([[2, 2], [4, 2]])
        self.assertFalse(grid.no_moves)

    def test_move_validation(self):
        """Test move validation."""
        # Valid move
        move = MoveFactory.create(DIRECTION.RIGHT)
        self.assertTrue(self.simple_grid.move(move))

        # Invalid move (no changes possible)
        grid = Grid2048(2, 2)
        grid.data = np.array([[2, 4], [4, 2]])
        move = MoveFactory.create(DIRECTION.RIGHT)
        self.assertFalse(grid.move(move))

    def test_last_move(self):
        """Test last move tracking."""
        with self.assertRaises(ValueError):
            _ = self.simple_grid.last_move

        move = MoveFactory.create(DIRECTION.RIGHT)
        self.simple_grid.move(move)
        self.assertEqual(self.simple_grid.last_move.direction, DIRECTION.RIGHT)

    def test_grid_equality(self):
        """Test grid equality comparison."""
        grid1 = Grid2048(4, 4)
        grid2 = Grid2048(4, 4)

        # Same dimensions but different content
        self.assertNotEqual(grid1, grid2)  # Random tiles make them different

        # Copy data to make them equal
        grid2.data = grid1.data.copy()
        self.assertEqual(grid1, grid2)

        # Different dimensions
        grid3 = Grid2048(3, 3)
        self.assertNotEqual(grid1, grid3)

        # Compare with non-Grid2048 object
        self.assertNotEqual(grid1, "not a grid")


if __name__ == "__main__":
    unittest.main()
