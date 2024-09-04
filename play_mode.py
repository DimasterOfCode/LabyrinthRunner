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


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()

class PlayMode(GameMode):
    def __init__(self, game, level_manager):
        super().__init__(game)
        self.level_manager = level_manager
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.state = GameState.PLAYING
        self.init_game_objects()

    def get_current_maze(self):
        return self.level_manager.get_current_level().maze

    def init_game_objects(self):
        player_color = self.game.modes["runner_customization"].get_player_color()
        self.player = self.create_player(player_color)
        self.enemy = self.create_enemy()
        self.star = self.create_star()
        self.diamonds = self.create_diamonds()
        self.coins = self.create_coins(0)
        self.score = 0
        self.state = GameState.PLAYING

    def update(self):
        if self.state == GameState.PLAYING:
            self.player.update()
            if self.enemy:
                self.enemy.update((self.player.x, self.player.y))
            self.collect_coins()
            self.check_enemy_collision()
            self.check_level_complete()
        elif self.state == GameState.PAUSED:
            pass  # Do nothing when paused
        elif self.state == GameState.GAME_OVER:
            pass  # Maybe add a game over animation or countdown here
        elif self.state == GameState.LEVEL_COMPLETE:
            pass  # Maybe add a level complete animation here

    def render(self, screen, interpolation):
        # Draw gradient background
        self.draw_gradient_background(screen)

        # Render maze and other game elements
        self.render_maze(screen)
        self.render_game_objects(screen, interpolation)
        self.draw_score_area(screen)

        # Render state-specific overlays
        if self.state == GameState.PAUSED:
            self.render_pause_overlay(screen)
        elif self.state == GameState.GAME_OVER:
            self.render_game_over_overlay(screen)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.render_level_complete_overlay(screen)

        self.draw_ui(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
                else:  # GAME_OVER or LEVEL_COMPLETE
                    self.game.set_mode("menu")
            elif event.key == pygame.K_x and self.state == GameState.PAUSED:
                self.game.set_mode("menu")
            elif self.state == GameState.LEVEL_COMPLETE and event.key == pygame.K_n:
                self.next_level()
            elif self.state == GameState.PLAYING:
                self.handle_player_input(event)

    def check_collision(self, x, y, radius):
        return MazeUtils.check_collision(self.get_current_maze(), x, y, radius)

    def find_path(self, start, goal):
        return MazeUtils.find_path(self.get_current_maze(), start, goal)

    def create_game_object(self, object_class, *args):
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == object_class.SYMBOL:
                    if object_class in [Player, Enemy]:
                        return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
                    else:
                        return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            if object_class in [Player, Enemy]:
                return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
            else:
                return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
        
        return None

    def create_player(self, color):
        player = self.create_game_object(Player, CELL_SIZE // 2 - 1, PLAYER_SPEED, self.check_collision, color)
        return player

    def create_coins(self, num_coins):
        coins = []
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == ' ':
                    coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return coins

    def create_enemy(self):
        enemy = self.create_game_object(Enemy, CELL_SIZE // 2 - 1, ENEMY_SPEED, self.find_path)
        return enemy

    def create_star(self):
        return self.create_game_object(Star, CELL_SIZE // 2)

    def create_diamonds(self):
        diamonds = []
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == 'D':
                    diamonds.append(Diamond(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return diamonds

    def next_level(self):
        self.level_manager.next_level()
        self.init_game_objects()

    def draw_score_area(self, screen):
        pygame.draw.rect(screen, LIGHT_GREEN, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(midleft=(10, SCORE_AREA_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        level_text = self.font.render(f"Level: {self.level_manager.get_current_level().level_number}", True, BLACK)
        level_rect = level_text.get_rect(midright=(WIDTH - 10, SCORE_AREA_HEIGHT // 2))
        screen.blit(level_text, level_rect)

        # Add level title
        current_level = self.level_manager.get_current_level()
        if current_level.title:
            title_text = self.title_font.render(current_level.title, True, BLACK)
            title_rect = title_text.get_rect(center=(WIDTH // 2, SCORE_AREA_HEIGHT // 2))
            screen.blit(title_text, title_rect)

    def draw_gradient_background(self, screen):
        color1 = (0, 0, 0)  # Start color (black)
        color2 = (0, 0, 255)  # End color (blue)
        for y in range(HEIGHT):
            color = (
                color1[0] + (color2[0] - color1[0]) * y // HEIGHT,
                color1[1] + (color2[1] - color1[1]) * y // HEIGHT,
                color1[2] + (color2[2] - color1[2]) * y // HEIGHT,
            )
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    def render_maze(self, screen):
        for y, row in enumerate(self.get_current_maze()):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == 'S' or cell == '*' or cell == 'D':
                    pygame.draw.rect(screen, WHITE, (x * CELL_SIZE + self.game.offset_x, y * CELL_SIZE + self.game.offset_y, CELL_SIZE, CELL_SIZE))

    def render_game_objects(self, screen, interpolation):
        for coin in self.coins:
            coin.draw(screen, self.game.offset_x, self.game.offset_y)

        if self.enemy:
            interpolated_x = self.enemy.x + (self.enemy.dx * interpolation)
            interpolated_y = self.enemy.y + (self.enemy.dy * interpolation)
            self.enemy.draw(screen, self.game.offset_x, self.game.offset_y, interpolated_x, interpolated_y)
            if not self.enemy.should_chase():
                countdown = int(self.enemy.chase_delay - (time.time() - self.enemy.start_time))
                countdown_text = self.font.render(f"Chase starts in: {countdown} seconds", True, RED)
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                screen.blit(countdown_text, countdown_rect)

        if self.player:
            interpolated_x = self.player.x + (self.player.dx * interpolation)
            interpolated_y = self.player.y + (self.player.dy * interpolation)
            self.player.draw(screen, self.game.offset_x, self.game.offset_y, interpolated_x, interpolated_y)

        if self.star:
            self.star.draw(screen, self.game.offset_x, self.game.offset_y)

        for diamond in self.diamonds:
            diamond.draw(screen, self.game.offset_x, self.game.offset_y)

    def draw_ui(self, screen):
        if self.state == GameState.PLAYING:
            instruction_text = "Press ESC to pause"
        elif self.state == GameState.PAUSED:
            instruction_text = "Press ESC to resume, X to exit"
        elif self.state == GameState.GAME_OVER:
            instruction_text = "Press ESC to return to menu"
        elif self.state == GameState.LEVEL_COMPLETE:
            instruction_text = "Press N for next level, ESC for menu"
        
        text = self.font.render(instruction_text, True, WHITE)
        text_rect = text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        screen.blit(text, text_rect)

    def collect_coins(self):
        player_rect = pygame.Rect(self.player.x - self.player.radius, 
                                  self.player.y - self.player.radius,  
                                  self.player.radius * 2, 
                                  self.player.radius * 2)
        
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin.x - coin.radius, 
                                    coin.y - coin.radius, 
                                    coin.radius * 2, 
                                    coin.radius * 2)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                self.score += 10
        
        if self.star:
            star_rect = pygame.Rect(self.star.x - self.star.radius, 
                                    self.star.y - self.star.radius, 
                                    self.star.radius * 2, 
                                    self.star.radius * 2)
            if player_rect.colliderect(star_rect):
                self.state = GameState.LEVEL_COMPLETE
                star_x, star_y = int(self.star.x // CELL_SIZE), int(self.star.y // CELL_SIZE)
                self.get_current_maze()[star_y][star_x] = ' '
                self.star = None
                self.game.play_star_consume_sound()  # Add this line to play the sound

        for diamond in self.diamonds[:]:
            diamond_rect = pygame.Rect(diamond.x - diamond.radius, 
                                       diamond.y - diamond.radius, 
                                       diamond.radius * 2, 
                                       diamond.radius * 2)
            if player_rect.colliderect(diamond_rect):
                diamond_x, diamond_y = int(diamond.x // CELL_SIZE), int(diamond.y // CELL_SIZE)
                self.get_current_maze()[diamond_y][diamond_x] = ' '
                self.diamonds.remove(diamond)
                self.score += 10000

    def check_enemy_collision(self):
        if self.enemy:
            player_rect = pygame.Rect(self.player.x - self.player.radius, 
                                      self.player.y - self.player.radius,
                                      self.player.radius * 2, 
                                      self.player.radius * 2)
            enemy_rect = pygame.Rect(self.enemy.x - self.enemy.radius, 
                                     self.enemy.y - self.enemy.radius,
                                     self.enemy.radius * 2, 
                                     self.enemy.radius * 2)
            if player_rect.colliderect(enemy_rect):
                self.state = GameState.GAME_OVER
                self.game.play_game_over_sound()

    def check_level_complete(self):
        if not self.coins and not self.star and not self.diamonds:
            self.state = GameState.LEVEL_COMPLETE

        # Check if we've completed all levels
        if self.state == GameState.LEVEL_COMPLETE and self.level_manager.current_level_index == len(self.level_manager.levels) - 1:
            self.level_manager.current_level_index = 0
            self.init_game_objects()

    def handle_player_input(self, event):
        if event.key == pygame.K_RIGHT:
            self.player.set_direction((1, 0))
        elif event.key == pygame.K_LEFT:
            self.player.set_direction((-1, 0))
        elif event.key == pygame.K_DOWN:
            self.player.set_direction((0, 1))
        elif event.key == pygame.K_UP:
            self.player.set_direction((0, -1))

    def render_pause_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))
        
        pause_text = self.title_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_text, pause_rect)

    def render_game_over_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.title_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)

    def render_level_complete_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))
        
        complete_text = self.title_font.render("LEVEL COMPLETE!", True, GOLD)
        complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(complete_text, complete_rect)

        next_level_text = self.font.render("Press N for next level", True, WHITE)
        next_rect = next_level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(next_level_text, next_rect)
