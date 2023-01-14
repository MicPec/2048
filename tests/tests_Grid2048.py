import unittest
from grid2048 import Grid2048


class TestGrid2048(unittest.TestCase):
    def test_init(self):
        grid = Grid2048(4, 4)
        self.assertEqual(grid.width, 4)
        self.assertEqual(grid.height, 4)
        self.assertEqual(grid.state, grid.STATES.IDLE)

    def test_str(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 0, 0], [0, 4, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]]
        self.assertEqual(
            str(grid),
            "\n-------------\n|2 |  |  |  |\n-------------\n|  |4 |  |  |\n-------------\n|  |  |8 |  |\n-------------\n|  |  |  |16|\n-------------\n",
        )

    def test_getitem_setitem(self):
        grid = Grid2048(4, 4)
        grid[0][0] = 2
        self.assertEqual(grid[0][0], 2)

    def test_reset(self):
        grid = Grid2048(4, 4)
        grid.reset()
        self.assertEqual(grid.state, grid.STATES.IDLE)
        self.assertEqual(grid.score, 0)
        self.assertEqual(grid.moves, 0)

    def test_score(self):
        grid = Grid2048(4, 4)
        grid._grid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        grid.shift_left()
        self.assertEqual(grid.score, 0)
        grid._grid = [[2, 2, 0, 0], [2, 0, 2, 0], [2, 0, 0, 2], [4, 0, 0, 4]]
        grid.shift_left()
        self.assertEqual(grid.score, 20)

    def test_get_empty_fields(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 0, 0], [0, 4, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]]
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

    def test_combine_tiles(self):
        grid = Grid2048(4, 4)
        temp = [2, 2, 4, 4]
        temp = grid.combine_tiles(temp)
        self.assertEqual(temp, [4, 8])
        self.assertEqual(grid.score, 12)

    def test_combine_tiles_2(self):
        grid = Grid2048(4, 4)
        temp = [8, 8, 8]
        temp = grid.combine_tiles(temp)
        self.assertEqual(temp, [16, 8])
        self.assertEqual(grid.score, 16)

    def test_no_moves(self):
        grid = Grid2048(4, 4)
        self.assertFalse(grid.no_moves())
        for i in range(4):
            for j in range(4):
                grid[i][j] = 2 ** (i + j)
        self.assertTrue(grid.no_moves())

    def test_no_moves_2(self):
        grid = Grid2048(4, 4)
        self.assertFalse(grid.no_moves())
        for i in range(4):
            for j in range(4):
                grid[i][j] = 2 ** (i + 1)
        self.assertFalse(grid.no_moves())

    def test_moved(self):
        grid = Grid2048(4, 4)
        shifted = [[2, 2, 4, 4], [2, 2, 4, 4], [2, 2, 4, 4], [2, 2, 4, 4]]
        self.assertTrue(grid.moved(shifted))
        self.assertEqual(grid[0][0], 2)
        self.assertEqual(grid.moves, 1)
        self.assertEqual(grid.state, grid.STATES.IDLE)

    def test_shift_up(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 8, 0], [2, 4, 0, 0], [0, 0, 8, 0], [0, 32, 0, 16]]
        grid.shift_up()
        self.assertEqual(grid[0][0], 4)
        self.assertEqual(grid[0][1], 4)
        self.assertEqual(grid[0][2], 16)
        self.assertEqual(grid[0][3], 16)
        self.assertEqual(grid.state, grid.STATES.IDLE)

    def test_shift_down(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 8, 0], [2, 4, 0, 0], [0, 0, 8, 0], [0, 32, 0, 16]]
        grid.shift_down()

        self.assertEqual(grid[3][0], 4)
        self.assertEqual(grid[3][1], 32)
        self.assertEqual(grid[3][2], 16)
        self.assertEqual(grid[3][3], 16)

    def test_shift_left(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 2, 0], [0, 4, 4, 0], [2, 0, 8, 0], [0, 32, 16, 16]]
        grid.shift_left()
        self.assertEqual(grid[0][0], 4)
        self.assertEqual(grid[1][0], 8)
        self.assertEqual(grid[2][0], 2)
        self.assertEqual(grid[2][1], 8)
        self.assertEqual(grid[3][0], 32)

        self.assertEqual(grid.state, grid.STATES.IDLE)

    def test_shift_right(self):
        grid = Grid2048(4, 4)
        grid._grid = [[2, 0, 2, 0], [0, 4, 4, 0], [2, 0, 8, 0], [0, 32, 16, 16]]
        grid.shift_right()
        self.assertEqual(grid[0][3], 4)
        self.assertEqual(grid[1][3], 8)
        self.assertEqual(grid[2][2], 2)
        self.assertEqual(grid[2][3], 8)
        self.assertEqual(grid[3][3], 32)

    def test_grid_vertical(self):
        grid = Grid2048(3, 5)
        empty_fields = grid.get_empty_fields()
        grid.shift_up()
        grid.shift_down()
        grid.shift_left()
        grid.shift_right()
        self.assertNotEqual(grid.get_empty_fields(), empty_fields)

    def test_grid_horizontal(self):
        grid = Grid2048(5, 3)
        empty_fields = grid.get_empty_fields()
        grid.shift_up()
        grid.shift_down()
        grid.shift_left()
        grid.shift_right()
        self.assertNotEqual(grid.get_empty_fields(), empty_fields)


if __name__ == "__main__":
    unittest.main()
