
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

class MenuMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.title = "Labyrinth Runner"  # Update the title here
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.buttons = [
            {"text": "Play", "action": lambda: self.game.set_mode("play")},
            {"text": "Level Editor", "action": lambda: self.game.set_mode("level_editor")},
            {"text": "Customize Runner", "action": lambda: self.game.set_mode("runner_customization")},
            {"text": "Quit", "action": lambda: setattr(self.game, 'running', False)}
        ]
        self.selected_button = 0
        self.animation_offset = 0
        self.animation_speed = 0.5

    def update(self):
        self.animation_offset = (self.animation_offset + self.animation_speed) % (2 * math.pi)

    def render(self, screen, interpolation):
        # Create gradient background
        for y in range(HEIGHT):
            color = self.lerp_color((20, 20, 50), (50, 50, 100), y / HEIGHT)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Draw animated circles
        for i in range(10):
            radius = 50 + 20 * math.sin(self.animation_offset + i * 0.5)
            x = WIDTH * (i + 1) / 11
            y = HEIGHT * (0.2 + 0.1 * math.sin(self.animation_offset + i * 0.7))
            pygame.gfxdraw.aacircle(screen, int(x), int(y), int(radius), (255, 255, 255, 50))

        # Draw title
        title = self.font.render(self.title, True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)

        # Draw buttons
        for i, button in enumerate(self.buttons):
            text = self.small_font.render(button["text"], True, (255, 255, 255))
            button_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            
            if i == self.selected_button:
                # Draw highlighted button
                pygame.draw.rect(screen, (100, 100, 255), button_rect.inflate(20, 10), border_radius=5)
            
            screen.blit(text, button_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                self.buttons[self.selected_button]["action"]()

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
