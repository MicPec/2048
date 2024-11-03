"""User player classes for different interfaces"""

import pygame
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import PlayerInterface


class UserPlayer(PlayerInterface):
    """User player class for command line interface"""

    dirs = ["u", "d", "l", "r"]

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            "u": DIRECTION.UP,
            "d": DIRECTION.DOWN,
            "l": DIRECTION.LEFT,
            "r": DIRECTION.RIGHT,
        }

    def play(self, *args, **kwargs) -> bool:
        while True:
            direction = input("Enter a direction (u,d,l,r): ")
            if direction in self.dirs:
                break
            print("Invalid direction")
        move = MoveFactory.create(self.moves[direction])
        return self.grid.move(move)


class KivyPlayer(PlayerInterface):
    """User player class for kivy app"""

    dirs = [273, 274, 276, 275]

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            273: DIRECTION.UP,
            274: DIRECTION.DOWN,
            276: DIRECTION.LEFT,
            275: DIRECTION.RIGHT,
        }

    def play(self, *args, **kwargs) -> bool:
        while True:
            direction = kwargs.get("dir")
            if direction in self.dirs:
                break
            print("Invalid direction")
        move = MoveFactory.create(self.moves[direction])
        return self.grid.move(move)


class PygamePlayer(PlayerInterface):
    """User player class for pygame app"""

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.moves = {
            pygame.K_UP: DIRECTION.UP,  # pylint: disable=no-member
            pygame.K_DOWN: DIRECTION.DOWN,  # pylint: disable=no-member
            pygame.K_LEFT: DIRECTION.LEFT,  # pylint: disable=no-member
            pygame.K_RIGHT: DIRECTION.RIGHT,  # pylint: disable=no-member
        }
        self.last_event = None

    def play(self, *args, **kwargs) -> bool:
        """Handle pygame key events for movement"""
        event = kwargs.get("event")
        if not event:
            return False

        # Only process key down events to prevent continuous movement
        if (
            event.type == pygame.KEYDOWN and event.key in self.moves
        ):  # pylint: disable=no-member
            move = MoveFactory.create(self.moves[event.key])
            return self.grid.move(move)

        return False
