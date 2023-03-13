"""AI player using Minimax algorithm"""
import math
from copy import deepcopy

from grid2048 import DIRECTION, Grid2048, Move, MoveFactory, helpers
from players import AIPlayer


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))  # type: ignore
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_score = -math.inf
        best_move = None
        for direction in DIRECTION:
            # new_grid, moved = self.move(grid, direction)
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=True)
            if new_grid.no_moves:
                return direction
            if not moved:
                continue
            score = self.minimax(new_grid, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = direction
        return best_move

    def minimax(self, grid, depth, maximizing):
        if grid.no_moves or depth == 0:
            return self.evaluate(grid)
        if maximizing:
            best_score = -math.inf
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, False)
                best_score = max(best_score, score)
        else:
            best_score = math.inf
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, True)
                best_score = min(best_score, score)
        return best_score

    def evaluate(self, grid, move: Move | None = None):
        """Return the score of the grid"""
        val_move_mean = helpers.values_mean(grid) / grid.moves if grid.moves > 0 else 0
        zeros = helpers.zeros(grid) / (self.height * self.width)
        max_tile = helpers.max_tile(grid)
        val = [
            math.sqrt(
                helpers.monotonicity(grid) * helpers.smoothness(grid) * val_move_mean
            )
            / 50,
            # helpers.higher_on_edge(grid) * math.log(2, max_tile) * val_move_mean / 100,
            pow(2, val_move_mean * zeros),
        ]
        # print(val)
        return sum(val)
