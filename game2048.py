#!/usr/bin/env python3
import os
from typing import Dict, Tuple

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.event import EventDispatcher

# Import properties after other kivy imports
from kivy.properties import (
    NumericProperty,
    ListProperty,
    BoundedNumericProperty,
    ObjectProperty,
)

from grid2048 import Grid2048, DIRECTION, STATE, MoveFactory

COLORS: Dict[str, Tuple[float, float, float, float]] = {
    "0": (0.808, 0.757, 0.710, 1.0),
    "2": (0.937, 0.894, 0.859, 1.0),
    "4": (0.937, 0.878, 0.788, 1.0),
    "8": (0.973, 0.694, 0.494, 1.0),
    "16": (0.992, 0.588, 0.408, 1.0),
    "32": (1.000, 0.490, 0.388, 1.0),
    "64": (1.000, 0.376, 0.255, 1.0),
    "128": (0.945, 0.808, 0.475, 1.0),
    "256": (0.945, 0.800, 0.420, 1.0),
    "512": (0.945, 0.784, 0.365, 1.0),
    "1024": (0.957, 0.765, 0.310, 1.0),
    "2048": (0.949, 0.769, 0.255, 1.0),
    "4096": (0.180, 0.196, 0.169, 1.0),
    "8192": (0.180, 0.196, 0.169, 1.0),
    "16384": (0.180, 0.196, 0.169, 1.0),
    "32768": (0.180, 0.196, 0.169, 1.0),
    "65536": (0.170, 0.200, 0.150, 1.0),
}


class Tile(Button):
    value = BoundedNumericProperty(0, min=0)
    background_color = ListProperty(COLORS["0"])
    slide_x = NumericProperty(0)
    slide_y = NumericProperty(0)

    def on_value(self, instance, value):
        self.background_color = COLORS[str(int(value))]


class ScoreBox(BoxLayout):
    score = ObjectProperty(0)

    def on_score(self, instance, value):
        self.score = int(value)


class GameGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 4
        self.rows = 4
        self.tiles = {}
        self.game = Grid2048(4, 4)
        self.tile_size = None
        Clock.schedule_once(self._init_grid, 0)

    def _init_grid(self, dt):
        self.create_tiles()
        self.update_tiles()
        self.fbind("size", self._update_tiles_size)
        self.fbind("pos", self._update_tiles_pos)

    def create_tiles(self):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = Tile(value=0)
                self.tiles[(row, col)] = tile
                self.add_widget(tile)

    def _update_tiles_size(self, instance, value):
        if not self.tiles:
            return
        padding = dp(10)
        spacing = dp(10)
        available_width = self.width - 2 * padding - (self.cols - 1) * spacing
        available_height = self.height - 2 * padding - (self.rows - 1) * spacing
        tile_size = min(available_width / self.cols, available_height / self.rows)
        self.tile_size = tile_size

        for tile in self.tiles.values():
            tile.size = (tile_size, tile_size)
        self._update_tiles_pos(None, None)

    def _update_tiles_pos(self, instance, value):
        if not self.tile_size:
            return
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[(row, col)]
                tile.pos = self.calculate_pos(row, col)

    def calculate_pos(self, row, col):
        if not self.tile_size:
            return (0, 0)
        padding = dp(10)
        spacing = dp(10)
        x = self.x + padding + col * (self.tile_size + spacing)
        y = self.y + padding + (self.rows - 1 - row) * (self.tile_size + spacing)
        return (x, y)

    def update_tiles(self, dt=None, animate=False):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[(row, col)]
                new_value = int(self.game[row][col])

                if animate:
                    target_pos = self.calculate_pos(row, col)
                    current_pos = tile.pos
                    anim = Animation(
                        slide_x=target_pos[0] - current_pos[0],
                        slide_y=target_pos[1] - current_pos[1],
                        duration=0.15,
                        transition="in_out_quad",
                    )

                    def update_value(anim, tile, value):
                        tile.value = value
                        tile.slide_x = 0
                        tile.slide_y = 0

                    anim.bind(on_complete=lambda a, t: update_value(a, tile, new_value))
                    anim.start(tile)
                else:
                    tile.value = new_value
                    tile.slide_x = 0
                    tile.slide_y = 0

    def make_move(self, direction):
        if self.game.state == STATE.RUNNING:
            return False

        if direction == "left":
            dir_enum = DIRECTION.LEFT
        elif direction == "right":
            dir_enum = DIRECTION.RIGHT
        elif direction == "up":
            dir_enum = DIRECTION.UP
        elif direction == "down":
            dir_enum = DIRECTION.DOWN
        else:
            return False

        move = MoveFactory.create(dir_enum)
        moved = self.game.move(move)

        if moved:
            self.update_tiles(animate=True)
            if self.parent:
                score = int(self.game.score)
                self.parent.ids.score_box.score = score
                if self.game.no_moves:
                    self.parent.game_over()

        return moved


class Game2048(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self._on_keyboard)

    def reset_game(self):
        self.ids.game_grid.game.reset()
        self.ids.game_grid.update_tiles()
        self.ids.score_box.score = 0

    def _on_keyboard(self, window, key, *args):
        if key == 273:  # Up arrow
            self.ids.game_grid.make_move("up")
            return True
        elif key == 274:  # Down arrow
            self.ids.game_grid.make_move("down")
            return True
        elif key == 276:  # Left arrow
            self.ids.game_grid.make_move("left")
            return True
        elif key == 275:  # Right arrow
            self.ids.game_grid.make_move("right")
            return True
        return False

    def game_over(self):
        # TODO: Add game over animation/display
        pass


class Game2048App(App):
    def build(self):
        Window.clearcolor = (0.741, 0.678, 0.631, 1.0)
        Window.size = (dp(400), dp(500))
        return Game2048()


if __name__ == "__main__":
    Game2048App().run()
