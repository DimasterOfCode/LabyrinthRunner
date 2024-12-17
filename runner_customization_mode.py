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
        self.large_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Accessories and prices
        self.accessories = [
            {"name": "Top Hat", "price": 100, "unlocked": False},
            {"name": "Crown", "price": 150, "unlocked": False},
            {"name": "Cap", "price": 50, "unlocked": False}
        ]

        # Player score
        self.player_score = 200  # Example score

        # Animation
        self.animation_offset = 0

        # Face customization
        self.current_face = "happy"
        self.faces = {
            "happy": "☺",
            "sad": "☹"
        }
        
        # Hat customization
        self.hats = ["none", "top_hat", "crown"]
        self.current_hat = "none"
        
        # Color customization
        self.colors = [
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (255, 0, 0),      # Red
            (0, 255, 255),    # Cyan
            (255, 165, 0),    # Orange
            (255, 192, 203),  # Pink
            (128, 0, 128),    # Purple
            (0, 0, 255),      # Blue
            (255, 255, 255),  # White
            (0, 0, 0),        # Black
            (192, 192, 192)   # Silver
        ]
        self.color_index = 0
        
        # Trail color customization
        self.trail_colors = [
            (135, 206, 235),  # Light blue (default)
            (255, 192, 203),  # Pink
            (144, 238, 144),  # Light green
            (255, 215, 0),    # Gold
            (230, 230, 250),  # Lavender
            (255, 255, 255),  # White
            (255, 69, 0),     # Red-Orange
            (75, 0, 130),     # Indigo
            (255, 20, 147),   # Deep Pink
            (0, 128, 128),    # Teal
            (240, 230, 140)   # Khaki
        ]
        self.trail_color_index = 0
        
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
        
        # Trail color selection buttons
        self.prev_trail_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing//2, 
                                           HEIGHT//2 + (self.button_height + self.button_spacing) * 2, 
                                           self.button_width, self.button_height)
        self.next_trail_button = pygame.Rect(WIDTH//2 + self.button_spacing//2, 
                                           HEIGHT//2 + (self.button_height + self.button_spacing) * 2, 
                                           self.button_width, self.button_height)
        
        # Add hat selection buttons
        self.prev_hat_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing//2,
                                         HEIGHT//2 + (self.button_height + self.button_spacing) * 3,
                                         self.button_width, self.button_height)
        self.next_hat_button = pygame.Rect(WIDTH//2 + self.button_spacing//2,
                                         HEIGHT//2 + (self.button_height + self.button_spacing) * 3,
                                         self.button_width, self.button_height)
        self.hat_index = 0

    def update(self):
        pass

    def draw_hat(self, screen, pos, radius):
        # Reduce the offset even further to make hats sit much lower on the circle
        hat_y_offset = radius * 0.05  # Changed from 0.2 to 0.05
        
        if self.current_hat == "top_hat":
            # Draw top hat
            brim_width = radius * 1.8
            hat_height = radius * 1.2
            hat_width = radius * 1.2
            
            # Draw brim
            pygame.draw.ellipse(screen, BLACK,
                (pos[0] - brim_width//2,
                 pos[1] - radius - hat_y_offset,
                 brim_width, radius * 0.3))
            
            # Draw top part
            pygame.draw.rect(screen, BLACK,
                (pos[0] - hat_width//2,
                 pos[1] - radius - hat_y_offset - hat_height,
                 hat_width, hat_height))
                
        elif self.current_hat == "crown":
            # Draw crown with rounded points and curved base
            # Base curve points
            base_points = [
                (pos[0] - radius, pos[1] - radius + hat_y_offset),  # Bottom left
                (pos[0], pos[1] - radius + hat_y_offset + radius * 0.1),  # Bottom middle curve
                (pos[0] + radius, pos[1] - radius + hat_y_offset),  # Bottom right
            ]
            pygame.draw.lines(screen, GOLD, False, base_points, width=max(2, int(radius * 0.15)))
            
            # Draw the points with circles on top
            point_height = radius * 0.4
            points = [
                (int(pos[0] - radius * 0.8), point_height),  # First point
                (int(pos[0] - radius * 0.4), point_height),  # Second point
                (int(pos[0]), point_height),  # Middle point
                (int(pos[0] + radius * 0.4), point_height),  # Fourth point
                (int(pos[0] + radius * 0.8), point_height)  # Fifth point
            ]
            
            # Draw the triangular points
            for i, (px, h) in enumerate(points):
                point_points = [
                    (px, int(pos[1] - radius + hat_y_offset - h)),  # Top
                    (px - radius * 0.15, int(pos[1] - radius + hat_y_offset)),  # Bottom left
                    (px + radius * 0.15, int(pos[1] - radius + hat_y_offset))  # Bottom right
                ]
                pygame.draw.polygon(screen, GOLD, point_points)
                
                # Draw circles on top of points
                circle_radius = max(2, int(radius * 0.1))
                pygame.draw.circle(screen, GOLD, 
                                 (px, int(pos[1] - radius + hat_y_offset - h)), 
                                 circle_radius)
        
        elif self.current_hat == "cap":
            pygame.draw.ellipse(screen, self.colors[self.color_index],
                (pos[0] - radius * 1.2,
                 pos[1] - radius - hat_y_offset + radius * 0.3,
                 radius * 1.5, radius * 0.3))
            
            pygame.draw.arc(screen, self.colors[self.color_index],
                (pos[0] - radius,
                 pos[1] - radius - hat_y_offset - radius * 0.5,
                 radius * 2, radius * 1.2),
                math.pi, 2 * math.pi)

    def render(self, screen, interpolation):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Create a moving gradient background
        for y in range(screen_height):
            color = self.lerp_color((20, 20, 40), (50, 50, 80), (y + self.animation_offset * 50) % screen_height / screen_height)
            pygame.draw.line(screen, color, (0, y), (screen_width, y))

        screen.fill(THEME_BACKGROUND)
        
        # Draw title
        title = self.font.render("Customize Your Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Display player points in the top right corner
        points_text = self.small_font.render(f"{self.player_score} points", True, THEME_TEXT)
        points_rect = points_text.get_rect(topright=(screen_width - 20, 20))
        screen.blit(points_text, points_rect)
        
        # Draw current character preview (larger circle with face)
        preview_pos = (WIDTH//2, HEIGHT//2 - 100)
        preview_radius = 60
        
        # Draw trail particles BEFORE the character, now even higher
        particle_spacing = 20
        base_particle_size = 18
        particle_size = base_particle_size
        start_x = preview_pos[0] - 280
        particle_y = preview_pos[1] + 5
        
        # Draw 3 trail particles
        for i in range(3):
            particle_size = base_particle_size - (i * 2.0)
            opacity = 200 - (i * 50)
            
            particle_color = list(self.trail_colors[self.trail_color_index])
            particle_color.append(opacity)
            
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            
            # Draw the particle with a softer edge effect
            for radius in range(int(particle_size), 0, -1):
                current_opacity = int(opacity * (radius / particle_size) * 0.8)
                current_color = list(self.trail_colors[self.trail_color_index])
                current_color.append(current_opacity)
                pygame.draw.circle(particle_surface, current_color, 
                                 (particle_size, particle_size), radius)
            
            # Draw particles from right to left (newest to oldest)
            x_pos = start_x + ((2 - i) * (particle_spacing + particle_size))
            screen.blit(particle_surface, 
                       (x_pos, particle_y))
        
        # Draw the character
        pygame.draw.circle(screen, self.colors[self.color_index], preview_pos, preview_radius)
        
        # Draw the hat on the preview character
        self.draw_hat(screen, preview_pos, preview_radius)
        
        # Draw eyes and mouth for preview
        eye_radius = max(3, preview_radius // 5)
        eye_offset = preview_radius // 3
        pygame.draw.circle(screen, BLACK, (int(preview_pos[0] - eye_offset), int(preview_pos[1] - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(preview_pos[0] + eye_offset), int(preview_pos[1] - eye_offset)), eye_radius)
        
        if self.current_face == "happy":
            smile_rect = (int(preview_pos[0] - preview_radius//2), int(preview_pos[1]), preview_radius, preview_radius//2)
            pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, max(2, preview_radius//5))
        else:
            frown_rect = (int(preview_pos[0] - preview_radius//2), int(preview_pos[1] + preview_radius//4), preview_radius, preview_radius//2)
            pygame.draw.arc(screen, BLACK, frown_rect, 0, 3.14, max(2, preview_radius//5))

        # Draw face selection buttons first
        happy_button_y = preview_pos[1] + preview_radius + 30
        self.happy_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing//2,
                                      happy_button_y,
                                      self.button_width, self.button_height)
        self.sad_button = pygame.Rect(WIDTH//2 + self.button_spacing//2,
                                    happy_button_y,
                                    self.button_width, self.button_height)
        
        pygame.draw.rect(screen, THEME_PRIMARY, self.happy_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.sad_button)
        
        happy_text = self.font.render("Happy", True, THEME_TEXT)
        sad_text = self.font.render("Sad", True, THEME_TEXT)
        screen.blit(happy_text, happy_text.get_rect(center=self.happy_button.center))
        screen.blit(sad_text, sad_text.get_rect(center=self.sad_button.center))

        # Draw color selection buttons second
        color_button_y = happy_button_y + self.button_height + self.button_spacing
        self.prev_color_button = pygame.Rect(WIDTH//2 - self.button_width - self.button_spacing,
                                           color_button_y,
                                           self.button_width, self.button_height)
        self.next_color_button = pygame.Rect(WIDTH//2 + self.button_spacing,
                                           color_button_y,
                                           self.button_width, self.button_height)
        
        pygame.draw.rect(screen, THEME_PRIMARY, self.prev_color_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.next_color_button)
        
        prev_text = self.font.render("< Color", True, THEME_TEXT)
        next_text = self.font.render("Color >", True, THEME_TEXT)
        screen.blit(prev_text, prev_text.get_rect(center=self.prev_color_button.center))
        screen.blit(next_text, next_text.get_rect(center=self.next_color_button.center))
        
        # Draw current color name
        color_text = self.font.render("Current Color", True, self.colors[self.color_index])
        color_rect = color_text.get_rect(midtop=(WIDTH//2, color_button_y + self.button_height + 10))
        screen.blit(color_text, color_rect)

        # Update trail color selection buttons to be aligned with particles
        particles_center_x = start_x + ((particle_spacing + base_particle_size) * 1.5)
        trail_button_y = preview_pos[1] + 90
        
        self.prev_trail_button = pygame.Rect(particles_center_x - self.button_width - self.button_spacing,
                                           trail_button_y,
                                           self.button_width, self.button_height)
        self.next_trail_button = pygame.Rect(particles_center_x + self.button_spacing,
                                           trail_button_y,
                                           self.button_width, self.button_height)
        
        pygame.draw.rect(screen, THEME_PRIMARY, self.prev_trail_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.next_trail_button)
        
        prev_trail_text = self.font.render("< Trail", True, THEME_TEXT)
        next_trail_text = self.font.render("Trail >", True, THEME_TEXT)
        screen.blit(prev_trail_text, prev_trail_text.get_rect(center=self.prev_trail_button.center))
        screen.blit(next_trail_text, next_trail_text.get_rect(center=self.next_trail_button.center))
        
        # Draw trail color name below the particles
        trail_color_text = self.font.render("Trail Color", True, self.trail_colors[self.trail_color_index])
        trail_color_rect = trail_color_text.get_rect(midtop=(particles_center_x, trail_button_y + self.button_height + 10))
        screen.blit(trail_color_text, trail_color_rect)

        # Draw hat selection buttons
        pygame.draw.rect(screen, THEME_PRIMARY, self.prev_hat_button)
        pygame.draw.rect(screen, THEME_PRIMARY, self.next_hat_button)
        
        prev_hat_text = self.font.render("< Hat", True, THEME_TEXT)
        next_hat_text = self.font.render("Hat >", True, THEME_TEXT)
        screen.blit(prev_hat_text, prev_hat_text.get_rect(center=self.prev_hat_button.center))
        screen.blit(next_hat_text, next_hat_text.get_rect(center=self.next_hat_button.center))
        
        # Draw current hat name
        hat_text = self.font.render(f"Hat: {self.current_hat.replace('_', ' ').title()}", True, THEME_TEXT)
        hat_rect = hat_text.get_rect(midtop=(WIDTH//2, self.prev_hat_button.bottom + 10))
        screen.blit(hat_text, hat_rect)

        # Draw accessories shop
        self.draw_accessories_shop(screen, preview_pos)

        # Draw back button
        back_text = self.font.render("Back to Menu", True, THEME_TEXT)
        back_rect = back_text.get_rect(midbottom=(WIDTH//2, HEIGHT - 20))
        screen.blit(back_text, back_rect)

    def draw_accessories_shop(self, screen, preview_pos):
        x_offset = 120
        y_offset = 50
        self.accessory_rects = []  # Store rects for click detection
        for accessory in self.accessories:
            accessory_text = f"{accessory['name']} - {accessory['price']} pts"
            text_surface = self.large_font.render(accessory_text, True, THEME_TEXT)
            text_rect = text_surface.get_rect(midleft=(preview_pos[0] + x_offset, preview_pos[1] + y_offset))
            screen.blit(text_surface, text_rect)

            # Create button
            button_text = "Unlock" if not accessory["unlocked"] else "Unlocked"
            button_surface = self.small_font.render(button_text, True, THEME_TEXT)
            button_rect = button_surface.get_rect(midleft=(text_rect.right + 10, text_rect.centery))
            screen.blit(button_surface, button_rect)

            self.accessory_rects.append((button_rect, accessory))  # Store rect and accessory
            y_offset += 50

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            self.check_accessory_purchase(mouse_pos)
            
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
            
            # Trail color selection
            elif self.prev_trail_button.collidepoint(mouse_pos):
                self.trail_color_index = (self.trail_color_index - 1) % len(self.trail_colors)
            elif self.next_trail_button.collidepoint(mouse_pos):
                self.trail_color_index = (self.trail_color_index + 1) % len(self.trail_colors)
            
            # Hat selection
            elif self.prev_hat_button.collidepoint(mouse_pos):
                self.hat_index = (self.hat_index - 1) % len(self.hats)
                self.current_hat = self.hats[self.hat_index]
            elif self.next_hat_button.collidepoint(mouse_pos):
                self.hat_index = (self.hat_index + 1) % len(self.hats)
                self.current_hat = self.hats[self.hat_index]
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")

    def get_player_color(self):
        return self.colors[self.color_index]

    def get_player_face(self):
        return self.faces[self.current_face]

    def get_trail_color(self):
        return self.trail_colors[self.trail_color_index]

    def get_player_hat(self):
        return self.current_hat

    def check_accessory_purchase(self, mouse_pos):
        for button_rect, accessory in self.accessory_rects:
            if button_rect.collidepoint(mouse_pos):
                if not accessory["unlocked"] and self.player_score >= accessory['price']:
                    self.player_score -= accessory['price']
                    accessory["unlocked"] = True
                    print(f"Unlocked {accessory['name']}")
                elif accessory["unlocked"]:
                    print(f"{accessory['name']} is already unlocked")
                else:
                    print("Not enough points")

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
