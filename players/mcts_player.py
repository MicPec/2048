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
    def uct(self):
        return (
            self.value / self.visits
            + self.c * sqrt(2 * log(self.parent.visits) / self.visits)
            if self.visits > 0
            else float("inf")
        )

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self.children

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
        return

    def simulate(self):
        grid = deepcopy(self.grid)
        while not grid.no_moves:
            direction = choice(list(DIRECTION))
            grid.move(MoveFactory.create(direction))
        return grid


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 8
    n_sim = 64 * max_depth

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
        # for direction in self.root.valid_moves:
        #     new_grid = deepcopy(self.grid)
        #     new_grid.move(MoveFactory.create(direction), add_tile=False)
        #     self.root.add_child(MCTSNode(new_grid, direction))

        for _ in range(self.n_sim):
            node = self.root.get_best_child()

            if node.is_leaf and node.depth < self.max_depth and not node.is_terminal:
                node.expand()
                for node in node.children:
                    score = self.evaluate(node.grid)
                    node.update(score)
                    node.backpropagate(score)
                continue
            else:
                # node = node.get_best_child()
                score = self.evaluate(node.grid)
                node.update(score)
                node.backpropagate(score)
        print(self.root.valid_moves)
        return self.select()

    def select(self):
        direction = max(self.root.children, key=lambda x: x.visits).direction
        print(direction)
        return direction

    def evaluate(self, grid):
        """Return the score of the grid"""
        val = [
            # 0.1 * grid.score,
            0.2 * helpers.grid_sum(grid),
            12 * helpers.zeros(grid),
            0.3 * helpers.monotonicity(grid),
            8 * helpers.smoothness(grid),
            helpers.pairs(grid, [2, 4, 8, 16]),
            2 * helpers.pairs(grid, [32, 64, 128, 256]),
            4 * helpers.pairs(grid, [512, 1024, 2048, 4096]),
            0.4 * helpers.higher_on_edge(grid),
            0.2 * helpers.high_vals_in_corner(grid, helpers.max_tile(grid))
            # helpers.max_tile(grid),
        ]
        # print(grid, val)
        return sum(val)
