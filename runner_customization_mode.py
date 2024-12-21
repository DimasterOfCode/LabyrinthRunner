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
                ITEMS["hat"]["none"],
                ITEMS["hat"]["top_hat"]
            ]),
            "body": CustomizationSlot("Body", [
                ITEMS["face"]["happy"],
                ITEMS["face"]["sad"]
            ]),
            "body_color": CustomizationSlot("Body Color", [
                {"id": "red", "name": "Red", "color": (255, 0, 0)},
                {"id": "green", "name": "Green", "color": (0, 255, 0)},
                {"id": "yellow", "name": "Yellow", "color": (255, 255, 0)},
                {"id": "magenta", "name": "Magenta", "color": (255, 0, 255)},
                {"id": "blue", "name": "Blue", "color": (0, 0, 255)}
            ]),
            "trail": CustomizationSlot("Trail", [
                ITEMS["trail"]["none"],
                ITEMS["trail"]["circles"]
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
            
            # Get name from either SlotItem instance or dictionary
            item_name = current_item.name if hasattr(current_item, 'name') else current_item["name"]
            
            # Draw slot label
            label = self.font.render(f"{slot.name}: {item_name}", True, THEME_TEXT)
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
        # Get current customization values
        body_color = self.slots["body_color"].current_item["color"]
        
        # Handle SlotItem instances
        face_item = self.slots["body"].current_item
        face_type = face_item.id if hasattr(face_item, 'id') else face_item["id"]
        
        hat_item = self.slots["hat"].current_item
        hat_type = hat_item.id if hasattr(hat_item, 'id') else hat_item["id"]
        
        trail_item = self.slots["trail"].current_item
        trail_type = trail_item.id if hasattr(trail_item, 'id') else trail_item["id"]

        # Draw trail if enabled using PlayerRenderer
        if trail_type != "none":
            # Position trail to the right of the player
            trail_offset = self.preview_radius * 2  # Offset by player diameter
            trail_pos = (self.preview_pos[0] + trail_offset, self.preview_pos[1])
            PlayerRenderer.draw_trail(
                screen=screen,
                pos=trail_pos,
                radius=self.preview_radius,
                scale=1.0,
                trail_type=trail_type,
                trail_color=self.slots["trail_color"].current_item["color"]
            )

        # Use shared renderer for player
        PlayerRenderer.draw_player(
            screen=screen,
            pos=self.preview_pos,
            radius=self.preview_radius,
            color=body_color,
            face_type=face_type,
            hat_type=hat_type,
            scale=1.0  # Preview uses base scale
        )

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
        item = self.slots["body"].current_item
        return item.id if hasattr(item, 'id') else item["id"]

    def get_trail_color(self):
        """Get the currently selected trail color"""
        return self.slots["trail_color"].current_item["color"]

    def get_player_hat(self):
        """Get the currently selected hat type"""
        item = self.slots["hat"].current_item
        return item.id if hasattr(item, 'id') else item["id"]

    def get_trail_type(self):
        """Get the currently selected trail type"""
        item = self.slots["trail"].current_item
        return item.id if hasattr(item, 'id') else item["id"]
