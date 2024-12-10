print("Running updated version of runner_customization_mode.py")
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
        
        # Face customization
        self.current_face = "happy"
        self.faces = {
            "happy": "☺",
            "sad": "☹"
        }
        
        # Color customization
        self.colors = [
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (255, 0, 0),      # Red
            (0, 255, 255),    # Cyan
            (255, 165, 0),    # Orange
            (255, 192, 203)   # Pink
        ]
        self.color_index = 0
        
        # Button dimensions
        self.button_width = 80
        self.button_height = 40
        self.button_spacing = 20
        
        # Face selection buttons
        self.happy_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing//2, 
                                      HEIGHT//2, self.button_width, self.button_height)
        self.sad_button = pygame.Rect(WIDTH//2 + self.button_spacing//2, 
                                    HEIGHT//2, self.button_width, self.button_height)
        
        # Color selection buttons
        self.prev_color_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing//2, 
                                           HEIGHT//2 + self.button_height + self.button_spacing, 
                                           self.button_width, self.button_height)
        self.next_color_button = pygame.Rect(WIDTH//2 + self.button_spacing//2, 
                                           HEIGHT//2 + self.button_height + self.button_spacing, 
                                           self.button_width, self.button_height)

    def update(self):
        pass

    def render(self, screen, interpolation):
        screen.fill(THEME_BACKGROUND)
        
        # Draw title
        title = self.font.render("Customize Your Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Draw current character preview (larger circle with face)
        preview_radius = 60  # Increased from 40 to 60
        preview_pos = (WIDTH//2, HEIGHT//2 - 100)  # Moved up a bit more to accommodate larger size
        pygame.draw.circle(screen, self.colors[self.color_index], preview_pos, preview_radius)
        
        # Draw eyes for preview (scaled up)
        eye_radius = max(3, preview_radius // 5)  # Slightly larger eyes
        eye_offset = preview_radius // 3
        pygame.draw.circle(screen, BLACK, (int(preview_pos[0] - eye_offset), int(preview_pos[1] - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(preview_pos[0] + eye_offset), int(preview_pos[1] - eye_offset)), eye_radius)
        
        # Draw mouth based on current_face (scaled up)
        if self.current_face == "happy":
            smile_rect = (int(preview_pos[0] - preview_radius//2), int(preview_pos[1]), preview_radius, preview_radius//2)
            pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, max(2, preview_radius//5))  # Thicker line
        else:
            frown_rect = (int(preview_pos[0] - preview_radius//2), int(preview_pos[1] + preview_radius//4), preview_radius, preview_radius//2)
            pygame.draw.arc(screen, BLACK, frown_rect, 0, 3.14, max(2, preview_radius//5))  # Thicker line
        
        # Draw face selection buttons
        pygame.draw.rect(screen, THEME_PRIMARY, self.happy_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.sad_button)
        
        happy_text = self.font.render("Happy", True, THEME_TEXT)
        sad_text = self.font.render("Sad", True, THEME_TEXT)
        screen.blit(happy_text, happy_text.get_rect(center=self.happy_button.center))
        screen.blit(sad_text, sad_text.get_rect(center=self.sad_button.center))
        
        # Draw color selection buttons
        pygame.draw.rect(screen, THEME_PRIMARY, self.prev_color_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.next_color_button)
        
        prev_text = self.font.render("< Color", True, THEME_TEXT)
        next_text = self.font.render("Color >", True, THEME_TEXT)
        screen.blit(prev_text, prev_text.get_rect(center=self.prev_color_button.center))
        screen.blit(next_text, next_text.get_rect(center=self.next_color_button.center))
        
        # Draw current color name
        color_text = self.font.render(f"Current Color", True, self.colors[self.color_index])
        color_rect = color_text.get_rect(midtop=(WIDTH//2, HEIGHT//2 + self.button_height*2 + self.button_spacing*2))
        screen.blit(color_text, color_rect)
        
        # Draw back button
        back_text = self.font.render("Back to Menu", True, THEME_TEXT)
        back_rect = back_text.get_rect(midbottom=(WIDTH//2, HEIGHT - 20))
        screen.blit(back_text, back_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Face selection
            if self.happy_button.collidepoint(mouse_pos):
                print("Happy face selected")  # Debug print
                self.current_face = "happy"
            elif self.sad_button.collidepoint(mouse_pos):
                print("Sad face selected")  # Debug print
                self.current_face = "sad"
            
            # Color selection
            elif self.prev_color_button.collidepoint(mouse_pos):
                self.color_index = (self.color_index - 1) % len(self.colors)
            elif self.next_color_button.collidepoint(mouse_pos):
                self.color_index = (self.color_index + 1) % len(self.colors)
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")

    def get_player_color(self):
        return self.colors[self.color_index]

    def get_player_face(self):
        return self.faces[self.current_face]
