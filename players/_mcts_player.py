"""AI player using Monte Carlo Tree Search algorithm"""
from copy import deepcopy
from math import log, sqrt
from random import choice

from numpy import mean

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class Node:
    c = 1.41

    def __init__(self, grid: Grid2048, direction: DIRECTION):
        self.grid = grid
        self.direction = direction
        self.visits = 0
        self.value = 0
        self.parent = None
        self.children = []
        self.valid_moves = helpers.get_valid_moves(self.grid)

    def __str__(self):
        if self.parent is not None:
            return f"Node(dir:{self.direction}, vis:{self.visits}, val:{self.value}, dph:{self.depth},'uct:{self.uct}', children:{len(self.children)})"
        else:
            return "root"

    def add_child(self, child_node):
        if child_node.direction in self.valid_moves:
            self.valid_moves.remove(child_node.direction)
        child_node.parent = self
        self.children.append(child_node)

    def update(self, value):
        self.visits += 1
        self.value += value

    @property
    def depth(self):
        d = 0
        node = self
        while node.parent:
            d += 1
            node = node.parent
        return d

    @property
    def uct(self):
        return (
            self.value / self.visits
            + self.c * sqrt(2 * log(self.parent.visits) / self.visits)
            if self.visits
            else float("-inf")
        )

    @property
    def expanded(self):
        return (
            len(self.children) >= len(self.valid_moves) * helpers.zeros(self.grid) + 1
        )

    def get_best_child(self):
        return max(self.children, key=lambda x: x.visits)

    def is_valid(self, direction: DIRECTION):
        return direction in self.valid_moves


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 20
    n_sim = 2000

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.root: Node

    def play(self, *args, **kwargs) -> bool:
        self.root = Node(deepcopy(self.grid), None)
        move = MoveFactory.create(self.get_best_direction())
        return self.grid.move(move)

    def get_best_direction(self) -> DIRECTION:

        for _ in range(self.n_sim):
            print("*" * 40)
            self.process_node(self.root)
            # node = self.expand(node)
        best_child = max(self.root.children, key=lambda x: x.visits)
        # self.root = best_child
        print("Best child:", best_child)
        return best_child.direction

    def process_node(self, node):
        node = self.select(node)
        if node.depth < self.max_depth and not node.expanded:
            child = self.expand(node)
            score = self.simulate(child)
        else:
            score = self.evaluate(node.grid)
        self.backpropagate(node, score)
        print("score:", score, "node:", node.value)
        # return node

    def select(self, node):
        """Traverse the tree using UCT to select the best child node to expand"""
        while node.children:
            best_child = max(node.children, key=lambda x: x.uct)
            node = best_child
        print("Selected node:", node)
        return node

    # def expand(self, node: Node):
    #     """Expand the node by adding a new child"""
    #     for direction in DIRECTION:
    #         grid = deepcopy(node.grid)
    #         if grid.move(MoveFactory.create(direction), add_tile=True):
    #             child = Node(grid, direction)
    #             node.add_child(child)
    #             self.evaluate(child.grid)
    #             if child.grid.no_moves:
    #                 child.value = -child.value
    #     child = choice(node.children)
    #     # child = self.select(node)
    #     return child

    def expand(self, node: Node):
        """Expand the node by adding a new child"""
        # if not node.expanded:
        #     return node
        direction = (
            choice(node.valid_moves)
            if node.valid_moves != []
            else choice(list(DIRECTION))
        )
        grid = deepcopy(node.grid)
        grid.move(MoveFactory.create(direction), add_tile=True)
        child = Node(grid, direction)
        node.add_child(child)
        return child

    def simulate(self, node: Node):
        """Simulate the game from the node using a random playout policy"""
        grid = deepcopy(node.grid)
        sim = 0
        while not grid.no_moves:  # or sim < 10:  # self.n_sim:
            sim += 1
            direction = choice(list(DIRECTION))
            grid.move(MoveFactory.create(direction), add_tile=True)
        return self.evaluate(grid)

    def backpropagate(self, node: Node, score):
        """Backpropagate the score to update the information in the tree"""
        while node:
            node.update(score)
            node = node.parent

    def get_root(self):
        node = self.root
        while node:
            self.root = node
            node = node.parent
        return self.root

    def evaluate(self, grid):
        """Return the score of the grid"""
        val = [
            0.1 * grid.score,
            4 * helpers.zeros(grid),
            # 0.1 * helpers.monotonicity(grid),
            # helpers.smoothness(grid),
            # helpers.higher_on_edge(grid),
            # helpers.max_tile(grid),
        ]
        print(grid, val)
        return sum(val)
