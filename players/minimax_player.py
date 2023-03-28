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

    def get_best_move(self, grid: Grid2048) -> DIRECTION | None:
        best_score = -math.inf
        best_move = None
        for direction in DIRECTION:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=False)
            if not moved:
                continue
            score = self.minimax(new_grid, -math.inf, math.inf, self.depth, False)
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
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=False)
                if not moved:
                    continue
                score = self.minimax(new_grid, alpha, beta, depth - 1, False)
                alpha = max(alpha, score)
                if beta <= alpha:  # beta cut-off
                    break
            return alpha
        else:
            for _ in grid.get_empty_fields():
                new_grid = deepcopy(grid)
                new_grid.add_random_tile(new_grid.get_empty_fields())
                if new_grid.no_moves:
                    return 0
                score = self.minimax(new_grid, alpha, beta, depth - 1, True)
                beta = min(beta, score)
                if beta <= alpha:  # alpha cut-off
                    break
            return beta

    def evaluate(self, grid: Grid2048, move: Move | None = None):
        """Return the score of the grid"""
        val_mean = helpers.values_mean(grid)
        zeros = helpers.zeros(grid) / (self.height * self.width)
        # grid_sum = helpers.grid_sum(grid)
        # sum_steps = grid_sum / grid.moves * 0.75 if grid.moves > 0 else 0
        max_tile = helpers.max_tile(grid)
        # max_in_corner = helpers.high_vals_in_corner(grid, max_tile)
        high_on_edge = helpers.high_vals_on_edge(grid, max_tile // 2)
        if grid.no_moves:
            return -math.inf
        val = [
            0.3 * math.log(high_on_edge if high_on_edge > 0 else 1),
            # math.log(max_in_corner if max_in_corner > 0 else 1) / 2,
            0.2 * helpers.monotonicity(grid),
            0.05 * helpers.smoothness(grid),
            5 * zeros,
            grid.score / grid.moves if grid.moves > 0 else 0,
            val_mean,
        ]
        # print(val)
        return sum(val)
