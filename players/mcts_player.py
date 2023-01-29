"""AI player using Monte Carlo Tree Search algorithm"""
from copy import deepcopy
from math import log, sqrt
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class MCTSNode:
    c = 1.41

    def __init__(self, grid: Grid2048, direction: DIRECTION):
        self.direction = direction
        self.grid = grid
        self.visits = 0
        self.value = 0
        self.parent: MCTSNode = None
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
    def q(self):
        return self.value / self.visits

    @property
    def u(self):
        return sqrt(2 * log(self.parent.visits) / self.visits)

    @property
    def uct(self):
        return self.q + self.c * self.u

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self.children

    @property
    def is_fully_expanded(self):
        return len(self.children) >= len(self.valid_moves) + helpers.zeros(self.grid)

    @property
    def is_terminal(self):
        return self.grid.no_moves

    def select(self):
        return self.get_best_child() if self.is_fully_expanded else self.expand()

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
        if self.is_fully_expanded:
            raise ValueError("Node is already expanded")
        direction = choice(self.valid_moves)
        new_grid = deepcopy(self.grid)
        new_grid.move(MoveFactory.create(direction))
        child = MCTSNode(new_grid, direction)
        self.add_child(child)
        # self.backpropagate(child.simulate())
        return child

    def simulate(self):
        grid = deepcopy(self.grid)
        while not grid.no_moves:
            direction = choice(self.valid_moves)
            grid.move(MoveFactory.create(direction))
        return grid


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 3
    n_sim = 10

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.root: MCTSNode

    def play(self, *args, **kwargs) -> bool:
        self.root = MCTSNode(deepcopy(self.grid), None)
        move = MoveFactory.create(self.get_best_direction())
        return self.grid.move(move)

    def get_best_direction(self):
        for _ in range(self.n_sim):
            node = self.root.select()
            if node.is_leaf:
                node.backpropagate(self.evaluate(node.grid))
            else:
                node.backpropagate(node.simulate().score)
        return self.root.get_best_child().direction

    def evaluate(self, grid):
        """Return the score of the grid"""
        val = [
            0.1 * grid.score,
            # helpers.zeros(grid),
            # 0.1 * helpers.monotonicity(grid),
            # helpers.smoothness(grid),
            # helpers.higher_on_edge(grid),
            # helpers.max_tile(grid),
        ]
        # print(grid, val)
        return sum(val)
