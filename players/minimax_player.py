"""AI player using Minimax algorithm"""
from copy import deepcopy
from random import shuffle
from grid2048 import helpers

from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    depth = 5

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
            score = self.minimax(new_grid, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = direction
        return best_move

    def minimax(self, grid, depth, maximizing):
        if grid.no_moves or depth == 0:
            return self.evaluate(grid)
        if maximizing:
            best_score = float("-inf")
            for direction in DIRECTION:
                # new_grid, moved = self.move(grid, direction, True)
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, False)
                best_score = max(best_score, score)
        else:
            best_score = float("inf")
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                if not moved:
                    continue
                # new_grid.add_random_tile(new_grid.get_empty_fields())
                score = self.minimax(new_grid, depth - 1, True)
                best_score = min(best_score, score)
        return best_score

    def evaluate(self, grid):
        """Return the score of the grid"""
        max_val = helpers.max_tile(grid)
        move_score = grid.last_move.score
        high_val = max_val // 4 if max_val > 512 else 512
        val_move_mean = helpers.values_mean(grid) / grid.moves

        val = [
            # # 0.1 * grid.score,
            # 1 * helpers.grid_sum(grid),
            helpers.zeros(grid),
            0.1 * helpers.monotonicity2(grid),
            # 2 * helpers.smoothness(grid),
            # # helpers.pairs(grid, [2, 4, 8]),
            # # 1.2 * helpers.pairs(grid, [32, 64, 128, 256]),
            # # 1.4 * helpers.pairs(grid, [512, 1024, 2048, 4096]),
            # 0.1 * helpers.higher_on_edge(grid),
            # 0.1 * helpers.high_vals_in_corner(grid, helpers.max_tile(grid)),
            # # helpers.max_tile(grid),
            val_move_mean,
        ]
        print(val)
        return sum(val)
