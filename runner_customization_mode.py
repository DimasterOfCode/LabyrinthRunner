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
        preview_radius = 40  # Larger radius for better visibility
        preview_pos = (WIDTH//2, HEIGHT//2 - 80)  # Moved up a bit
        pygame.draw.circle(screen, self.colors[self.color_index], preview_pos, preview_radius)
        
        # Draw current face larger (using a larger font for the face)
        face_font = pygame.font.Font(None, 80)  # Larger font for the face
        face = face_font.render(self.faces[self.current_face], True, BLACK)  # Changed color to BLACK for better visibility
        face_rect = face.get_rect(center=preview_pos)
        screen.blit(face, face_rect)
        
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
                self.current_face = "happy"
            elif self.sad_button.collidepoint(mouse_pos):
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
