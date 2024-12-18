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
        
        # Particle system
        self.particles = []
        self.particle_colors = [(255, 215, 0), (135, 206, 250), (255, 182, 193)]  # Gold, Light Blue, Light Pink
        
        # Stats display
        self.show_stats = True
        self.stats_alpha = 0
        self.stats_fade_speed = 5

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
        
        # Update particles
        self.update_particles()
        
        # Update stats fade effect
        if self.show_stats:
            self.stats_alpha = min(255, self.stats_alpha + self.stats_fade_speed)
        else:
            self.stats_alpha = max(0, self.stats_alpha - self.stats_fade_speed)

    def update_particles(self):
        # Add new particles occasionally
        if random.random() < 0.1:
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': HEIGHT + 10,
                'speed': random.uniform(1, 3),
                'size': random.randint(2, 6),
                'color': random.choice(self.particle_colors)
            })
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                self.particles.remove(particle)

    def render(self, screen, interpolation):
        # Update fonts for current screen size
        self.update_fonts(screen)
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        scale = self.get_screen_scale(screen)
        
        # Draw animated background
        screen.fill(THEME_BACKGROUND)
        
        # Draw particles with adjusted coordinates
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x'] * screen_width/WIDTH), 
                              int(particle['y'] * screen_height/HEIGHT)), 
                             particle['size'])
        
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
        
        # Draw enemy and player characters
        self.draw_characters(screen)
        
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
                desc = self.small_font.render(button["description"], True, THEME_TEXT)
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

    def draw_characters(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate scale factor based on screen dimensions
        scale = min(screen_width/WIDTH, screen_height/HEIGHT)
        
        # Base sizes scaled by screen
        base_radius = int(80 * scale)
        base_eye_radius = int(10 * scale)
        base_eye_offset = int(25 * scale)
        base_eye_shift = int(10 * scale)
        base_eyebrow_length = int(20 * scale)
        base_line_width = max(2, int(4 * scale))  # Ensure minimum line width of 2
        
        # Update enemy position - move further left
        enemy_center = (screen_width//2 - screen_width//3, screen_height//2 - 40 * scale)
        enemy_radius = base_radius
        
        # Draw main enemy circle with pulsing effect
        pulse = math.sin(self.animation_offset) * 5 * scale
        pygame.draw.circle(screen, (255, 0, 0), enemy_center, enemy_radius + pulse, base_line_width)
        
        # Draw evil eyes with animation
        eye_y_offset = math.sin(self.animation_offset) * 3 * scale
        
        # Left eye
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(enemy_center[0] - base_eye_offset + base_eye_shift), 
                          int(enemy_center[1] - 15 * scale + eye_y_offset)), 
                         base_eye_radius)
        # Right eye
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(enemy_center[0] + base_eye_offset + base_eye_shift), 
                          int(enemy_center[1] - 15 * scale + eye_y_offset)), 
                         base_eye_radius)
        
        # Draw evil eyebrows
        eyebrow_angle = -math.pi / 6
        
        # Left and right eyebrows
        for x_mult in [-1, 1]:
            brow_start = (enemy_center[0] + x_mult * base_eye_offset + base_eye_shift 
                         - x_mult * base_eyebrow_length * math.cos(eyebrow_angle),
                         enemy_center[1] - 30 * scale 
                         - base_eyebrow_length * math.sin(eyebrow_angle))
            brow_end = (enemy_center[0] + x_mult * base_eye_offset + base_eye_shift 
                       + x_mult * base_eyebrow_length * math.cos(eyebrow_angle),
                       enemy_center[1] - 30 * scale 
                       + base_eyebrow_length * math.sin(eyebrow_angle))
            pygame.draw.line(screen, (255, 0, 0), brow_start, brow_end, base_line_width)
        
        # Draw evil smile with animation
        smile_offset = math.sin(self.animation_offset) * 5 * scale
        smile_rect = pygame.Rect(enemy_center[0] - 35 * scale + base_eye_shift, 
                               enemy_center[1] - 30 * scale + smile_offset, 
                               70 * scale, 50 * scale)
        pygame.draw.arc(screen, (255, 0, 0), smile_rect, math.pi, 2 * math.pi, base_line_width)
        
        # Update player position - move further right
        player_center = (screen_width//2 + screen_width//3, screen_height//2 - 40 * scale)
        player_radius = base_radius
        
        # Draw player with bounce animation
        bounce = math.sin(self.animation_offset * 2) * 10 * scale
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (player_center[0], player_center[1] + bounce), 
                         player_radius, base_line_width)
        
        # Draw player eyes
        eye_backward_shift = base_eye_shift  # Shift eyes left to look at enemy
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (int(player_center[0] - base_eye_offset - eye_backward_shift), 
                          int(player_center[1] - 15 * scale + bounce)), 
                         base_eye_radius)
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (int(player_center[0] + base_eye_offset - eye_backward_shift), 
                          int(player_center[1] - 15 * scale + bounce)), 
                         base_eye_radius)
        
        # Draw player mouth
        pygame.draw.circle(screen, THEME_SECONDARY,
                         (int(player_center[0] - eye_backward_shift), 
                          int(player_center[1] + 15 * scale + bounce)),
                         base_eye_radius)

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
