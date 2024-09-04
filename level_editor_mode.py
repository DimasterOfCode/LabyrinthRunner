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

    def update(self):
        pass

    def render(self, screen, interpolation):
        screen.fill(GREEN)
        self.draw_maze(screen)
        self.draw_ui(screen)
        if self.show_help:
            self.draw_help_overlay(screen)

    def draw_ui(self, screen):
        dev_text = self.font.render("Dev Mode: Press H for help", True, BLACK)
        dev_rect = dev_text.get_rect(midtop=(WIDTH // 2, 10))
        screen.blit(dev_text, dev_rect)

        quit_text = self.font.render("Press ESC to return to menu", True, BLACK)
        quit_rect = quit_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
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
        elif event.key == pygame.K_n:
            self.selected_item = Enemy.SYMBOL
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
        elif event.key == pygame.K_e:
            self.level_manager.get_current_level().maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        elif event.key == pygame.K_LEFTBRACKET:
            self.level_manager.prev_level()
        elif event.key == pygame.K_RIGHTBRACKET:
            self.level_manager.next_level()

    def draw_maze(self, screen):
        current_maze = self.level_manager.get_current_level().maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE + self.game.offset_x, y * CELL_SIZE + self.game.offset_y, CELL_SIZE, CELL_SIZE)
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

    def draw_help_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black background

        help_text = [
            "Dev Mode Hotkeys:",
            "P - Place Player",
            "N - Place Enemy",
            "S - Place Star",
            "M - Place Diamond",
            "W - Place Wall",
            "C - Clear/Empty cell",
            "SPACE - Save maze",
            "L - Load maze",
            "E - Erase entire maze",
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

        y_offset = 50
        for line in help_text:
            text_surface = self.font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset))
            overlay.blit(text_surface, text_rect)
            y_offset += 30

        screen.blit(overlay, (0, 0))

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
        x, y = pos
        cell_x = (x - self.game.offset_x) // CELL_SIZE
        cell_y = (y - self.game.offset_y) // CELL_SIZE
        if 0 <= cell_x < MAZE_WIDTH and 0 <= cell_y < MAZE_HEIGHT:
            self.level_manager.get_current_level().maze[cell_y][cell_x] = self.selected_item
