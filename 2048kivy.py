#!/usr/bin/env python3
import os

# os.environ["KIVY_NO_CONSOLELOG"] = "1"
os.environ["KIVY_NO_ARGS"] = "1"
import argparse

import kivy

from players.cycle_player import CyclePlayer
from players.expectimax_player import ExpectimaxPlayer
from players.mcts_player import MCTSPlayer
from players.minimax_player import MinimaxPlayer
from players.player import PlayerFactory
from players.random_player import RandomPlayer
from players.user_player import KivyPlayer

kivy.require("2.1.0")

from kivy.config import Config

Config.set("graphics", "resizable", "0")


import itertools

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from grid2048.grid2048 import STATE, Grid2048

player_factory = PlayerFactory()
player_factory.register("user", KivyPlayer)
player_factory.register("random", RandomPlayer)
player_factory.register("cycle", CyclePlayer)
player_factory.register("mcts", MCTSPlayer)
player_factory.register("expectimax", ExpectimaxPlayer)
player_factory.register("minimax", MinimaxPlayer)


COLORS = {
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
TXT_LOW_COLOR = (0.471, 0.431, 0.400, 1.0)
TXT_HI_COLOR = (0.929, 0.898, 0.867, 1.0)


class Grid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = width
        self.rows = height
        self.spacing = 10, 10
        self.padding = 10, 10, 10, 10
        self.game_board = Grid2048(self.cols, self.rows)
        self.player = player_factory.create(player, self.game_board)
        # self.game_board.data = [
        #     [0, 2, 4, 8],
        #     [16, 32, 64, 128],
        #     [256, 512, 1024, 2048],
        #     [4096, 8192, 16384, 32768],
        # ]
        self.create_widgets()

    def create_widgets(self):
        for _ in range(self.cols * self.rows):
            tile = Button(
                text="",
                disabled=True,
                font_size=32,
                bold=True,
                size_hint=(0.25, 0.25),
                size=(80, 80),
                disabled_color=(0.471, 0.431, 0.400, 1.0),  # text color
                background_color=(0.808, 0.757, 0.710, 1.0),  # tile color
                background_disabled_normal="",
            )
            self.add_widget(tile)
        self.update_widgets()

    def update_widgets(self):
        for col, row in itertools.product(range(self.cols), range(self.rows)):
            tile = self.children[row * self.cols + col]
            tile.text = (
                str(self.game_board[row][col]) if self.game_board[row][col] > 0 else ""
            )
            tile.background_color = COLORS[str(self.game_board[row][col])]
            tile.color = (
                TXT_LOW_COLOR if self.game_board[row][col] < 8 else TXT_HI_COLOR
            )
        self.children.reverse()
        if self.parent:
            self.parent.update_score(self.game_board.score)
            if self.game_board.no_moves:
                self.parent.game_over()
        # print(self.game_board)

    def play(self, **kwargs):
        if self.game_board.state == STATE.RUNNING or self.game_board.no_moves:
            return
        moved = self.player.play(**kwargs)
        # if not moved and not self.game_board.no_moves and player != "user":
        #     self.play(**kwargs)
        if moved:
            self.update_widgets()


class Game2048(BoxLayout):
    paused = False
    step = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        title_layout = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.2),
        )

        self.title_btn = Button(
            disabled=True,
            text="2048",
            font_size=40,
            bold=True,
            size_hint=(0.7, 1),
            color=(0.937, 0.894, 0.859, 1.0),
            disabled_color=(0.361, 0.306, 0.282, 1.0),
            background_color=(0.741, 0.678, 0.631, 1.0),
            background_disabled_normal="",
        )
        self.title_btn.bind(on_press=self.reset)
        title_layout.add_widget(self.title_btn)

        self.score_label = Label(
            text="Score: 0",
            font_size=20,
            bold=True,
            color=(1.0, 1.0, 1.0, 1.0),
        )
        title_layout.add_widget(self.score_label)

        self.add_widget(title_layout)
        self.grid = kwargs.get("grid", Grid())
        self.add_widget(self.grid)

    def update_score(self, score):
        self.score_label.text = f"Score: {score}"

    def reset(self, *args):
        self.grid.game_board.reset()
        self.grid.update_widgets()
        self.title_btn.text = "2048"
        self.title_btn.disabled = True
        self.paused = False

    def game_over(self):
        self.title_btn.text = "Reset"
        self.title_btn.disabled = False

    def play(self, *args, **kwargs):
        if not self.paused:
            self.grid.play(**kwargs)
        elif self.step:
            self.grid.play(**kwargs)
            self.step = False


class Game2048App(App):
    def build(self):
        global width, height, player
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-c", "--cols", "--width", type=int, help="width of the grid"
        )
        parser.add_argument(
            "-r", "--rows", "--height", type=int, help="height of the grid"
        )
        parser.add_argument("-i", "--interval", type=int, help="interval between moves")
        parser.add_argument("-p", "--player", type=str, help="player type")
        args = parser.parse_args()
        interval = args.interval or 10
        width = args.cols or 4
        height = args.rows or 4
        player = args.player or "user"
        if player not in player_factory.container.keys():
            raise ValueError(f"Invalid player type: {player!r}")
        print(f"Starting game with {width}x{height} grid and {player!r} player")
        Window.size = width * 100, height * 100 + 80
        Window.clearcolor = (0.741, 0.678, 0.631, 1.0)
        Window.bind(on_key_down=self.key_pressed)
        # Create game
        self.game = Game2048()
        self.title = f"2048 - {width}x{height} {player!r}"
        if player != "user":
            Clock.schedule_interval(self.game.play, interval / 60.0)
        return self.game

    def key_pressed(self, window, key, scancode, codepoint, modifier):
        if key in [32]:  # space
            self.game.paused = not self.game.paused
        if key in [13]:  # enter
            self.game.step = not self.game.step
        if player == "user" and key in [273, 274, 275, 276]:  # up, down, right, left
            self.game.play(**{"dir": key})


if __name__ == "__main__":
    app = Game2048App()
    app.run()
