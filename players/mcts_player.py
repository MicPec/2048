"""AI player using Monte Carlo Tree Search algorithm"""
from copy import deepcopy
from math import sqrt
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 250  # maximum depth to simulate
    n_sim = 50  # number of simulations to run for each move

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid) -> DIRECTION:
        # Initialize a dictionary to store the number of wins for each move
        wins = {
            DIRECTION.UP: 0,
            DIRECTION.DOWN: 0,
            DIRECTION.LEFT: 0,
            DIRECTION.RIGHT: 0,
        }

        for direction, _ in wins.items():
            for _ in range(self.n_sim):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                if sim_grid.move(move, add_tile=True):
                    wins[direction] += self.simulate(sim_grid)
        w = max(wins, key=wins.get)
        return w

    def simulate(self, grid):

        depth = 0
        while depth < self.max_depth:
            depth += 1
            # select a random move
            direction = choice(list(DIRECTION))
            move = MoveFactory.create(direction)
            moved = grid.move(move, add_tile=True)
            if not moved or grid.no_moves:
                break
        return self.evaluate(grid)

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = helpers.max_tile(grid)
        high_val = maxi // 4 if maxi > 256 else 256
        score = grid.last_move.score
        val = [
            0.5 * score,
            # (0.01 * helpers.shift_score(grid) + 0.001 * grid.score) / 2,
            0.1 * helpers.grid_sum(grid),
            12 * helpers.zeros(grid),
            0.2 * helpers.pairs(grid) * helpers.monotonicity(grid),
            # 2 / (helpers.smoothness(grid) + 1),
            # 0.01 * helpers.max_tile(grid),
            # helpers.zero_field(grid) * helpers.max_tile(grid),
            # helpers.monotonicity(grid),
            helpers.high_vals_on_edge(grid, 512),
            # 2 * helpers.high_vals_on_edge(grid, high_val),
            4 * helpers.low_to_high(grid, 256),
        ]
        print(val)
        return sum(val)
