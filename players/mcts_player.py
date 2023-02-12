"""AI player using Monte Carlo Tree Search algorithm"""
import math
from copy import deepcopy
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class MCTSNode:
    """Node in the Monte Carlo Tree Search tree"""

    c = 0.01

    def __init__(self, grid: Grid2048, direction: DIRECTION):
        self.direction = direction
        self.grid = grid
        self.visits = 0
        self.value = 0
        self.parent: MCTSNode = None  # type: ignore
        self.children = []
        self.valid_moves = helpers.get_valid_moves(self.grid)

    def __str__(self):
        if self.parent is not None:
            return f"Node(dir:{self.direction}, vis:{self.visits}, val:{self.value}, dph:{self.depth},'uct:{self.uct}', children:{len(self.children)})"
        else:
            return f"Root(dir:{self.direction}, vis:{self.visits}, val:{self.value}, dph:{self.depth},'uct:{self.uct}', children:{len(self.children)})"

    @property
    def depth(self):
        d = 0
        node = self
        while node.parent:
            node = node.parent
            d += 1
        return d

    @property
    def uct(self):
        return (
            self.value / self.visits
            + self.c * math.sqrt(2 * math.log(self.parent.visits) / self.visits)
            if self.visits > 0
            else math.inf
        )

    @property
    def rave(self):
        return (
            (self.value + self.parent.value) / (self.visits + self.parent.visits)
            if self.visits > 0
            else math.inf
        )

    @property
    def is_terminal(self):
        return self.grid.no_moves

    def get_best_child(self):
        node = self
        while node.children:
            node = max(node.children, key=lambda x: x.uct)
        return node

    def add_child(self, child):
        if child.direction not in self.valid_moves:
            raise ValueError("Invalid move")
        child.parent = self
        self.children.append(child)
        # self.valid_moves.remove(child.direction)

    def update(self, value):
        self.visits += 1
        self.value += value

    def backpropagate(self, value):
        self.update(value)
        if self.parent:
            self.parent.backpropagate(value)

    def expand(self):
        for direction in self.valid_moves:
            new_grid = deepcopy(self.grid)
            new_grid.move(MoveFactory.create(direction), add_tile=True)
            self.add_child(MCTSNode(new_grid, direction))
        return choice(self.children)

    def simulate(self, sim_l=math.inf):
        grid = deepcopy(self.grid)
        s = 0
        while not grid.no_moves and (s < sim_l or sim_l < 0):
            s += 1
            direction = choice(list(DIRECTION))
            grid.move(MoveFactory.create(direction))
        return grid


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    # Length of the simulation. How many times the simulation is run
    sim_length = 256

    # Number of random steps to take before evaluating the grid.
    # Set to positive integer to evaluate the grid after a certain number of random moves.
    # Set to 0 to evaluate the grid after each move.
    # Set to -1 to evaluate the grid after the game is over.
    # Be careful with this parameter, as it can cause the simulation to take a very long time.
    # Also, make sure that the evaluation function will return proper values for the grid.
    # By defalut, the evaluation function returns the mean of the values multiplied by the number empty tiles,
    # so for terminal nodes, the return value will always be 0.
    rnd_steps = 0

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.root: MCTSNode

    def play(self, *args, **kwargs) -> bool:
        self.root = MCTSNode(deepcopy(self.grid), None)  # type: ignore
        move = MoveFactory.create(self.get_best_direction())
        return self.grid.move(move)

    def get_best_direction(self):
        for _ in range(self.sim_length):
            node = self.root.get_best_child()
            if node.is_terminal:
                score = -2 / math.sqrt(node.depth)
                node.update(score)
                node.backpropagate(score)
                continue
            child = node.expand()
            score = self.evaluate(child.simulate(self.rnd_steps))
            child.update(score)
            child.backpropagate(score)

        return self.select_move()

    def select_move(self):
        direction = max(self.root.children, key=lambda x: x.visits).direction
        return direction

    def evaluate(self, grid):
        """Return the score of the grid"""
        val_move_mean = helpers.values_mean(grid) / grid.moves if grid.moves > 0 else 0
        zeros = helpers.zeros(grid) / (self.height * self.width)
        max_tile = helpers.max_tile(grid)
        val = [
            math.sqrt(
                helpers.monotonicity2(grid) * helpers.smoothness(grid) * val_move_mean
            )
            / 50,
            helpers.higher_on_edge(grid) * math.log(2, max_tile) * val_move_mean / 100,
            pow(2, val_move_mean * zeros),
        ]
        # print(val)
        return sum(val)
