"""AI player using Expectimax algorithm"""
from copy import deepcopy
from random import choice

from grid2048 import Grid2048
from players.player import AIPlayer


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    dirs = ["l", "u", "d", "r"]
    max_depth = 20  # maximum depth to simulate
    n_sim = 30  # number of simulations to run for each move

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
        # Initialize a dictionary to store the number of wins for each move
        wins = {"u": 0, "d": 0, "l": 0, "r": 0}

        for move, _ in wins.items():
            for _ in range(self.n_sim):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                if self.move(sim_grid, move, True):
                    result = self.simulate(sim_grid)
                    wins[move] += result
        return max(wins, key=wins.get)

    def move(self, grid, direction, add_tile: bool = False):
        moved = False
        if direction == "u":
            moved = grid.shift_up(add_tile=add_tile)
        elif direction == "d":
            moved = grid.shift_down(add_tile=add_tile)
        elif direction == "l":
            moved = grid.shift_left(add_tile=add_tile)
        elif direction == "r":
            moved = grid.shift_right(add_tile=add_tile)
        return moved

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = self.max_tile(grid)
        val = [
            (0.01 * self.shifted_sum(grid) + 0.001 * grid.score) / 2,
            # # 0.1 * self.grid_sum(grid),
            0.6 * self.zeros(grid),
            0.1 * self.pairs(grid),
            # 1.25 / (self.smoothness(grid) + 1),
            # 0.01 * self.max_tile(grid),
            0.005 * self.zero_field(grid) * self.max_tile(grid),
            0.001 * self.monotonicity(grid),
            self.high_vals_on_edge(grid, 512),
            # 0.75 * self.low_to_high(grid, maxi // 4),
        ]
        # print(val)
        return sum(val)

    def simulate(self, grid):

        depth = 0
        while depth < self.max_depth:
            depth += 1
            # select a random move
            move = choice(self.dirs)
            moved = self.move(grid, move, False)
            if not moved or grid.no_moves():
                break
        # return score
        return self.evaluate(grid)
