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

class CustomizationSlot:
    def __init__(self, name, items, default_index=0):
        self.name = name
        self.items = items
        self.current_index = default_index
    
    @property
    def current_item(self):
        return self.items[self.current_index]

    def next_item(self):
        self.current_index = (self.current_index + 1) % len(self.items)

    def prev_item(self):
        self.current_index = (self.current_index - 1) % len(self.items)

class RunnerCustomizationMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.setup_initial_state()
        self.update_layout(game.screen.get_width(), game.screen.get_height())

    def setup_initial_state(self):
        """Initialize customization slots and their items"""
        # Define available items for each slot
        self.slots = {
            "hat": CustomizationSlot("Hat", [
                {"id": "none", "name": "No Hat"},
                {"id": "black_hat", "name": "Black Hat"}
            ]),
            "body": CustomizationSlot("Body", [
                {"id": "happy", "name": "Happy Face"},
                {"id": "sad", "name": "Sad Face"}
            ]),
            "body_color": CustomizationSlot("Body Color", [
                {"id": "red", "name": "Red", "color": (255, 0, 0)},
                {"id": "green", "name": "Green", "color": (0, 255, 0)},
                {"id": "yellow", "name": "Yellow", "color": (255, 255, 0)},
                {"id": "magenta", "name": "Magenta", "color": (255, 0, 255)},
                {"id": "blue", "name": "Blue", "color": (0, 0, 255)}
            ]),
            "trail": CustomizationSlot("Trail", [
                {"id": "none", "name": "No Trail"},
                {"id": "circles", "name": "Circles"}
            ]),
            "trail_color": CustomizationSlot("Trail Color", [
                {"id": "teal", "name": "Teal", "color": (0, 128, 128)},
                {"id": "pink", "name": "Pink", "color": (255, 192, 203)}
            ])
        }

        # Animation state
        self.animation_offset = 0

    def update_layout(self, screen_width, screen_height):
        """Update all UI elements based on screen dimensions"""
        self.scale = min(screen_width / 1280, screen_height / 720)
        
        # Update fonts
        self.font = pygame.font.Font(None, int(36 * self.scale))
        self.large_font = pygame.font.Font(None, int(48 * self.scale))
        
        # Calculate dimensions
        self.button_width = int(120 * self.scale)
        self.button_height = int(40 * self.scale)
        self.button_spacing = int(20 * self.scale)
        self.preview_radius = int(60 * self.scale)
        
        # Preview position
        self.preview_pos = (screen_width * 0.7, screen_height * 0.4)
        
        # Calculate slot positions
        self.slot_buttons = {}
        start_y = screen_height * 0.2
        slot_spacing = screen_height * 0.12
        
        for i, slot_name in enumerate(self.slots.keys()):
            y_pos = start_y + (i * slot_spacing)
            
            # Previous button
            prev_rect = pygame.Rect(
                screen_width * 0.2,
                y_pos,
                self.button_width,
                self.button_height
            )
            
            # Next button
            next_rect = pygame.Rect(
                screen_width * 0.4,
                y_pos,
                self.button_width,
                self.button_height
            )
            
            self.slot_buttons[slot_name] = {
                "prev": prev_rect,
                "next": next_rect,
                "label_pos": (screen_width * 0.3, y_pos - self.button_height * 0.5)
            }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check slot button clicks
            for slot_name, buttons in self.slot_buttons.items():
                if buttons["prev"].collidepoint(mouse_pos):
                    self.slots[slot_name].prev_item()
                elif buttons["next"].collidepoint(mouse_pos):
                    self.slots[slot_name].next_item()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")

    def render(self, screen, interpolation):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Draw background
        screen.fill((20, 20, 40))

        # Draw title
        title = self.large_font.render("Customize Your Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(screen_width * 0.5, screen_height * 0.05))
        screen.blit(title, title_rect)

        # Draw slots and their controls
        for slot_name, buttons in self.slot_buttons.items():
            slot = self.slots[slot_name]
            current_item = slot.current_item

            # Draw slot label
            label = self.font.render(f"{slot.name}: {current_item['name']}", True, THEME_TEXT)
            screen.blit(label, buttons["label_pos"])

            # Draw navigation buttons
            pygame.draw.rect(screen, THEME_PRIMARY, buttons["prev"])
            pygame.draw.rect(screen, THEME_PRIMARY, buttons["next"])
            
            prev_text = self.font.render("<", True, THEME_TEXT)
            next_text = self.font.render(">", True, THEME_TEXT)
            
            screen.blit(prev_text, prev_text.get_rect(center=buttons["prev"].center))
            screen.blit(next_text, next_text.get_rect(center=buttons["next"].center))

        # Draw preview
        self.draw_preview(screen)

    def draw_preview(self, screen):
        # Draw body
        body_color = self.slots["body_color"].current_item["color"]
        pygame.draw.circle(screen, body_color, self.preview_pos, self.preview_radius)

        # Draw face
        self.draw_face(screen)

        # Draw hat
        if self.slots["hat"].current_item["id"] == "black_hat":
            self.draw_hat(screen, self.preview_pos, self.preview_radius)

        # Draw trail if enabled
        if self.slots["trail"].current_item["id"] == "circles":
            self.draw_trail(screen)

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
        if self.slots["body"].current_item["id"] == "happy":
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

    def draw_hat(self, screen, pos, radius):
        # Reduce the offset even further to make hats sit much lower on the circle
        hat_y_offset = radius * 0.05  # Changed from 0.2 to 0.05
        
        if self.slots["hat"].current_item["id"] == "black_hat":
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
                
        elif self.slots["hat"].current_item["id"] == "crown":
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
        
        elif self.slots["hat"].current_item["id"] == "cap":
            pygame.draw.ellipse(screen, self.slots["body_color"].current_item["color"],
                (pos[0] - radius * 1.2,
                 pos[1] - radius - hat_y_offset + radius * 0.3,
                 radius * 1.5, radius * 0.3))
            
            pygame.draw.arc(screen, self.slots["body_color"].current_item["color"],
                (pos[0] - radius,
                 pos[1] - radius - hat_y_offset - radius * 0.5,
                 radius * 2, radius * 1.2),
                math.pi, 2 * math.pi)

    def draw_trail(self, screen):
        particle_spacing = int(25 * self.scale)
        base_particle_size = int(18 * self.scale)
        start_x = self.preview_pos[0] - particle_spacing * 10
        
        for i in range(3):
            particle_size = base_particle_size - (i * 2.0)
            opacity = 200 - (i * 50)
            particle_color = list(self.slots["trail_color"].current_item["color"])
            particle_color.append(opacity)
            
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            
            for radius in range(int(particle_size), 0, -1):
                current_opacity = int(opacity * (radius / particle_size) * 0.8)
                current_color = list(self.slots["trail_color"].current_item["color"])
                current_color.append(current_opacity)
                pygame.draw.circle(particle_surface, current_color, 
                                 (particle_size, particle_size), radius)
            
            x_pos = start_x + ((2 - i) * (particle_spacing + particle_size))
            screen.blit(particle_surface, 
                       (x_pos, self.preview_pos[1] + 5))

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def on_screen_resize(self, screen_width, screen_height):
        """Handle screen resize events"""
        self.update_layout(screen_width, screen_height)

    def get_player_color(self):
        """Get the currently selected body color"""
        return self.slots["body_color"].current_item["color"]

    def get_player_face(self):
        """Get the currently selected face type"""
        return self.slots["body"].current_item["id"]

    def get_trail_color(self):
        """Get the currently selected trail color"""
        return self.slots["trail_color"].current_item["color"]

    def get_player_hat(self):
        """Get the currently selected hat type"""
        return self.slots["hat"].current_item["id"]

    def get_trail_type(self):
        """Get the currently selected trail type"""
        return self.slots["trail"].current_item["id"]
