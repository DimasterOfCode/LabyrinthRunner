import random
import time
import math

import pygame
import pygame.gfxdraw

from constants import *
from game_objects import *
from maze_utils import *


class GameMode: 
    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def render(self, screen):
        pass

    def handle_event(self, event):
        pass

class MenuMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.title = "Labyrinth Runner"  # Update the title here
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.buttons = [
            {"text": "Play", "action": lambda: self.game.set_mode("play")},
            {"text": "Level Editor", "action": lambda: self.game.set_mode("level_editor")},
            {"text": "Customize Runner", "action": lambda: self.game.set_mode("runner_customization")},
            {"text": "Quit", "action": lambda: setattr(self.game, 'running', False)}
        ]
        self.selected_button = 0
        self.animation_offset = 0
        self.animation_speed = 0.5

    def update(self):
        self.animation_offset = (self.animation_offset + self.animation_speed) % (2 * math.pi)

    def render(self, screen, interpolation):
        # Create gradient background
        for y in range(HEIGHT):
            color = self.lerp_color((20, 20, 50), (50, 50, 100), y / HEIGHT)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Draw animated circles
        for i in range(10):
            radius = 50 + 20 * math.sin(self.animation_offset + i * 0.5)
            x = WIDTH * (i + 1) / 11
            y = HEIGHT * (0.2 + 0.1 * math.sin(self.animation_offset + i * 0.7))
            pygame.gfxdraw.aacircle(screen, int(x), int(y), int(radius), (255, 255, 255, 50))

        # Draw title
        title = self.font.render(self.title, True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)

        # Draw buttons
        for i, button in enumerate(self.buttons):
            text = self.small_font.render(button["text"], True, (255, 255, 255))
            button_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            
            if i == self.selected_button:
                # Draw highlighted button
                pygame.draw.rect(screen, (100, 100, 255), button_rect.inflate(20, 10), border_radius=5)
            
            screen.blit(text, button_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                self.buttons[self.selected_button]["action"]()

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

class PlayMode(GameMode):
    def __init__(self, game, level_manager):
        super().__init__(game)
        self.level_manager = level_manager
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
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
        self.game_over = False
        self.level_complete = False

    def update(self):
        if not self.game_over and not self.level_complete:
            self.player.update()
            if self.enemy:
                self.enemy.update((self.player.x, self.player.y))
            self.collect_coins()
            self.check_enemy_collision()
            self.check_level_complete()

    def render(self, screen, interpolation):
        # Draw gradient background
        self.draw_gradient_background(screen)

        # Render maze and other game elements
        self.render_maze(screen)
        self.render_game_objects(screen, interpolation)
        self.draw_score_area(screen)
        self.draw_game_state(screen)
        self.draw_ui(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")
            elif self.level_complete:
                if event.key == pygame.K_n:
                    self.next_level()
            else:
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

    def draw_game_state(self, screen):
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)

        if self.level_complete:
            level_complete_text = self.font.render("Level Complete! Press N for next level", True, GOLD)
            level_complete_rect = level_complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(level_complete_text, level_complete_rect)

    def draw_ui(self, screen):
        quit_text = self.font.render("Press ESC to return to menu", True, BLACK)
        quit_rect = quit_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        screen.blit(quit_text, quit_rect)

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
                self.level_complete = True
                star_x, star_y = int(self.star.x // CELL_SIZE), int(self.star.y // CELL_SIZE)
                self.get_current_maze()[star_y][star_x] = ' '
                self.star = None

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
                self.game_over = True

    def check_level_complete(self):
        if not self.coins and not self.star and not self.diamonds:
            self.level_complete = True

        # Check if we've completed all levels
        if self.level_complete and self.level_manager.current_level_index == len(self.level_manager.levels) - 1:
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

class RunnerCustomizationMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.colors = [GOLD, RED, GREEN, BLUE, WHITE, CYAN, MAGENTA]
        self.color_index = 0

    def update(self):
        pass

    def render(self, screen, interpolation):
        screen.fill(BLACK)

        title = self.title_font.render("Runner Customization", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        screen.blit(title, title_rect)

        color_text = self.font.render("Press SPACE to change color", True, WHITE)
        color_rect = color_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(color_text, color_rect)

        # Draw example player
        pygame.draw.circle(screen, self.colors[self.color_index], (WIDTH // 2, HEIGHT // 2 + 50), CELL_SIZE // 2 - 1)

        back_text = self.font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(back_text, back_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.color_index = (self.color_index + 1) % len(self.colors)
            elif event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")

    def get_player_color(self):
        return self.colors[self.color_index]
 