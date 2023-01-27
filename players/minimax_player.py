"""AI player using Minimax algorithm"""
from copy import deepcopy
from grid2048 import helpers

from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_score = float("-inf")
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
            score = float("-inf")
            for direction in DIRECTION:
                # new_grid, moved = self.move(grid, direction, True)
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
            score = float("inf")
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

    def evaluate(self, grid):
        """Return the score of the grid"""
        max_val = helpers.max_tile(grid)
        move_score = grid.last_move.score
        edge_val = max_val // 2 if max_val > 256 else 256

        val = [
            # 0.1 * move_score,
            # (helpers.shift_score(grid)),
            1 * grid.score,
            0.1 * max_val,
            2 * helpers.zeros(grid),
            0.8 * helpers.pairs(grid, [2, 4]),
            0.4 * helpers.pairs(grid, [8, 16, 32, 64]),
            0.2 * helpers.pairs(grid, [128, 256, 512, 1024]),
            12 * helpers.low_to_high(grid, 4),
            0.06 * helpers.smoothness(grid),
            # 0.2 * helpers.zero_field(grid) * high_val,
            0.6 * helpers.monotonicity(grid),
            # helpers.high_vals_on_edge(grid, edge_val),
            0.28 * helpers.higher_on_edge(grid),
            # 0.05 * helpers.values_mean(grid) / helpers.count_vals_lte(grid, 4),
        ]
        print(grid, val)
        return sum(val)
