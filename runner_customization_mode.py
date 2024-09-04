import random
import time
import math

import pygame
import pygame.gfxdraw

from constants import *
from game_objects import *
from maze_utils import *
from game_mode import GameMode


from enum import Enum, auto

class RunnerCustomizationMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.colors = [GOLD, RED, GREEN, BLUE, WHITE, CYAN, MAGENTA]
        self.color_index = 0

    def update(self):
        pass

    def render(self, screen, interpolation):
        # Draw gradient background
        for y in range(HEIGHT):
            color = self.lerp_color(THEME_BACKGROUND, THEME_PRIMARY, y / HEIGHT)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        title = self.title_font.render("Runner Customization", True, THEME_TEXT)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        screen.blit(title, title_rect)

        color_text = self.font.render("Press SPACE to change color", True, THEME_TEXT)
        color_rect = color_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(color_text, color_rect)

        # Draw example player
        pygame.draw.circle(screen, self.colors[self.color_index], (WIDTH // 2, HEIGHT // 2 + 50), CELL_SIZE // 2 - 1)

        back_text = self.font.render("Press ESC to return to menu", True, THEME_TEXT)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(back_text, back_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.color_index = (self.color_index + 1) % len(self.colors)
            elif event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")

    def get_player_color(self):
        return self.colors[self.color_index]
