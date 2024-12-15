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
        self.title_font = pygame.font.Font(None, 80)
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        
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
        # Draw animated background
        screen.fill(THEME_BACKGROUND)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Draw animated title with bounce effect
        title = self.title_font.render("Labyrinth Runner", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(WIDTH//2, 50 + self.title_bounce))
        screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.small_font.render("Navigate through mazes, collect stars, avoid enemies!", True, THEME_SECONDARY)
        subtitle_rect = subtitle.get_rect(midtop=(WIDTH//2, title_rect.bottom + 20))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw enemy and player characters
        self.draw_characters(screen)
        
        # Draw menu buttons with hover effects and descriptions
        button_start_y = HEIGHT//2 - 50
        for i, button in enumerate(self.buttons):
            text = self.small_font.render(button["text"], True, THEME_TEXT)
            button_rect = text.get_rect(center=(WIDTH//2, button_start_y + i * 60))
            
            # Draw button background with animation if selected
            if i == self.selected_button:
                # Animated selection background
                padding = 10 + math.sin(self.animation_offset) * 5
                pygame.draw.rect(screen, THEME_SECONDARY, 
                               button_rect.inflate(padding * 2, padding),
                               border_radius=5)
                
                # Draw description
                desc = self.small_font.render(button["description"], True, THEME_TEXT)
                desc_rect = desc.get_rect(midtop=(WIDTH//2, button_rect.bottom + 5))
                screen.blit(desc, desc_rect)
            
            screen.blit(text, button_rect)
        
        # Draw help overlay if active
        if self.show_help_overlay:
            self.draw_help_overlay(screen)
        
        # Draw current level and high score
        stats_text = [
            f"Current Level: {self.game.level_manager.get_current_level().level_number}/{len(self.game.level_manager.levels)}",
            f"High Score: {max(self.game.level_scores.values()) if self.game.level_scores else 0}"
        ]
        
        y_pos = HEIGHT - 60
        for text in stats_text:
            text_surface = self.small_font.render(text, True, THEME_TEXT)
            text_rect = text_surface.get_rect(center=(WIDTH//2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25

    def draw_characters(self, screen):
        # Draw enemy circle on the left
        enemy_center = (WIDTH//2 - 250, HEIGHT//2 - 40)
        enemy_radius = 80
        
        # Draw main enemy circle with pulsing effect
        pulse = math.sin(self.animation_offset) * 5
        pygame.draw.circle(screen, (255, 0, 0), enemy_center, enemy_radius + pulse, 4)
        
        # Draw evil eyes with animation (shifted right to look at player)
        eye_radius = 10
        eye_offset = 25
        eye_forward_shift = 10  # Shift eyes right to look at player
        eye_y_offset = math.sin(self.animation_offset) * 3
        pygame.draw.circle(screen, (255, 0, 0), 
                         (enemy_center[0] - eye_offset + eye_forward_shift, enemy_center[1] - 15 + eye_y_offset), 
                         eye_radius)
        pygame.draw.circle(screen, (255, 0, 0), 
                         (enemy_center[0] + eye_offset + eye_forward_shift, enemy_center[1] - 15 + eye_y_offset), 
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
        
        # Draw evil smile with animation
        smile_offset = math.sin(self.animation_offset) * 5
        smile_rect = pygame.Rect(enemy_center[0] - 35 + eye_forward_shift, 
                               enemy_center[1] - 30 + smile_offset, 
                               70, 50)
        pygame.draw.arc(screen, (255, 0, 0), smile_rect, math.pi, 2 * math.pi, 4)
        
        # Draw player circle on the right
        circle_center = (WIDTH//2 + 250, HEIGHT//2 - 40)
        circle_radius = 80
        
        # Draw player with bounce animation
        bounce = math.sin(self.animation_offset * 2) * 10
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (circle_center[0], circle_center[1] + bounce), 
                         circle_radius, 4)
        
        # Draw player eyes (shifted left to look at enemy)
        eye_backward_shift = 10  # Shift eyes left to look at enemy
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (circle_center[0] - eye_offset - eye_backward_shift, circle_center[1] - 15 + bounce), 
                         eye_radius)
        pygame.draw.circle(screen, THEME_SECONDARY, 
                         (circle_center[0] + eye_offset - eye_backward_shift, circle_center[1] - 15 + bounce), 
                         eye_radius)
        
        # Draw player mouth (shifted left)
        pygame.draw.circle(screen, THEME_SECONDARY,
                         (circle_center[0] - eye_backward_shift, circle_center[1] + 15 + bounce),
                         eye_radius)

    def draw_help_overlay(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark semi-transparent background
        screen.blit(overlay, (0, 0))

        # Help title
        help_title = self.font.render("Game Controls", True, THEME_TEXT)
        title_rect = help_title.get_rect(midtop=(WIDTH//2, HEIGHT//4))
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

        y_pos = title_rect.bottom + 30
        for instruction in instructions:
            if instruction == "":
                y_pos += 10  # Add extra space for empty lines
                continue
            text = self.small_font.render(instruction, True, THEME_TEXT)
            text_rect = text.get_rect(midtop=(WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 30

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
