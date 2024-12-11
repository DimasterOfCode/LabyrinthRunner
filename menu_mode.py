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
        
        # Draw enemy circle on the left
        enemy_center = (WIDTH//2 - 250, button_start_y + 60)
        enemy_radius = 80
        
        # Draw main enemy circle (in red)
        pygame.draw.circle(screen, (255, 0, 0), enemy_center, enemy_radius, 4)
        
        # Draw evil eyes (shifted right to look at scared circle)
        eye_radius = 10
        eye_offset = 25
        eye_forward_shift = 10  # Shift eyes right to look at scared circle
        pygame.draw.circle(screen, (255, 0, 0), 
                          (enemy_center[0] - eye_offset + eye_forward_shift, enemy_center[1] - 15), 
                          eye_radius)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (enemy_center[0] + eye_offset + eye_forward_shift, enemy_center[1] - 15), 
                          eye_radius)
        
        # Draw evil eyebrows (angled to look menacing)
        eyebrow_length = 20
        eyebrow_angle = -math.pi / 6
        
        # Left and right eyebrows (shifted right)
        for x_mult in [-1, 1]:
            brow_start = (enemy_center[0] + x_mult * eye_offset + eye_forward_shift - x_mult * eyebrow_length * math.cos(eyebrow_angle),
                         enemy_center[1] - 30 - eyebrow_length * math.sin(eyebrow_angle))
            brow_end = (enemy_center[0] + x_mult * eye_offset + eye_forward_shift + x_mult * eyebrow_length * math.cos(eyebrow_angle),
                       enemy_center[1] - 30 + eyebrow_length * math.sin(eyebrow_angle))
            pygame.draw.line(screen, (255, 0, 0), brow_start, brow_end, 4)
        
        # Draw evil smile (shifted right)
        smile_rect = pygame.Rect(enemy_center[0] - 35 + eye_forward_shift, enemy_center[1] - 30, 70, 50)
        pygame.draw.arc(screen, (255, 0, 0), smile_rect, math.pi, 2 * math.pi, 4)
        
        # Draw scared circle on the right
        circle_center = (WIDTH//2 + 250, button_start_y + 60)
        circle_radius = 80
        pygame.draw.circle(screen, THEME_SECONDARY, circle_center, circle_radius, 4)
        
        # Draw scared eyes (shifted left to look at enemy)
        scared_eye_radius = 12
        eye_backward_shift = 10  # Shift eyes left to look at enemy
        pygame.draw.circle(screen, THEME_SECONDARY, 
                          (circle_center[0] - eye_offset - eye_backward_shift, circle_center[1] - 15), 
                          scared_eye_radius)
        pygame.draw.circle(screen, THEME_SECONDARY, 
                          (circle_center[0] + eye_offset - eye_backward_shift, circle_center[1] - 15), 
                          scared_eye_radius)
        
        # Draw scared mouth (shifted left)
        scared_mouth_radius = 10
        pygame.draw.circle(screen, THEME_SECONDARY,
                          (circle_center[0] - eye_backward_shift, circle_center[1] + 15),
                          scared_mouth_radius)
        
        # Draw buttons
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
