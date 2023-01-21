import unittest

from grid2048.grid2048 import Grid2048, DIRECTION
from players.player import AIPlayer


class TestPlayer(AIPlayer):
    def evaluate(self, grid):
        """Returns the score of the grid."""
        pass

    def play(self, *args, **kwargs) -> bool:
        return True


class TestAIPlayer(unittest.TestCase):
    def setUp(self):
        self.grid = Grid2048(4, 4)
        self.player = TestPlayer(self.grid)
