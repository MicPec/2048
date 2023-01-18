"""AI player using Monte Carlo Tree Search algorithm"""
from copy import deepcopy
from math import sqrt
from random import choice

from grid2048.grid2048 import Grid2048, MOVES, MoveFactory
from grid2048 import helpers
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
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)
        # return move.is_valid

    def get_best_move(self, grid) -> MOVES:
        # Initialize a dictionary to store the number of wins for each move
        wins = {MOVES.UP: 0, MOVES.DOWN: 0, MOVES.LEFT: 0, MOVES.RIGHT: 0}

        for direction, _ in wins.items():
            for _ in range(self.n_sim):
                # Make a copy of the grid to simulate a move
                sim_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                # print("*****", direction)
                moved = sim_grid.move(move, add_tile=False)
                if moved and not sim_grid.no_moves:
                    wins[direction] += self.simulate(sim_grid)
                # else:
                #     break
        w = max(wins, key=wins.get)
        return w

    def simulate(self, grid):

        depth = 0
        while depth < self.max_depth:
            depth += 1
            # select a random move
            direction = choice(list(MOVES))
            move = MoveFactory.create(direction)
            # print("***", direction)
            moved = grid.move(move, add_tile=True)
            if not moved or grid.no_moves:
                break
        # return score
        return self.evaluate(grid, move)

    def evaluate(self, grid, move):
        """Return the score of the grid"""
        maxi = helpers.max_tile(grid)
        high_val = (sqrt(maxi) - 2) ** 2 if maxi > 512 else 512
        score = move.score if move else 0
        val = [
            # 0.1 * score,
            (0.01 * helpers.shifted_sum(grid) + 0.001 * grid.score) / 2,
            # 0.1 * helpers.grid_sum(grid),
            0.5 * helpers.zeros(grid),
            0.2 * helpers.pairs(grid),
            1.25 / (helpers.smoothness(grid) + 1),
            # 0.01 * helpers.max_tile(grid),
            0.005 * helpers.zero_field(grid) * helpers.max_tile(grid),
            0.001 * helpers.monotonicity(grid),
            helpers.high_vals_on_edge(grid, 512),
            1.0 * helpers.high_vals_on_edge(grid, high_val),
            # 0.75 * helpers.low_to_high(grid, maxi // 4),
        ]
        # print(val)
        return sum(val)
