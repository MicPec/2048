"""AI player using Monte Carlo simulation algorithm"""

import math
from copy import deepcopy
from random import choice

from grid2048 import DIRECTION, Grid2048, MoveFactory, helpers
from players import AIPlayer


class MCSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    sim_length = 5  # maximum length to simulate
    sim_count = 200  # number of simulations to run for each move

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid) -> DIRECTION:
        # Initialize a dictionary to store the number of wins for each move
        wins = {direction: 0.0 for direction in DIRECTION}

        for direction in DIRECTION:
            for _ in range(self.sim_count):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                if sim_grid.move(move, add_tile=True):
                    wins[direction] += self.simulate(sim_grid)
        return max(wins, key=wins.get)  # type: ignore

    def simulate(self, grid):
        sim_grid = deepcopy(grid)
        sim_n = 0
        while sim_n < self.sim_length:
            sim_n += 1
            # select a random move
            direction = choice(list(DIRECTION))
            move = MoveFactory.create(direction)
            if not sim_grid.move(move, add_tile=True) or sim_grid.no_moves:
                break
        return self.evaluate(sim_grid)

    def evaluate(self, grid):
        """Return the score of the grid"""
        val_mean = helpers.values_mean(grid)
        zeros = helpers.zeros(grid) / (self.height * self.width)
        grid_sum = helpers.grid_sum(grid)
        sum_steps = grid_sum / grid.moves * 0.75 if grid.moves > 0 else 0
        max_tile = helpers.max_tile(grid)
        high_on_edge = helpers.high_vals_on_edge(grid, max_tile // 2)

        # Avoid multiplying by zeros to prevent zero scores for terminal states
        val = [
            math.log(high_on_edge if high_on_edge > 0 else 1),
            helpers.monotonicity(grid) * (sum_steps + 1) * 2,
            helpers.smoothness(grid) * (sum_steps + 1) * 2,
            (zeros + 0.1) * math.log2(max_tile) * (sum_steps + 1) / 2,
            val_mean / math.log2(max_tile) * 4,
        ]
        return sum(val)
