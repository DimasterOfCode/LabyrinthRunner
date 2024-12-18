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

class LevelEditorMode(GameMode):
    def __init__(self, game, level_manager):
        super().__init__(game)
        self.level_manager = level_manager
        self.selected_item = ' '
        self.is_drawing = False
        self.show_help = False
        self.font = pygame.font.Font(None, 36)
        # Store initial dimensions
        self.base_width = WIDTH
        self.base_height = HEIGHT

    def update(self):
        pass

    def render(self, screen, interpolation):
        screen_width, screen_height = screen.get_size()
        
        # Draw gradient background for full screen
        for y in range(screen_height):
            color = self.lerp_color(THEME_BACKGROUND, THEME_PRIMARY, y / screen_height)
            pygame.draw.line(screen, color, (0, y), (screen_width, y))

        self.draw_maze(screen)
        self.draw_ui(screen)
        if self.show_help:
            self.draw_help_overlay(screen)

    def draw_ui(self, screen):
        screen_width, screen_height = screen.get_size()
        
        dev_text = self.font.render("Dev Mode: Press H for help", True, THEME_TEXT)
        dev_rect = dev_text.get_rect(midtop=(screen_width // 2, 10))
        screen.blit(dev_text, dev_rect)

        quit_text = self.font.render("Press ESC to return to menu", True, THEME_TEXT)
        quit_rect = quit_text.get_rect(midbottom=(screen_width // 2, screen_height - 10))
        screen.blit(quit_text, quit_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")
            elif event.key == pygame.K_h:
                self.show_help = not self.show_help
            else:
                self.handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mousebuttondown(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mousebuttonup(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mousemotion(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_p:
            self.selected_item = Player.SYMBOL
        elif event.key == pygame.K_e:
            self.selected_item = Enemy.SYMBOL
        elif event.key == pygame.K_n:
            self.level_manager.new_level()
            print("Created new level")
        elif event.key == pygame.K_s:
            self.selected_item = Star.SYMBOL
        elif event.key == pygame.K_m:
            self.selected_item = Diamond.SYMBOL
        elif event.key == pygame.K_w:
            self.selected_item = 'X'
        elif event.key == pygame.K_c:
            self.selected_item = ' '
        elif event.key == pygame.K_SPACE:
            self.level_manager.save_levels_to_file()
            print(f"Level {self.level_manager.get_current_level().level_number} saved")
        elif event.key == pygame.K_l:
            self.level_manager.load_levels_from_file()
            print(f"Levels loaded from {self.level_manager.levels_file}")
        elif event.key == pygame.K_r:
            self.level_manager.get_current_level().maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        elif event.key == pygame.K_LEFTBRACKET:
            self.level_manager.prev_level()
        elif event.key == pygame.K_RIGHTBRACKET:
            self.level_manager.next_level()

    def draw_maze(self, screen):
        screen_width, screen_height = screen.get_size()
        
        # Calculate scaling factors
        scale = min(screen_width / self.base_width, (screen_height - SCORE_AREA_HEIGHT) / (self.base_height - SCORE_AREA_HEIGHT))
        scaled_cell_size = CELL_SIZE * scale
        
        # Recalculate offset to center the maze
        offset_x = (screen_width - MAZE_WIDTH * scaled_cell_size) // 2
        offset_y = SCORE_AREA_HEIGHT * scale
        
        current_maze = self.level_manager.get_current_level().maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                # Add 1 pixel to width and height to eliminate gaps
                rect = pygame.Rect(
                    int(x * scaled_cell_size + offset_x),
                    int(y * scaled_cell_size + offset_y),
                    int(scaled_cell_size + 1),  # Add 1 to overlap with next cell
                    int(scaled_cell_size + 1)   # Add 1 to overlap with next cell
                )
                if cell == 'X':
                    pygame.draw.rect(screen, BLACK, rect)
                elif cell == ' ':
                    pygame.draw.rect(screen, WHITE, rect)
                elif cell == 'S':
                    pygame.draw.rect(screen, LIGHT_BROWN, rect)
                elif cell == 'E':
                    pygame.draw.rect(screen, RED, rect)
                elif cell == '*':
                    pygame.draw.rect(screen, GOLD, rect)
                elif cell == 'D':
                    pygame.draw.rect(screen, CYAN, rect)
                
                # Draw grid lines
                pygame.draw.rect(screen, (128, 128, 128), rect, 1)  # Gray color, 1 pixel width

    def draw_help_overlay(self, screen):
        screen_width, screen_height = screen.get_size()
        
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((*THEME_BACKGROUND[:3], 200))
        screen.blit(overlay, (0, 0))

        help_text = [
            "Dev Mode Hotkeys:",
            "P - Place Player",
            "E - Place Enemy",
            "S - Place Star",
            "M - Place Diamond",
            "W - Place Wall",
            "C - Clear/Empty cell",
            "SPACE - Save maze",
            "L - Load maze",
            "R - Erase entire maze",
            "ESC - Exit Dev Mode",
            "",
            "Level Management:",
            "N - New level",
            "S - Save current level",
            "[ - Previous level",
            "] - Next level",
            "",
            "Click and drag to draw",
            "",
            "Press H to close this help"
        ]

        y_offset = screen_height * 0.1  # Start at 10% of screen height
        line_spacing = screen_height * 0.04  # 4% of screen height between lines
        for line in help_text:
            text_surface = self.font.render(line, True, THEME_TEXT)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += line_spacing

    def handle_mousebuttondown(self, event):
        if event.button == 1:
            self.is_drawing = True
            self.draw_cell(event.pos)

    def handle_mousebuttonup(self, event):
        if event.button == 1:
            self.is_drawing = False

    def handle_mousemotion(self, event):
        if self.is_drawing:
            self.draw_cell(event.pos)

    def draw_cell(self, pos):
        screen_width, screen_height = self.game.screen.get_size()
        scale = min(screen_width / self.base_width, (screen_height - SCORE_AREA_HEIGHT) / (self.base_height - SCORE_AREA_HEIGHT))
        scaled_cell_size = CELL_SIZE * scale
        
        # Calculate new offsets
        offset_x = (screen_width - MAZE_WIDTH * scaled_cell_size) // 2
        offset_y = SCORE_AREA_HEIGHT * scale
        
        x, y = pos
        cell_x = int((x - offset_x) // scaled_cell_size)
        cell_y = int((y - offset_y) // scaled_cell_size)
        
        if 0 <= cell_x < MAZE_WIDTH and 0 <= cell_y < MAZE_HEIGHT:
            self.level_manager.get_current_level().maze[cell_y][cell_x] = self.selected_item

    def on_screen_resize(self, screen_width, screen_height):
        """Handle screen resize events"""
        scale = self.get_screen_scale(self.game.screen)
        self.font = pygame.font.Font(None, int(36 * scale))
