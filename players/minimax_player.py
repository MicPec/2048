"""AI player using Minimax algorithm"""

import math
from copy import deepcopy

from grid2048 import DIRECTION, Grid2048, Move, MoveFactory, helpers
from players import AIPlayer


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    depth = 5

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))  # type: ignore
        return self.grid.move(move)

    def get_best_move(self, grid: Grid2048) -> DIRECTION | None:
        best_score = -math.inf
        best_move = None
        for direction in DIRECTION:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=False)
            if not moved:
                continue
            score = self.minimax(new_grid, -math.inf, math.inf, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = direction
        return best_move

    def minimax(
        self, grid: Grid2048, alpha: float, beta: float, depth: int, maximizing: bool
    ) -> float:
        """Return the best score for the grid"""
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid)

        if maximizing:
            max_score = -math.inf
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                if not new_grid.move(move, add_tile=False):
                    continue
                score = self.minimax(new_grid, alpha, beta, depth - 1, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:  # beta cut-off
                    break
            return max_score
        else:
            min_score = math.inf
            empty_fields = grid.get_empty_fields()
            if not empty_fields:
                return self.minimax(grid, alpha, beta, depth - 1, True)

            for field in empty_fields:
                new_grid = deepcopy(grid)
                new_grid.put_random_tile(*field)
                score = self.minimax(new_grid, alpha, beta, depth - 1, True)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:  # alpha cut-off
                    break
            return min_score

    def evaluate(self, grid: Grid2048, move: Move | None = None):
        """Return the score of the grid"""
        val_mean = helpers.values_mean(grid)
        zeros = helpers.zeros(grid) / (self.height * self.width)
        max_tile = helpers.max_tile(grid)
        high_on_edge = helpers.high_vals_on_edge(grid, max_tile // 2)
        val = [
            0.95 * math.log(high_on_edge if high_on_edge > 0 else 1),
            0.21 * helpers.monotonicity(grid),
            0.05 * helpers.smoothness(grid),
            zeros * math.log2(max_tile),
            grid.score / grid.moves if grid.moves > 0 else 0,
        ]
        return sum(val)
