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

    depth = 3

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.evaluator = Evaluator()
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
        self.evaluator.register("zeros", 0.45)
        self.evaluator.register("pairs", 0.6)
        self.evaluator.register("pairs2", 0.2)
        self.evaluator.register("pairs3", 0.1)
        self.evaluator.register("smoothness", 1)
        self.evaluator.register("monotonicity", 0.2)
        self.evaluator.register("high_vals_on_edge", 0.02)
        self.evaluator.register("high_vals_in_corner", 0.2)
        self.evaluator.register("higher_on_edge", 0.01)
        self.evaluator.register("score", 0.2)

    def evaluate(self, grid):
        """Return the score of the grid"""
        max_tile = helpers.max_tile(grid)
        edge_val = max_tile // 2 if max_tile > 256 else 256

        self.evaluator["zeros"] = helpers.zeros(grid) * log(max_tile, 2)
        self.evaluator["pairs"] = helpers.pairs(grid, [2, 4])
        self.evaluator["pairs2"] = helpers.pairs(grid, [8, 16, 32, 64])
        self.evaluator["pairs3"] = helpers.pairs(grid, [128, 256, 512, 1024])
        self.evaluator["smoothness"] = helpers.smoothness(grid)
        self.evaluator["monotonicity"] = helpers.monotonicity(grid)
        self.evaluator["high_vals_on_edge"] = helpers.high_vals_on_edge(grid, edge_val)
        self.evaluator["high_vals_in_corner"] = helpers.high_vals_in_corner(
            grid, max_tile
        )
        self.evaluator["higher_on_edge"] = helpers.higher_on_edge(grid)
        self.evaluator["score"] = grid.score
        # print(grid, self.evaluator)
        return self.evaluator.evaluate()
