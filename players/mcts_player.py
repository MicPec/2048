"""AI player using Expectimax algorithm"""
from copy import deepcopy
from math import sqrt
from random import choice

from grid2048.grid2048 import Grid2048, MOVES, MoveFactory
from players.player import AIPlayer


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 20  # maximum depth to simulate
    n_sim = 30  # number of simulations to run for each move

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.grid, self.get_best_move(self.grid))
        self.grid.move(move)
        return move.is_valid

    def get_best_move(self, grid) -> MOVES:
        # Initialize a dictionary to store the number of wins for each move
        wins = {MOVES.UP: 0, MOVES.DOWN: 0, MOVES.LEFT: 0, MOVES.RIGHT: 0}

        for direction, _ in wins.items():
            for _ in range(self.n_sim):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                move = MoveFactory.create(sim_grid, direction)
                if move.is_valid:
                    sim_grid = grid.move(move, copy=False)
                    result = self.simulate(sim_grid)
                    wins[direction] += result
        w = max(wins, key=wins.get)
        return w

    def simulate(self, grid):

        depth = 0
        while depth < self.max_depth:
            depth += 1
            # select a random move
            direction = choice(list(MOVES))
            print("**************", direction, "**************")
            move = MoveFactory.create(grid, direction)
            # grid = grid.move(move, copy=False, add_tile=False)
            move()
            if not move.is_valid or grid.no_moves():
                break
        # return score
        return self.evaluate(grid, move)

    def evaluate(self, grid, move):
        """Return the score of the grid"""
        maxi = self.max_tile(grid)
        high_val = (sqrt(maxi) - 2) ** 2 if maxi > 512 else 512
        score = move.score if move else 0
        val = [
            score,
            (0.01 * self.grid_sum(grid) + 0.001 * grid.score) / 2,
            # 0.1 * self.grid_sum(grid),
            0.5 * self.zeros(grid),
            0.2 * self.pairs(grid),
            1.25 / (self.smoothness(grid) + 1),
            # 0.01 * self.max_tile(grid),
            0.005 * self.zero_field(grid) * self.max_tile(grid),
            0.001 * self.monotonicity(grid),
            self.high_vals_on_edge(grid, 512),
            1.0 * self.high_vals_on_edge(grid, high_val),
            # 0.75 * self.low_to_high(grid, maxi // 4),
        ]
        print(val)
        return sum(val)
