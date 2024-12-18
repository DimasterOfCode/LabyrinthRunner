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
        self.game = game
        self.setup_initial_state()
        self.update_layout(game.screen.get_width(), game.screen.get_height())

    def setup_initial_state(self):
        """Initialize non-layout related state"""
        # Accessories and prices
        self.accessories = [
            {"name": "Top Hat", "price": 100, "unlocked": False},
            {"name": "Crown", "price": 150, "unlocked": False},
            {"name": "Cap", "price": 50, "unlocked": False}
        ]

        # Player score
        self.player_score = 10000

        # Animation
        self.animation_offset = 0

        # Face customization
        self.current_face = "happy"
        self.faces = {"happy": "☺", "sad": "☹"}
        
        # Hat customization
        self.hats = ["none", "top_hat", "crown"]
        self.current_hat = "none"
        self.hat_index = 0
        
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

    def update_layout(self, screen_width, screen_height):
        """Update all UI elements based on screen dimensions"""
        # Calculate base scale factor based on screen dimensions
        self.scale = min(screen_width / 1280, screen_height / 720)  # Base resolution
        
        # Update fonts
        self.font = pygame.font.Font(None, int(36 * self.scale))
        self.large_font = pygame.font.Font(None, int(48 * self.scale))
        self.small_font = pygame.font.Font(None, int(24 * self.scale))
        
        # Calculate relative dimensions
        self.button_width = int(120 * self.scale)
        self.button_height = int(40 * self.scale)
        self.button_spacing = int(20 * self.scale)
        
        # Calculate preview character dimensions
        self.preview_radius = int(60 * self.scale)
        self.preview_pos = (screen_width * 0.35, screen_height * 0.35)
        
        # Calculate vertical spacing
        section_spacing = screen_height * 0.08
        
        # Update button positions relative to preview character
        button_y = self.preview_pos[1] + self.preview_radius + section_spacing
        
        # Face selection buttons
        self.happy_button = pygame.Rect(
            self.preview_pos[0] - self.button_width - self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        self.sad_button = pygame.Rect(
            self.preview_pos[0] + self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        
        # Color selection buttons
        button_y += self.button_height + section_spacing
        self.prev_color_button = pygame.Rect(
            self.preview_pos[0] - self.button_width - self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        self.next_color_button = pygame.Rect(
            self.preview_pos[0] + self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        
        # Trail buttons
        button_y += self.button_height + section_spacing
        self.prev_trail_button = pygame.Rect(
            self.preview_pos[0] - self.button_width - self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        self.next_trail_button = pygame.Rect(
            self.preview_pos[0] + self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        
        # Hat selection buttons
        button_y += self.button_height + section_spacing
        self.prev_hat_button = pygame.Rect(
            self.preview_pos[0] - self.button_width - self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        self.next_hat_button = pygame.Rect(
            self.preview_pos[0] + self.button_spacing//2,
            button_y,
            self.button_width, self.button_height
        )
        
        # Shop section
        self.shop_pos = (screen_width * 0.75, screen_height * 0.35)
        self.shop_item_spacing = int(50 * self.scale)

    def calculate_points(self):
        return self.player_score // 100  # Convert score to points

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
            color = self.lerp_color(
                (20, 20, 40), 
                (50, 50, 80), 
                (y + self.animation_offset * 50) % screen_height / screen_height
            )
            pygame.draw.line(screen, color, (0, y), (screen_width, y))

        # Draw title
        title = self.large_font.render("Customize Your Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(screen_width * 0.5, screen_height * 0.05))
        screen.blit(title, title_rect)
        
        # Display player points
        points_text = self.small_font.render(f"{self.calculate_points()} points", True, THEME_TEXT)
        points_rect = points_text.get_rect(topright=(screen_width * 0.95, screen_height * 0.05))
        screen.blit(points_text, points_rect)
        
        # Draw trail particles
        self.draw_trail_particles(screen)
        
        # Draw character preview
        pygame.draw.circle(screen, self.colors[self.color_index], self.preview_pos, self.preview_radius)
        self.draw_hat(screen, self.preview_pos, self.preview_radius)
        self.draw_face(screen)
        
        # Draw all buttons
        self.draw_buttons(screen)
        
        # Draw accessories shop
        self.draw_accessories_shop(screen)
        
        # Draw back button
        back_text = self.font.render("Back to Menu", True, THEME_TEXT)
        back_rect = back_text.get_rect(midbottom=(screen_width * 0.5, screen_height * 0.95))
        screen.blit(back_text, back_rect)

    def draw_trail_particles(self, screen):
        particle_spacing = int(25 * self.scale)
        base_particle_size = int(18 * self.scale)
        start_x = self.preview_pos[0] - particle_spacing * 3
        
        for i in range(3):
            particle_size = base_particle_size - (i * 2.0)
            opacity = 200 - (i * 50)
            particle_color = list(self.trail_colors[self.trail_color_index])
            particle_color.append(opacity)
            
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            
            for radius in range(int(particle_size), 0, -1):
                current_opacity = int(opacity * (radius / particle_size) * 0.8)
                current_color = list(self.trail_colors[self.trail_color_index])
                current_color.append(current_opacity)
                pygame.draw.circle(particle_surface, current_color, 
                                 (particle_size, particle_size), radius)
            
            x_pos = start_x + ((2 - i) * (particle_spacing + particle_size))
            screen.blit(particle_surface, 
                       (x_pos, self.preview_pos[1] + 5))

    def draw_face(self, screen):
        eye_radius = max(3, self.preview_radius // 5)
        eye_offset = self.preview_radius // 3
        
        # Draw eyes
        pygame.draw.circle(screen, BLACK, 
                          (int(self.preview_pos[0] - eye_offset), 
                           int(self.preview_pos[1] - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, 
                          (int(self.preview_pos[0] + eye_offset), 
                           int(self.preview_pos[1] - eye_offset)), eye_radius)
        
        # Draw mouth
        if self.current_face == "happy":
            smile_rect = (int(self.preview_pos[0] - self.preview_radius//2), 
                         int(self.preview_pos[1]), 
                         self.preview_radius, 
                         self.preview_radius//2)
            pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, 
                           max(2, self.preview_radius//5))
        else:
            frown_rect = (int(self.preview_pos[0] - self.preview_radius//2), 
                         int(self.preview_pos[1] + self.preview_radius//4), 
                         self.preview_radius, 
                         self.preview_radius//2)
            pygame.draw.arc(screen, BLACK, frown_rect, 0, 3.14, 
                           max(2, self.preview_radius//5))

    def draw_buttons(self, screen):
        # Helper function to draw a button with text
        def draw_button(rect, text):
            pygame.draw.rect(screen, THEME_PRIMARY, rect)
            text_surface = self.font.render(text, True, THEME_TEXT)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        # Draw all buttons
        button_pairs = [
            (self.happy_button, "Happy"),
            (self.sad_button, "Sad"),
            (self.prev_color_button, "< Color"),
            (self.next_color_button, "Color >"),
            (self.prev_trail_button, "< Trail"),
            (self.next_trail_button, "Trail >"),
            (self.prev_hat_button, "< Hat"),
            (self.next_hat_button, "Hat >")
        ]
        
        for rect, text in button_pairs:
            draw_button(rect, text)

    def draw_accessories_shop(self, screen):
        # Draw shop title
        shop_title = self.large_font.render("Accessories Shop", True, THEME_TEXT)
        title_rect = shop_title.get_rect(midtop=(self.shop_pos[0], self.shop_pos[1] - self.shop_item_spacing))
        screen.blit(shop_title, title_rect)
        
        self.accessory_rects = []
        y_offset = 0
        
        for accessory in self.accessories:
            # Draw accessory name and price
            text = f"{accessory['name']} - {accessory['price']} pts"
            text_surface = self.font.render(text, True, THEME_TEXT)
            text_rect = text_surface.get_rect(
                midleft=(self.shop_pos[0] - self.button_width//2, 
                        self.shop_pos[1] + y_offset)
            )
            screen.blit(text_surface, text_rect)
            
            # Draw unlock/unlocked button
            button_text = "Unlock" if not accessory["unlocked"] else "Unlocked"
            button_surface = self.small_font.render(button_text, True, THEME_TEXT)
            button_rect = button_surface.get_rect(
                midleft=(text_rect.right + 20, text_rect.centery)
            )
            screen.blit(button_surface, button_rect)
            
            self.accessory_rects.append((button_rect, accessory))
            y_offset += self.shop_item_spacing

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
                if not accessory["unlocked"] and self.calculate_points() >= accessory['price']:
                    self.player_score -= accessory['price'] * 100  # Convert points back to score
                    accessory["unlocked"] = True
                    print(f"Unlocked {accessory['name']}")
                elif accessory["unlocked"]:
                    print(f"{accessory['name']} is already unlocked")
                else:
                    print("Not enough points")

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def on_screen_resize(self, screen_width, screen_height):
        """Handle screen resize events"""
        self.update_layout(screen_width, screen_height)
