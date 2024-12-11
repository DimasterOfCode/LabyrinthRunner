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
        screen.fill(THEME_BACKGROUND)
        
        # Draw title
        title = self.font.render("Labyrinth Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Draw buttons in the center
        button_start_y = HEIGHT//2 - 100
        
        # Draw decorative circle with smiley face to the right
        circle_center = (WIDTH//2 + 250, button_start_y + 60)  # Changed from +200 to +250 pixels to the right
        circle_radius = 80  # Large circle for visibility
        
        # Draw main circle
        pygame.draw.circle(screen, THEME_SECONDARY, circle_center, circle_radius, 4)  # Outlined circle
        
        # Draw eyes
        eye_radius = 10
        eye_offset = 25
        pygame.draw.circle(screen, THEME_SECONDARY, 
                          (circle_center[0] - eye_offset, circle_center[1] - 15), 
                          eye_radius)
        pygame.draw.circle(screen, THEME_SECONDARY, 
                          (circle_center[0] + eye_offset, circle_center[1] - 15), 
                          eye_radius)
        
        # Draw smile
        smile_rect = pygame.Rect(circle_center[0] - 35, circle_center[1] - 20, 70, 50)
        pygame.draw.arc(screen, THEME_SECONDARY, smile_rect, 0, math.pi, 4)
        
        # Draw buttons in center (unchanged)
        for i, button in enumerate(self.buttons):
            text = self.small_font.render(button["text"], True, THEME_TEXT)
            button_rect = text.get_rect(center=(WIDTH//2, button_start_y + i * 60))
            
            if i == self.selected_button:
                pygame.draw.rect(screen, THEME_SECONDARY, button_rect.inflate(20, 10), border_radius=5)
            
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
