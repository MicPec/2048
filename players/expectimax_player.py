"""AI player using Expectimax algorithm"""
from copy import deepcopy
from math import sqrt
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = float("-inf")
        best_move = None

        for direction in DIRECTION:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=True)
            if new_grid.no_moves:
                return direction
            value = self.expectimax(new_grid, self.depth, True)
            if not moved:
                continue
            if value > best_value:
                best_value = value
                best_move = direction
        return best_move

    def expectimax(self, grid, depth, maximize):
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid)
        if maximize == True:
            best_value = float("-inf")
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                value = self.expectimax(new_grid, depth - 1, False)
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                values.append(self.expectimax(new_grid, depth - 1, True))
            return sum(values) / len(values)

    def evaluate(self, grid):
        """Return the score of the grid"""
        max_val = helpers.max_tile(grid)
        move_score = grid.last_move.score
        edge_val = max_val // 2 if max_val > 256 else 256

        val = [
            # 0.1 * move_score,
            # (helpers.shift_score(grid)),
            0.52 * grid.score,
            1 * max_val,
            33 * helpers.zeros(grid),
            0.8 * helpers.pairs(grid, [2, 4]),
            0.2 * helpers.pairs(grid, [8, 16, 32, 64]),
            0.01 * helpers.pairs(grid, [128, 256, 512, 1024]),
            helpers.low_to_high(grid, 4),
            (helpers.smoothness(grid)) / -0.001,
            # 0.2 * helpers.zero_field(grid) * high_val,
            0.3 * helpers.monotonicity(grid),
            helpers.high_vals_on_edge(grid, edge_val),
            0.3 * helpers.higher_on_edge(grid),
            0.05 * helpers.values_mean(grid) / helpers.count_vals_lte(grid, 4),
        ]
        print(grid, val)
        return sum(val)
