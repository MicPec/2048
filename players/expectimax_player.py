"""AI player using Expectimax algorithm"""
from copy import deepcopy
from random import shuffle

from grid2048.grid2048 import Grid2048, MoveFactory, MOVES
from players.player import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    # dirs = ["l", "u", "d", "r"]
    depth = 3

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        # self.moves = {
        #     "u": self.grid.shift_up,
        #     "d": self.grid.shift_down,
        #     "l": self.grid.shift_left,
        #     "r": self.grid.shift_right,
        # }

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = float("-inf")
        best_move = None

        for direction in MOVES:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=True)
            if new_grid.no_moves:
                return direction
            if not moved:
                continue
            value = self.expectimax(new_grid, move, self.depth, "ai")
            if value > best_value:
                best_value = value
                best_move = direction
        return best_move

    def expectimax(self, grid, move, depth, player):
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid, move)
        if player == "ai":
            best_value = float("-inf")
            for direction in MOVES:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=False)
                if not moved:
                    continue
                value = self.expectimax(new_grid, move, depth - 1, "random")
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            for direction in MOVES:
                new_grid = deepcopy(grid)
                new_grid.add_random_tile(new_grid.get_empty_fields())
                values.append(self.expectimax(new_grid, None, depth - 1, "ai"))
            return sum(values) / len(values)

    def evaluate(self, grid, move=None):
        """Return the score of the grid"""
        maxi = self.max_tile(grid)
        score = move.score if move else 0

        val = [
            score,
            # (0.01 * self.grid_sum(grid) + 0.001 * grid.score) / 2,
            # # 0.1 * self.grid_sum(grid),
            0.6 * self.zeros(grid),
            0.1 * self.pairs(grid),
            # 1.25 / (self.smoothness(grid) + 1),
            # 0.01 * self.max_tile(grid),
            0.005 * self.zero_field(grid) * self.max_tile(grid),
            0.001 * self.monotonicity(grid),
            self.high_vals_on_edge(grid, 512),
        ]
        print(val)
        return sum(val)
