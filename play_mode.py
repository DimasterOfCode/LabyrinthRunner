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
    LEVEL_START = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()

class PlayMode(GameMode):
    def __init__(self, game, level_manager):
        super().__init__(game)
        self.level_manager = level_manager
        self.player = None
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.state = GameState.LEVEL_START
        self.level_start_time = 0
        self.LEVEL_START_DELAY = 2000  # 2 seconds delay
        self.remaining_time = 0

    def start_level(self):
        current_level = self.level_manager.get_current_level()
        # Find starting position in maze
        start_pos = self.find_start_position(current_level.maze)
        if start_pos is None:
            # If no start position found, use a default position
            start_pos = (CELL_SIZE * 1.5, CELL_SIZE * 1.5)
        
        # Get customization settings
        customization_mode = self.game.modes["runner_customization"]
        player_color = customization_mode.get_player_color()
        player_face = customization_mode.current_face
        trail_color = customization_mode.get_trail_color()
        
        # Create player with the selected face type and trail color
        self.player = Player(
            x=start_pos[0],
            y=start_pos[1],
            radius=PLAYER_RADIUS,
            speed=PLAYER_SPEED,
            collision_checker=self.check_collision,
            color=player_color,
            face_type=player_face,
            trail_color=trail_color
        )
        
        # Reset all game objects
        self.enemy = self.create_enemy()
        self.star = self.create_star()
        self.diamonds = self.create_diamonds()
        self.coins = self.create_coins(0)
        self.score = 0
        self.state = GameState.LEVEL_START
        self.level_start_time = pygame.time.get_ticks()

    def find_start_position(self, maze):
        """Find the starting position marked with 'S' in the maze"""
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 'S':
                    return (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
        return None

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
        if self.player is None:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update camera position to follow player
        self.update_camera()
        
        if self.state == GameState.LEVEL_START:
            self.remaining_time = max(0, (self.level_start_time + self.LEVEL_START_DELAY - current_time) // 1000)
            if current_time - self.level_start_time > self.LEVEL_START_DELAY:
                self.state = GameState.PLAYING
        elif self.state == GameState.PLAYING:
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
        screen.fill((0, 0, 0))
        
        # Draw the base game elements
        self.render_maze(screen)
        self.render_game_objects(screen, interpolation)
        self.draw_score_area(screen)
        
        # Draw appropriate overlay based on game state
        if self.state == GameState.LEVEL_START:
            self.render_level_start_overlay(screen)
        elif self.state == GameState.PAUSED:
            self.render_pause_overlay(screen)
        elif self.state == GameState.GAME_OVER:
            self.render_game_over_overlay(screen)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.render_level_complete_overlay(screen)
        
        # Always draw UI on top
        self.draw_ui(screen)

    def render_game_elements(self, screen, interpolation):
        screen.fill((0, 0, 0))
        self.render_maze(screen)
        self.render_game_objects(screen, interpolation)

    def render_ui_elements(self, screen):
        self.draw_score_area(screen)
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
        
        # Add zoom controls
        if event.type == pygame.MOUSEWHEEL:
            # Zoom in/out with mouse wheel
            self.game.target_zoom = max(0.5, min(2.0, self.game.target_zoom + event.y * 0.1))

    def check_collision(self, x, y, radius):
        return MazeUtils.check_collision(self.get_current_maze(), x, y, radius)

    def find_path(self, start, goal):
        return MazeUtils.find_path(self.get_current_maze(), start, goal)

    def create_game_object(self, object_class, *args):
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == object_class.SYMBOL:
                    # Center the object in the cell
                    obj_x = x * CELL_SIZE + (CELL_SIZE // 2)
                    obj_y = y * CELL_SIZE + (CELL_SIZE // 2)
                    if object_class in [Player, Enemy]:
                        return object_class(obj_x, obj_y, *args)
                    else:
                        return object_class(obj_x, obj_y, *args)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) 
                       for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            # Center the object in the cell
            obj_x = x * CELL_SIZE + (CELL_SIZE // 2)
            obj_y = y * CELL_SIZE + (CELL_SIZE // 2)
            if object_class in [Player, Enemy]:
                return object_class(obj_x, obj_y, *args)
            else:
                return object_class(obj_x, obj_y, *args)
        
        return None

    def create_player(self, color):
        player = self.create_game_object(Player, PLAYER_RADIUS, PLAYER_SPEED, self.check_collision, color)
        return player

    def create_coins(self, num_coins):
        coins = []
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == ' ':
                    # Center the coin in the cell
                    coin_x = x * CELL_SIZE + (CELL_SIZE // 2)
                    coin_y = y * CELL_SIZE + (CELL_SIZE // 2)
                    coins.append(Coin(coin_x, coin_y))
        return coins

    def create_enemy(self):
        enemy = self.create_game_object(Enemy, CELL_SIZE // 2 - 1, ENEMY_SPEED, self.find_path)
        if enemy is None:
            # If no 'E' symbol found, place the enemy at a random empty cell
            empty_cells = [(x, y) for y, row in enumerate(self.get_current_maze()) 
                           for x, cell in enumerate(row) if cell == ' ']
            if empty_cells:
                x, y = random.choice(empty_cells)
                # Center the enemy in the cell
                enemy_x = x * CELL_SIZE + (CELL_SIZE // 2)
                enemy_y = y * CELL_SIZE + (CELL_SIZE // 2)
                enemy = Enemy(enemy_x, enemy_y, 
                              CELL_SIZE // 2 - 1, ENEMY_SPEED, self.find_path)
        return enemy

    def create_star(self):
        return self.create_game_object(Star, CELL_SIZE // 2)

    def create_diamonds(self):
        diamonds = []
        current_maze = self.get_current_maze()
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == 'D':
                    # Center the diamond in the cell
                    diamond_x = x * CELL_SIZE + (CELL_SIZE // 2)
                    diamond_y = y * CELL_SIZE + (CELL_SIZE // 2)
                    diamonds.append(Diamond(diamond_x, diamond_y))
        return diamonds

    def next_level(self):
        self.level_manager.next_level()
        self.start_level()

    def draw_score_area(self, screen):
        pygame.draw.rect(screen, THEME_PRIMARY, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(screen, THEME_SECONDARY, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        score_text = self.font.render(f"Score: {self.score}", True, THEME_TEXT)
        score_rect = score_text.get_rect(midleft=(10, SCORE_AREA_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        level_text = self.font.render(f"Level: {self.level_manager.get_current_level().level_number}", True, THEME_TEXT)
        level_rect = level_text.get_rect(midright=(WIDTH - 10, SCORE_AREA_HEIGHT // 2))
        screen.blit(level_text, level_rect)

        # Add level title
        current_level = self.level_manager.get_current_level()
        if current_level.title:
            title_text = self.title_font.render(current_level.title, True, THEME_TEXT)
            title_rect = title_text.get_rect(center=(WIDTH // 2, SCORE_AREA_HEIGHT // 2))
            screen.blit(title_text, title_rect)

    def render_maze(self, screen):
        current_maze = self.get_current_maze()
        
        # Calculate visible range of cells based on camera position and zoom
        start_x = max(0, int(self.game.camera_x // CELL_SIZE))
        start_y = max(0, int(self.game.camera_y // CELL_SIZE))
        end_x = min(MAZE_WIDTH, int((self.game.camera_x + self.game.viewport_width) // CELL_SIZE) + 1)
        end_y = min(MAZE_HEIGHT, int((self.game.camera_y + self.game.viewport_height) // CELL_SIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                cell = current_maze[y][x]
                if cell == 'X':  # Add wall rendering
                    screen_x = (x * CELL_SIZE - self.game.camera_x) * self.game.zoom
                    screen_y = (y * CELL_SIZE - self.game.camera_y) * self.game.zoom + SCORE_AREA_HEIGHT
                    cell_size = CELL_SIZE * self.game.zoom
                    pygame.draw.rect(screen, BLACK, (screen_x, screen_y, cell_size, cell_size))
                elif cell in [' ', 'S', '*', 'D']:
                    screen_x = (x * CELL_SIZE - self.game.camera_x) * self.game.zoom
                    screen_y = (y * CELL_SIZE - self.game.camera_y) * self.game.zoom + SCORE_AREA_HEIGHT
                    cell_size = CELL_SIZE * self.game.zoom
                    pygame.draw.rect(screen, WHITE, (screen_x, screen_y, cell_size, cell_size))

    def render_game_objects(self, screen, interpolation):
        for coin in self.coins:
            coin.draw(screen, self.game)

        if self.enemy:
            interpolated_x = self.enemy.x + (self.enemy.dx * interpolation)
            interpolated_y = self.enemy.y + (self.enemy.dy * interpolation)
            self.enemy.draw(screen, self.game, interpolated_x, interpolated_y)

        if self.player:
            interpolated_x = self.player.x + (self.player.dx * interpolation)
            interpolated_y = self.player.y + (self.player.dy * interpolation)
            self.player.draw(screen, self.game, interpolated_x, interpolated_y)

        if self.star:
            self.star.draw(screen, self.game)

        for diamond in self.diamonds:
            diamond.draw(screen, self.game)

    def draw_ui(self, screen):
        if self.state == GameState.PLAYING:
            instruction_text = "Press ESC to pause"
        elif self.state == GameState.PAUSED:
            instruction_text = "Press ESC to resume, X to exit"
        elif self.state == GameState.GAME_OVER:
            instruction_text = "Press ESC to return to menu"
        elif self.state == GameState.LEVEL_COMPLETE:
            instruction_text = "Press N for next level, ESC for menu"
        else:
            instruction_text = ""  # No text for LEVEL_START or unexpected states

        if instruction_text:
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
                self.star = None
                self.game.play_star_consume_sound()

        for diamond in self.diamonds[:]:
            diamond_rect = pygame.Rect(diamond.x - diamond.radius, 
                                       diamond.y - diamond.radius, 
                                       diamond.radius * 2, 
                                       diamond.radius * 2)
            if player_rect.colliderect(diamond_rect):
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

        # Update the score for the current level
        current_level_number = self.level_manager.get_current_level().level_number
        self.game.update_level_score(current_level_number, self.score)

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
        overlay.fill((*THEME_BACKGROUND[:3], 150))  # Semi-transparent background
        screen.blit(overlay, (0, 0))
        
        pause_text = self.title_font.render("PAUSED", True, THEME_TEXT)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_text, pause_rect)

    def render_game_over_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*THEME_BACKGROUND[:3], 150))  # Semi-transparent background
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.title_font.render("GAME OVER", True, THEME_ACCENT)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)

    def render_level_complete_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*THEME_BACKGROUND[:3], 150))  # Semi-transparent background
        screen.blit(overlay, (0, 0))
        
        complete_text = self.title_font.render("LEVEL COMPLETE!", True, THEME_ACCENT)
        complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(complete_text, complete_rect)

        next_level_text = self.font.render("Press N for next level", True, THEME_TEXT)
        next_rect = next_level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(next_level_text, next_rect)

    def render_level_start_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*THEME_BACKGROUND[:3], 150))  # Semi-transparent background
        screen.blit(overlay, (0, 0))
        
        level_text = self.title_font.render(f"Level {self.level_manager.get_current_level().level_number}", True, THEME_TEXT)
        level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(level_text, level_rect)

        if self.level_manager.get_current_level().title:
            title_text = self.font.render(self.level_manager.get_current_level().title, True, THEME_TEXT)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(title_text, title_rect)

        # Add countdown display
        countdown_text = self.title_font.render(str(self.remaining_time), True, THEME_ACCENT)
        countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(countdown_text, countdown_rect)

        ready_text = self.font.render("Get ready!", True, THEME_TEXT)
        ready_rect = ready_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(ready_text, ready_rect)

    def update_camera(self):
        # Keep player centered by setting camera directly to player position minus half screen
        target_x = self.player.x - (self.game.viewport_width / 2)
        target_y = self.player.y - (self.game.viewport_height / 2)
        
        # Update camera position immediately instead of smoothly
        self.game.camera_x = target_x
        self.game.camera_y = target_y

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
