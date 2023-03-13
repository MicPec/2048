"""AI player using Expectimax algorithm"""
import math
from copy import deepcopy

from grid2048 import DIRECTION, Grid2048, Move, MoveFactory, helpers
from players import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    depth = 5

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))  # type: ignore
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = -math.inf
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
            best_value = -math.inf
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
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                values.append(self.expectimax(new_grid, depth - 1, True))
            return sum(values) / len(values) if values else 0

    def evaluate(self, grid, move: Move | None = None):
        """Return the score of the grid"""
        val_move_mean = helpers.values_mean(grid) / grid.moves if grid.moves > 0 else 0
        zeros = helpers.zeros(grid) / (self.height * self.width)
        max_tile = helpers.max_tile(grid)
        val = [
            math.sqrt(
                helpers.monotonicity(grid) * helpers.smoothness(grid) * val_move_mean
            )
            / 25,
            helpers.higher_on_edge(grid) * math.log(2, max_tile) * val_move_mean / 100,
            pow(2, val_move_mean * zeros),
        ]
        # print(val)
        return sum(val)
