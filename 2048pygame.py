#!/usr/bin/env python
"""2048 game using PyGame"""
import argparse
import sys

import pygame

from grid2048 import Grid2048
from players import player, player_factory
from players.user_player import PygamePlayer

player_factory.register("user", PygamePlayer)
# Constants
WINDOW_SIZE = 400
PADDING = 10


# Colors (similar to the image)
COLORS = {
    0: (205, 193, 180),  # Empty tile
    2: (238, 228, 218),  # 2
    4: (237, 224, 200),  # 4
    8: (242, 177, 121),  # 8
    16: (245, 149, 99),  # 16
    32: (246, 124, 95),  # 32
    64: (246, 94, 59),  # 64
    128: (237, 207, 114),  # 128
    256: (237, 204, 97),  # 256
    512: (237, 200, 80),  # 512
    1024: (237, 197, 63),  # 1024
    2048: (237, 194, 46),  # 2048
}

BACKGROUND_COLOR = (187, 173, 160)
TEXT_LIGHT = (249, 246, 242)  # For dark tiles
TEXT_DARK = (119, 110, 101)  # For light tiles


class Game2048:
    """2048 game class with PyGame interface"""

    def __init__(self, width: int, height: int, player_type: str, fps: int  ):
        pygame.init()
        self.width = width
        self.height = height
        self.player_type = player_type
        self.fps = fps
        self.init_game()

        # Calculate cell size based on window size and grid dimensions
        self.cell_size = (WINDOW_SIZE - (width + 1) * PADDING) // width
        window_width = width * self.cell_size + (width + 1) * PADDING
        window_height = (
            height * self.cell_size + (height + 1) * PADDING + 50
        )  # Extra height for score

        self.window = pygame.display.set_mode((window_width, window_height))
        self.font = pygame.font.SysFont("Arial", 36, True)
        self.score_font = pygame.font.SysFont("Arial", 24, True)
        self.clock = pygame.time.Clock()
        self.update_title()
        self.game_over = False
        self.paused = False

    def update_title(self):
        pygame.display.set_caption(
            f"2048PyGame: {self.player_type} player ({self.width}x{self.height}) {self.clock.get_fps():.2f} FPS" if self.player_type else "2048PyGame"
        )

    def init_game(self):
        """Initialize or reset the game state"""
        self.grid = Grid2048(self.width, self.height)
        if self.player_type:
            self.player = player_factory.create(self.player_type, self.grid)
        else:
            self.player = PygamePlayer(self.grid)
        self.game_over = False
        self.paused = False

    def draw_tile(self, value, x, y):
        """Draw a single tile with its value"""
        color = COLORS.get(value, COLORS[0])
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.rect(self.window, color, rect, border_radius=4)

        if value != 0:
            text_color = TEXT_LIGHT if value > 4 else TEXT_DARK
            text = self.font.render(str(value), True, text_color)
            text_rect = text.get_rect(
                center=(x + self.cell_size / 2, y + self.cell_size / 2)
            )
            self.window.blit(text, text_rect)

    def draw_overlay_text(self, main_text, sub_text=None):
        """Draw overlay with text messages"""
        s = pygame.Surface((self.window.get_width(), self.window.get_height()))
        s.set_alpha(128)
        s.fill((255, 255, 255))
        self.window.blit(s, (0, 0))

        main_text_surface = self.font.render(main_text, True, TEXT_DARK)
        main_rect = main_text_surface.get_rect(
            center=(self.window.get_width() / 2, self.window.get_height() / 2 - 20)
        )
        self.window.blit(main_text_surface, main_rect)

        if sub_text:
            sub_text_surface = self.score_font.render(sub_text, True, TEXT_DARK)
            sub_rect = sub_text_surface.get_rect(
                center=(self.window.get_width() / 2, self.window.get_height() / 2 + 20)
            )
            self.window.blit(sub_text_surface, sub_rect)

    def draw(self):
        """Draw the game state"""
        self.window.fill(BACKGROUND_COLOR)

        # Draw score
        score_text = self.score_font.render(
            f"Score: {self.grid.score}", True, TEXT_DARK
        )
        self.window.blit(score_text, (PADDING, PADDING))

        # Draw grid
        start_y = 50  # Start grid below score
        for i in range(self.grid.height):
            for j in range(self.grid.width):
                x = j * self.cell_size + (j + 1) * PADDING
                y = i * self.cell_size + (i + 1) * PADDING + start_y
                self.draw_tile(self.grid[i, j], x, y)

        # Draw overlays
        if self.game_over:
            self.draw_overlay_text("GAME OVER", "Press R to restart")
        elif self.paused and isinstance(self.player, PygamePlayer):
            self.draw_overlay_text("PAUSED", "Space to resume, ESC to quit")

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.draw()
            self.update_title()
            for event in pygame.event.get():
                # self.draw()
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.init_game()
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        break
               
                
                self.draw()
                
            if not self.game_over and not self.paused:
                # Allow AI players to play without an event
                if self.player_type != 'user':
                    self.player.play()
                else: 
                    self.player.play(event=event)

                # Check for game over
                if self.grid.no_moves:
                    self.game_over = True
                    

            self.clock.tick(self.fps)

        pygame.quit()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="2048 game with PyGame")
    parser.add_argument(
        "-c", "--cols", "--width", type=int, default=4, help="width of the grid"
    )
    parser.add_argument(
        "-r", "--rows", "--height", type=int, default=4, help="height of the grid"
    )
    parser.add_argument(
        "-p",
        "--player",
        type=str,
        help="player type (e.g., random, cycle, minimax, expectimax, mcs, mcst)",
    )
    parser.add_argument(
        "-fps",
        "-i",
        type=int,
        help="interval - max frames per second (default: 10, set 0 for unlimited)",
        default=10,
    )
    args = parser.parse_args()
    if args.player and args.player not in player_factory.container:
        print(f"Invalid player type: {args.player!r}")
        sys.exit(1)

    player = args.player or "user"
    game = Game2048(args.cols, args.rows, player, args.fps)
    game.run()


if __name__ == "__main__":
    main()
