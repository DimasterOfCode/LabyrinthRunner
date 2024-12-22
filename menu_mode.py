import random
import time
import math
import os

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
        self.title = "Labyrinth Runner"
        self.title_font_size = 80
        self.menu_font_size = 50
        self.small_font_size = 30
        
        # Initialize fonts with default sizes
        self.update_fonts(game.screen)  # Changed from WIDTH, HEIGHT to screen
        
        # Menu items with descriptions
        self.buttons = [
            {
                "text": "Play",
                "action": lambda: self.game.set_mode("play"),
                "description": "Start your adventure"
            },
            # Uncomment when shop is ready
            # {
            #     "text": "Shop",
            #     "action": lambda: self.game.set_mode("shop"),
            #     "description": "Browse and purchase items"
            # },
            {
                "text": "Level Editor",
                "action": lambda: self.game.set_mode("level_editor"),
                "description": "Create and edit your own maze levels"
            },
            {
                "text": "Customize Runner",
                "action": lambda: self.game.set_mode("runner_customization"),
                "description": "Personalize your runner's appearance"
            },
            {
                "text": "Help",
                "action": lambda: self.toggle_help(),
                "description": "View game controls and instructions"
            }
        ]
        self.selected_button = 0
        self.show_help_overlay = False
        
        # Animation variables
        self.animation_offset = 0
        self.animation_speed = 0.5
        self.title_bounce = 0
        self.title_bounce_speed = 3
        self.title_bounce_height = 10
        
        # Stats display
        self.show_stats = True
        self.stats_alpha = 0
        self.stats_fade_speed = 5
        
        # Add background image loading after other initializations
        background_path = os.path.join("assets", "background.png")
        try:
            self.background = pygame.image.load(background_path).convert()
        except pygame.error as e:
            print(f"Warning: Could not load background image: {e}")
            self.background = None

    def update_fonts(self, screen):
        """Update font sizes based on screen dimensions"""
        scale = self.get_screen_scale(screen)
        self.title_font = pygame.font.Font(None, int(self.title_font_size * scale))
        self.font = pygame.font.Font(None, int(self.menu_font_size * scale))
        self.small_font = pygame.font.Font(None, int(self.small_font_size * scale))

    def update(self):
        # Update menu animations
        self.animation_offset = (self.animation_offset + self.animation_speed) % (2 * math.pi)
        self.title_bounce = math.sin(pygame.time.get_ticks() / 500) * self.title_bounce_height
        
        # Update stats fade effect
        if self.show_stats:
            self.stats_alpha = min(255, self.stats_alpha + self.stats_fade_speed)
        else:
            self.stats_alpha = max(0, self.stats_alpha - self.stats_fade_speed)

    def render(self, screen, interpolation):
        # Update fonts for current screen size
        self.update_fonts(screen)
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        scale = self.get_screen_scale(screen)
        
        # Draw background with dimming effect
        if self.background:
            # Calculate scaling to fit width while maintaining aspect ratio
            bg_aspect_ratio = self.background.get_width() / self.background.get_height()
            new_width = screen_width
            new_height = int(screen_width / bg_aspect_ratio)
            
            # If height is too short, center it vertically
            y_offset = (screen_height - new_height) // 2
            
            scaled_background = pygame.transform.scale(self.background, (new_width, new_height))
            
            # Create a dark overlay matching the screen size
            dark_overlay = pygame.Surface((screen_width, screen_height))
            dark_overlay.fill((0, 0, 0))  # Black overlay
            
            # Fill screen with black first to cover any gaps
            screen.fill((0, 0, 0))
            
            # Draw background centered
            screen.blit(scaled_background, (0, y_offset))
            
            # Apply overlay
            dark_overlay.set_alpha(128)
            screen.blit(dark_overlay, (0, 0))
        else:
            screen.fill(THEME_BACKGROUND)
        
        # Draw animated title with bounce effect - adjust for screen size
        title = self.title_font.render("Labyrinth Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(screen_width//2, 
                                           (50 + self.title_bounce) * screen_height/HEIGHT))
        screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.small_font.render("Navigate through mazes, collect stars, avoid enemies!", 
                                        True, THEME_SECONDARY)
        subtitle_rect = subtitle.get_rect(midtop=(screen_width//2, title_rect.bottom + 20))
        screen.blit(subtitle, subtitle_rect)
        
        # Calculate spacing based on screen height
        total_buttons = len(self.buttons)
        button_spacing = min(60 * screen_height/HEIGHT, 
                            (screen_height * 0.4) / total_buttons)  # Limit maximum spacing
        
        # Draw menu buttons with hover effects and descriptions
        button_start_y = screen_height//2 - (total_buttons * button_spacing)/2
        
        for i, button in enumerate(self.buttons):
            text = self.small_font.render(button["text"], True, THEME_TEXT)
            button_rect = text.get_rect(center=(screen_width//2, 
                                              button_start_y + i * button_spacing))
            
            # Draw button background with animation if selected
            if i == self.selected_button:
                # Animated selection background
                padding = 10 + math.sin(self.animation_offset) * 5
                pygame.draw.rect(screen, THEME_SECONDARY, 
                               button_rect.inflate(padding * 2, padding),
                               border_radius=5)
                
                # Draw description
                desc = self.small_font.render(button["description"], True, THEME_TEXT_SECONDARY)
                desc_rect = desc.get_rect(midtop=(screen_width//2, button_rect.bottom + 5))
                screen.blit(desc, desc_rect)
            
            screen.blit(text, button_rect)
        
        # Draw help overlay if active
        if self.show_help_overlay:
            self.draw_help_overlay(screen)
        
        # Draw current level and high score at bottom
        stats_text = [
            f"Current Level: {self.game.level_manager.get_current_level().level_number}/{len(self.game.level_manager.levels)}",
            f"High Score: {max(self.game.level_scores.values()) if self.game.level_scores else 0}"
        ]
        
        y_pos = screen_height - 60
        for text in stats_text:
            text_surface = self.small_font.render(text, True, THEME_TEXT)
            text_rect = text_surface.get_rect(center=(screen_width//2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25

    def draw_help_overlay(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Help title
        help_title = self.font.render("Game Controls", True, THEME_TEXT)
        title_rect = help_title.get_rect(midtop=(screen_width//2, screen_height//4))
        screen.blit(help_title, title_rect)

        # Help instructions
        instructions = [
            "Menu Navigation:",
            "↑↓ Arrow Keys - Move selection",
            "ENTER - Select option",
            "",
            "In-Game Controls:",
            "Arrow Keys - Move player",
            "ESC - Pause game/Return to menu",
            "F11 - Toggle fullscreen",
            "",
            "Press ESC to close help"
        ]

        # Calculate spacing based on screen height
        spacing = min(30, screen_height / (len(instructions) + 8))  # +8 for padding
        y_pos = title_rect.bottom + spacing

        for instruction in instructions:
            if instruction == "":
                y_pos += spacing/2  # Add extra space for empty lines
                continue
            text = self.small_font.render(instruction, True, THEME_TEXT)
            text_rect = text.get_rect(midtop=(screen_width//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += spacing

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.show_help_overlay:
                if event.key == pygame.K_ESCAPE:
                    self.show_help_overlay = False
                    self.game.sound_manager.play_sound('menu_move')
            else:
                if event.key == pygame.K_UP:
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                    self.game.sound_manager.play_sound('menu_move')
                elif event.key == pygame.K_DOWN:
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
                    self.game.sound_manager.play_sound('menu_move')
                elif event.key == pygame.K_RETURN:
                    self.game.sound_manager.play_sound('menu_select')
                    self.buttons[self.selected_button]["action"]()

    def toggle_help(self):
        self.show_help_overlay = not self.show_help_overlay

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
