import itertools
import unittest

from grid2048.grid2048 import DIRECTION, STATE, Grid2048, MoveFactory
import numpy as np


class TestGrid2048(unittest.TestCase):
    def test_init(self):
        grid = Grid2048(4, 4)
        self.assertEqual(grid.width, 4)
        self.assertEqual(grid.height, 4)
        self.assertEqual(grid.state, STATE.IDLE)

    def test_str(self):
        grid = Grid2048(4, 4)
        grid.data = np.array([[2, 0, 0, 0], [0, 4, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]])
        self.assertEqual(
            str(grid),
            "\n-------------\n|2 |  |  |  |\n-------------\n|  |4 |  |  |\n-------------\n|  |  |8 |  |\n-------------\n|  |  |  |16|\n-------------\n",
        )

    def test_getitem_setitem(self):
        grid = Grid2048(4, 4)
        grid[0, 0] = 2
        self.assertEqual(grid[0, 0], 2)

    def test_reset(self):
        grid = Grid2048(4, 4)
        grid.reset()
        self.assertEqual(grid.state, STATE.IDLE)
        self.assertEqual(grid.score, 0)
        self.assertEqual(grid.moves, 0)

    def test_score(self):
        grid = Grid2048(4, 4)
        grid.data = np.zeros((4, 4), int)
        move = MoveFactory.create(DIRECTION.LEFT)
        grid.move(move)
        self.assertEqual(grid.score, 0)
        grid.data = np.array([[2, 2, 0, 0], [2, 0, 2, 0], [2, 0, 0, 2], [4, 0, 0, 4]])
        move = MoveFactory.create(DIRECTION.LEFT)
        grid.move(move)
        self.assertEqual(grid.score, 20)

    def test_get_empty_fields(self):
        grid = Grid2048(4, 4)
        grid.data = np.array([[2, 0, 0, 0], [0, 4, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]])
        empty_fields = grid.get_empty_fields()
        self.assertEqual(len(empty_fields), 12)
        self.assertNotIn((0, 0), empty_fields)
        self.assertNotIn((1, 1), empty_fields)
        self.assertNotIn((2, 2), empty_fields)
        self.assertNotIn((3, 3), empty_fields)

    def test_add_random_tile(self):
        grid = Grid2048(4, 4)
        empty_fields = grid.get_empty_fields()
        grid.add_random_tile(empty_fields)
        self.assertNotEqual(grid.get_empty_fields(), empty_fields)

    def test_no_moves_true(self):
        grid = Grid2048(4, 4)
        self.assertFalse(grid.no_moves)
        for i, j in itertools.product(range(4), range(4)):
            # [[64,2,4,8],[2,4,8,16],[4,8,16,32],[8,16,32,64]]
            grid[i, j] = 2 ** (i + j) if i + j > 0 else 64
        self.assertTrue(grid.no_moves)

    def test_no_moves_false(self):
        grid = Grid2048(4, 4)
        self.assertFalse(grid.no_moves)
        for i, j in itertools.product(range(4), range(4)):
            # [[2,2,2,2],[4,4,4,4],[8,8,8,8],[16,16,16,16]
            grid[i, j] = 2 ** (i + 1)
        self.assertFalse(grid.no_moves)


if __name__ == "__main__":
    unittest.main()
