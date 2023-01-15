"""AI player using Minimax algorithm"""
from copy import deepcopy
from random import shuffle

from grid2048 import Grid2048
from players.player import AIPlayer


class MinimaxPlayer(AIPlayer):
    """AI player using Minimax algorithm"""

    dirs = ["l", "u", "d", "r"]
    depth = 3

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.moves = {
            "u": self.grid.shift_up,
            "d": self.grid.shift_down,
            "l": self.grid.shift_left,
            "r": self.grid.shift_right,
        }

    def play(self, *args, **kwargs) -> bool:
        return self.moves[self.get_best_move(self.grid)]()

    def get_best_move(self, grid):
        best_score = float("-inf")
        best_move = None
        for move in self.dirs:
            new_grid, moved = self.move(grid, move)
            if new_grid.no_moves():
                return move
            if not moved:
                continue
            score = self.minimax(new_grid, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, grid, depth, maximizing):
        shuffle(self.dirs)
        if grid.no_moves() or depth == 0:
            return self.evaluate(grid)
        if maximizing:
            best_score = float("-inf")
            for move in self.dirs:
                new_grid, moved = self.move(grid, move, True)
                if not moved:
                    continue
                score = self.minimax(new_grid, depth - 1, False)
                best_score = max(best_score, score)
        else:
            best_score = float("inf")
            for move in self.dirs:
                # new_grid, moved = self.move(grid, move, False)
                # if not moved:
                #     continue
                new_grid = deepcopy(grid)
                new_grid.add_random_tile(new_grid.get_empty_fields())
                score = self.minimax(new_grid, depth - 1, True)
                best_score = min(best_score, score)
        return best_score

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = self.max_tile(grid)
        val = [
            (0.01 * self.shifted_sum(grid) + 0.001 * grid.score) / 2,
            # # 0.1 * self.grid_sum(grid),
            0.6 * self.zeros(grid),
            0.6 * self.pairs(grid),
            # 1.25 / (self.smoothness(grid) + 1),
            # 0.01 * self.max_tile(grid),
            # 0.005 * self.zero_field(grid) * self.max_tile(grid),
            # 0.001 * self.monotonicity(grid),
            self.high_vals_on_edge(grid, 512),
        ]
        print(val)
        return sum(val)
