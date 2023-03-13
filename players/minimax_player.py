"""AI player using Minimax algorithm"""
import math
from copy import deepcopy
from grid2048 import helpers

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
            score = self.minimax(
                new_grid, float("-inf"), float("inf"), self.depth, True
            )
            if score > best_score:
                best_score = score
                best_move = direction
        return best_move

    def minimax(self, grid, alpha, beta, depth, maximizing):
        """Return the best score for the grid"""
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
                score = self.minimax(new_grid, alpha, beta, depth - 1, False)
                alpha = max(alpha, score)
                if alpha >= beta:  # beta cut-off
                    break
            return alpha
        else:
            best_score = math.inf
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                # new_grid.add_random_tile(new_grid.get_empty_fields())
                score = self.minimax(new_grid, alpha, beta, depth - 1, True)
                beta = min(beta, score)
                if alpha >= beta:  # alpha cut-off
                    break
            return beta

    def evaluate(self, grid, move: Move | None = None):
        """Return the score of the grid"""
        max_val = helpers.max_tile(grid)
        move_score = grid.last_move.score
        edge_val = max_val // 2 if max_val > 256 else 256

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
