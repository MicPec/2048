"""AI player using Expectimax algorithm"""
from copy import deepcopy
from math import log, sqrt
from random import choice

from grid2048 import helpers
from grid2048.helpers import Evaluator
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.evaluator = Evaluator(grid)
        self.register_heuristics()

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
        if maximize is True:
            best_value = float("-inf")
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=False)
                if not moved:
                    continue
                value = self.expectimax(new_grid, depth - 1, False)
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            # for direction in DIRECTION:
            #     new_grid = deepcopy(grid)
            #     move = MoveFactory.create(direction)
            #     moved = new_grid.move(move, add_tile=True)
            #     if not moved:
            #         continue
            #     values.append(self.expectimax(new_grid, depth - 1, True))
            empty = grid.get_empty_fields()
            for tile in empty:
                new_grid = deepcopy(grid)
                new_grid.data[tile[0]][tile[1]] = 2
                values.append(self.expectimax(new_grid, depth - 1, True))
            return sum(values) / len(values) if values else 0

    def register_heuristics(self):
        self.evaluator.register(
            "zeros",
            1.42,
            lambda grid: helpers.zeros(grid) * log(helpers.max_tile(grid), 2),
        )
        self.evaluator.register("pairs", 0.29, lambda grid: helpers.pairs(grid, [2, 4]))
        self.evaluator.register(
            "pairs2", 1.15, lambda grid: helpers.pairs(grid, [8, 16, 32, 64])
        )
        self.evaluator.register(
            "pairs3", 1.05, lambda grid: helpers.pairs(grid, [128, 256, 512, 1024])
        )
        self.evaluator.register(
            "smoothness", 0.38, lambda grid: helpers.smoothness(grid)
        )
        self.evaluator.register(
            "monotonicity", 0.70, lambda grid: helpers.monotonicity(grid)
        )
        # self.evaluator.register(
        #     "high_vals_on_edge",
        #     0.7,
        #     lambda grid: helpers.high_vals_on_edge(grid, edge_val),
        # )
        self.evaluator.register(
            "high_vals_in_corner",
            0.85,
            lambda grid: helpers.high_vals_in_corner(grid, helpers.max_tile(grid)),
        )
        self.evaluator.register(
            "higher_on_edge", 2.37, lambda grid: helpers.higher_on_edge(grid)
        )
        self.evaluator.register("score", 0.82, lambda grid: grid.score)

    def evaluate(self, grid):
        """Return the score of the grid"""
        max_tile = helpers.max_tile(grid)
        edge_val = max_tile // 2 if max_tile > 256 else 256

        # print(grid, self.evaluator)
        val_move_mean = helpers.values_mean(grid) / grid.moves if grid.moves > 0 else 0
        zeros = helpers.zeros(grid) / (self.height * self.width)
        return val_move_mean + zeros
