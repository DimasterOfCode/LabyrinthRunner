import pygame
import sys
import random
from collections import deque
import time
import json
import os
import pygame.gfxdraw

# Constants
FPS = 60
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 20
MAZE_WIDTH, MAZE_HEIGHT = 40, 30
SCORE_AREA_HEIGHT = 40
ENEMY_SPEED = CELL_SIZE // 20
PLAYER_SPEED = CELL_SIZE // 4
ESCAPE_ROUTES = max(100, MAZE_WIDTH // 10)
DEV_MODE = True
ENEMY_CHASE_DELAY = 2
COIN_RADIUS = CELL_SIZE // 7  # New constant for coin radius

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (200, 200, 0)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)  # New color for diamonds
COIN_COLOR = YELLOW  # New constant for coin color

# New base classes without ABC
class GameObject:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen, offset_x, offset_y):
        raise NotImplementedError("Subclass must implement abstract method")

class MovableObject(GameObject):
    def __init__(self, x, y, radius, speed):
        super().__init__(x, y, radius)
        self.speed = speed

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

# Refactored game objects
class Player(MovableObject):
    SYMBOL = 'S'
    def __init__(self, game, x, y, radius, speed):
        super().__init__(x, y, radius, speed)
        self.game = game
        self.direction = None

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, LIGHT_BROWN, (int(self.x + offset_x), int(self.y + offset_y)), self.radius)
        eye_radius = max(2, self.radius // 5)
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset + offset_x), int(self.y - eye_offset + offset_y)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset + offset_x), int(self.y - eye_offset + offset_y)), eye_radius)
        smile_rect = (int(self.x - self.radius // 2 + offset_x), int(self.y + offset_y), self.radius, self.radius // 2)
        pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, max(1, self.radius // 5))

    def set_direction(self, direction):
        if self.direction is None:
            self.direction = direction

    def update(self):
        if self.direction:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not self.game.check_collision(new_x, new_y):
                self.move(dx, dy)
            else:
                self.direction = None

class Coin(GameObject):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, COIN_COLOR, (self.x + offset_x, self.y + offset_y), self.radius)

class Enemy(MovableObject):
    SYMBOL = 'E'
    def __init__(self, game, x, y, radius, speed):
        super().__init__(x, y, radius, speed)
        self.game = game
        self.path = []
        self.start_time = time.time()
        self.chase_delay = ENEMY_CHASE_DELAY

    def move_along_path(self):
        if self.path:
            target_x, target_y = self.path[0]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5
            
            if distance < self.speed:
                self.x, self.y = self.path.pop(0)
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, RED, (int(self.x + offset_x), int(self.y + offset_y)), self.radius)

    def should_chase(self):
        return time.time() - self.start_time >= self.chase_delay

class Star(GameObject):
    SYMBOL = '*'
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen, offset_x, offset_y):
        # Draw white background circle
        pygame.draw.rect(screen, WHITE, (int(self.x + offset_x - self.radius), int(self.y + offset_y - self.radius), self.radius * 2, self.radius * 2))
        
        # Draw star
        pygame.draw.polygon(screen, GOLD, [
            (self.x + offset_x, self.y - self.radius + offset_y),
            (self.x + self.radius * 0.3 + offset_x, self.y + self.radius * 0.4 + offset_y),
            (self.x + self.radius + offset_x, self.y + self.radius * 0.4 + offset_y),
            (self.x + self.radius * 0.5 + offset_x, self.y + self.radius + offset_y),
            (self.x + self.radius * 0.7 + offset_x, self.y + self.radius * 1.6 + offset_y),
            (self.x + offset_x, self.y + self.radius * 1.2 + offset_y),
            (self.x - self.radius * 0.7 + offset_x, self.y + self.radius * 1.6 + offset_y),
            (self.x - self.radius * 0.5 + offset_x, self.y + self.radius + offset_y),
            (self.x - self.radius + offset_x, self.y + self.radius * 0.4 + offset_y),
            (self.x - self.radius * 0.3 + offset_x, self.y + self.radius * 0.4 + offset_y),
        ])

class Diamond(GameObject):
    SYMBOL = 'D'
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = CELL_SIZE // 2

    def draw(self, screen, offset_x, offset_y):
        # Draw white background circle
        pygame.draw.rect(screen, WHITE, (int(self.x + offset_x - self.radius), int(self.y + offset_y - self.radius), self.radius * 2, self.radius * 2))
        
        # Draw diamond
        points = [
            (self.x + offset_x, self.y - self.radius + offset_y),
            (self.x + self.radius + offset_x, self.y + offset_y),
            (self.x + offset_x, self.y + self.radius + offset_y),
            (self.x - self.radius + offset_x, self.y + offset_y),
        ]
        pygame.draw.polygon(screen, CYAN, points)


class Level:
    def __init__(self, maze, level_number):
        self.maze = maze
        self.level_number = level_number


class GameRenderer:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        self.game.screen.fill(GREEN)
        
        if self.game.state == "menu":
            self.game.menu.draw(self.game.screen)
        elif self.game.state == "play":
            self.draw_play_state()
        elif self.game.state == "level_editor":
            self.draw_level_editor()

    def draw_play_state(self):
        self.draw_score_area()
        self.draw_maze()
        self.draw_game_objects()
        self.draw_game_state()
        self.draw_ui()

    def draw_score_area(self):
        pygame.draw.rect(self.game.screen, LIGHT_GREEN, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(self.game.screen, BLACK, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        score_text = self.font.render(f"Score: {self.game.score}", True, BLACK)
        score_rect = score_text.get_rect(midleft=(10, SCORE_AREA_HEIGHT // 2))
        self.game.screen.blit(score_text, score_rect)

        level_text = self.font.render(f"Level: {self.game.level_manager.get_current_level().level_number}", True, BLACK)
        level_rect = level_text.get_rect(midright=(WIDTH - 10, SCORE_AREA_HEIGHT // 2))
        self.game.screen.blit(level_text, level_rect)

    def draw_maze(self):
        for y, row in enumerate(self.game.level_manager.get_current_level().maze):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == 'S' or cell == '*' or cell == 'D':
                    pygame.draw.rect(self.game.screen, WHITE, (x * CELL_SIZE + self.game.offset_x, y * CELL_SIZE + self.game.offset_y, CELL_SIZE, CELL_SIZE))

    def draw_game_objects(self):
        for coin in self.game.coins:
            coin.draw(self.game.screen, self.game.offset_x, self.game.offset_y)

        if self.game.enemy:
            self.game.enemy.draw(self.game.screen, self.game.offset_x, self.game.offset_y)
            if not self.game.enemy.should_chase():
                countdown = int(self.game.enemy.chase_delay - (time.time() - self.game.enemy.start_time))
                countdown_text = self.font.render(f"Chase starts in: {countdown}", True, RED)
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                self.game.screen.blit(countdown_text, countdown_rect)

        if self.game.player:
            self.game.player.draw(self.game.screen, self.game.offset_x, self.game.offset_y)

        if self.game.star:
            self.game.star.draw(self.game.screen, self.game.offset_x, self.game.offset_y)

        for diamond in self.game.diamonds:
            diamond.draw(self.game.screen, self.game.offset_x, self.game.offset_y)

    def draw_game_state(self):
        if self.game.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.game.screen.blit(game_over_text, game_over_rect)

        if self.game.level_complete:
            level_complete_text = self.font.render("Level Complete! Press N for next level", True, GOLD)
            level_complete_rect = level_complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.game.screen.blit(level_complete_text, level_complete_rect)

    def draw_ui(self):
        quit_text = self.font.render("Press ESC to return to menu", True, BLACK)
        quit_rect = quit_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.game.screen.blit(quit_text, quit_rect)

    def draw_level_editor(self):
        for y, row in enumerate(self.game.level_manager.get_current_level().maze):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE + self.game.offset_x, y * CELL_SIZE + self.game.offset_y, CELL_SIZE, CELL_SIZE)
                if cell == 'X':
                    pygame.draw.rect(self.game.screen, BLACK, rect)
                elif cell == ' ':
                    pygame.draw.rect(self.game.screen, WHITE, rect)
                elif cell == 'S':
                    pygame.draw.rect(self.game.screen, LIGHT_BROWN, rect)
                elif cell == 'E':
                    pygame.draw.rect(self.game.screen, RED, rect)
                elif cell == '*':
                    pygame.draw.rect(self.game.screen, GOLD, rect)
                elif cell == 'D':
                    pygame.draw.rect(self.game.screen, CYAN, rect)
        
        dev_text = self.font.render("Dev Mode: Press H for help", True, BLACK)
        dev_rect = dev_text.get_rect(midtop=(WIDTH // 2, 10))
        self.game.screen.blit(dev_text, dev_rect)

        if self.game.show_help:
            self.draw_help_overlay()

        quit_text = self.font.render("Press ESC to return to menu", True, BLACK)
        quit_rect = quit_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.game.screen.blit(quit_text, quit_rect)

    def draw_help_overlay(self):
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

        self.game.screen.blit(overlay, (0, 0))

class GameLogic:
    def __init__(self, game):
        self.game = game

    def update(self):
        if self.game.state == "play":
            if not self.game.game_over and not self.game.is_dev_mode and not self.game.level_complete:
                self.game.player.update()
                self.update_enemy()
                self.collect_coins()
                self.check_enemy_collision()
                self.check_level_complete()

    def update_enemy(self):
        if self.game.enemy:
            if self.game.enemy.should_chase():
                if not self.game.enemy.path:
                    start = (int(self.game.enemy.x // CELL_SIZE), int(self.game.enemy.y // CELL_SIZE))
                    goal = (int(self.game.player.x // CELL_SIZE), int(self.game.player.y // CELL_SIZE))
                    path = self.game.find_path(start, goal)
                    if path:
                        self.game.enemy.path = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for x, y in path[1:]]
                
                self.game.enemy.move_along_path()

    def collect_coins(self):
        player_rect = pygame.Rect(self.game.player.x - self.game.player.radius, 
                                  self.game.player.y - self.game.player.radius,  
                                  self.game.player.radius * 2, 
                                  self.game.player.radius * 2)
        
        for coin in self.game.coins[:]:
            coin_rect = pygame.Rect(coin.x - coin.radius, 
                                    coin.y - coin.radius, 
                                    coin.radius * 2, 
                                    coin.radius * 2)
            if player_rect.colliderect(coin_rect):
                self.game.coins.remove(coin)
                self.game.score += 10
        
        if self.game.star:
            star_rect = pygame.Rect(self.game.star.x - self.game.star.radius, 
                                    self.game.star.y - self.game.star.radius, 
                                    self.game.star.radius * 2, 
                                    self.game.star.radius * 2)
            if player_rect.colliderect(star_rect):
                self.game.level_complete = True
                star_x, star_y = int(self.game.star.x // CELL_SIZE), int(self.game.star.y // CELL_SIZE)
                self.game.level_manager.get_current_level().maze[star_y][star_x] = ' '
                self.game.star = None

        for diamond in self.game.diamonds[:]:
            diamond_rect = pygame.Rect(diamond.x - diamond.radius, 
                                       diamond.y - diamond.radius, 
                                       diamond.radius * 2, 
                                       diamond.radius * 2)
            if player_rect.colliderect(diamond_rect):
                diamond_x, diamond_y = int(diamond.x // CELL_SIZE), int(diamond.y // CELL_SIZE)
                self.game.level_manager.get_current_level().maze[diamond_y][diamond_x] = ' '
                self.game.diamonds.remove(diamond)
                self.game.score += 10000

    def check_enemy_collision(self):
        if self.game.enemy:
            player_rect = pygame.Rect(self.game.player.x - self.game.player.radius, 
                                      self.game.player.y - self.game.player.radius,
                                      self.game.player.radius * 2, 
                                      self.game.player.radius * 2)
            enemy_rect = pygame.Rect(self.game.enemy.x - self.game.enemy.radius, 
                                     self.game.enemy.y - self.game.enemy.radius,
                                     self.game.enemy.radius * 2, 
                                     self.game.enemy.radius * 2)
            if player_rect.colliderect(enemy_rect):
                self.game.game_over = True

    def check_level_complete(self):
        if not self.game.coins and not self.game.star and not self.game.diamonds:
            self.game.level_complete = True

        # Check if we've completed all levels
        if self.game.level_complete and self.game.level_manager.current_level_index == len(self.game.level_manager.levels) - 1:
            self.game.level_manager.current_level_index = 0
            self.game.init_game_objects()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Circle Maze Game")
        self.clock = pygame.time.Clock()
        
        self.level_manager = LevelManager("levels.json")
        self.dev_mode = DevMode(self)
        self.is_dev_mode = False
        self.show_help = False
        self.is_drawing = False

        self.load_or_generate_levels()
        self.init_game_objects()

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT
        self.running = True
        
        self.state = "menu"
        self.menu = Menu(self)
        self.renderer = GameRenderer(self)
        self.logic = GameLogic(self)

    def load_or_generate_levels(self):
        if os.path.exists(self.level_manager.levels_file):
            self.level_manager.load_levels_from_file()
        else:
            print("No levels file found. Entering Dev Mode.")
            self.is_dev_mode = True
            self.dev_mode.init_dev_mode()

    def init_game_objects(self):
        self.player = self.create_player()
        self.enemy = self.create_enemy()
        self.star = self.create_star()
        self.diamonds = self.create_diamonds()
        self.coins = self.create_coins(0)
        self.score = 0
        self.game_over = False
        self.level_complete = False

    def create_game_object(self, object_class, *args):
        current_maze = self.level_manager.get_current_level().maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == object_class.SYMBOL:
                    if object_class in [Player, Enemy]:
                        return object_class(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
                    else:
                        return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            if object_class in [Player, Enemy]:
                return object_class(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
            else:
                return object_class(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, *args)
        
        return None

    def create_player(self):
        return self.create_game_object(Player, CELL_SIZE // 2 - 1, PLAYER_SPEED)

    def create_coins(self, num_coins):
        coins = []
        current_maze = self.level_manager.get_current_level().maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == ' ':
                    coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return coins

    def create_enemy(self):
        return self.create_game_object(Enemy, CELL_SIZE // 2 - 1, ENEMY_SPEED)

    def create_star(self):
        return self.create_game_object(Star, CELL_SIZE // 2)

    def create_diamonds(self):
        diamonds = []
        current_maze = self.level_manager.get_current_level().maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == 'D':
                    diamonds.append(Diamond(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return diamonds

    def find_path(self, start, goal):
        queue = deque([[start]])
        visited = set([start])
        
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            
            if (x, y) == goal:
                return path
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                    self.level_manager.get_current_level().maze[next_y][next_x] != 'X' and (next_x, next_y) not in visited):
                    queue.append(path + [(next_x, next_y)])
                    visited.add((next_x, next_y))
        
        return None

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.logic.update()
            self.renderer.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "menu":
                self.menu.handle_event(event)
            else:
                self.handle_input(event)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.return_to_menu()
            elif self.is_dev_mode:
                self.dev_mode.handle_dev_mode_input(event)
            elif self.level_complete:
                if event.key == pygame.K_n:
                    self.next_level()
            else:
                self.handle_player_input(event)
        if event.type == pygame.KEYUP and self.is_dev_mode:
            self.dev_mode.selected_item = ' '  # Reset to empty space when key is released
        if self.is_dev_mode:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.is_drawing = True
                self.dev_mode.handle_input(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_drawing = False
            elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                self.dev_mode.handle_input(event.pos)

    def handle_player_input(self, event):
        if event.key == pygame.K_RIGHT:
            self.player.set_direction((1, 0))
        elif event.key == pygame.K_LEFT:
            self.player.set_direction((-1, 0))
        elif event.key == pygame.K_DOWN:
            self.player.set_direction((0, 1))
        elif event.key == pygame.K_UP:
            self.player.set_direction((0, -1))

    def save_current_level(self):
        self.level_manager.save_levels_to_file()
        print(f"Level {self.level_manager.get_current_level().level_number} saved")

    def toggle_dev_mode(self):
        self.is_dev_mode = not self.is_dev_mode
        if self.is_dev_mode:
            self.dev_mode.init_dev_mode()
        else:
            self.level_manager.load_levels_from_file()
        self.init_game_objects()

    def next_level(self):
        self.level_manager.next_level()
        self.init_game_objects()

    def prev_level(self):
        self.level_manager.prev_level()
        self.init_game_objects()

    def start_game(self):
        self.state = "play"
        self.init_game_objects()

    def start_level_editor(self):
        self.state = "level_editor"
        self.is_dev_mode = True
        self.dev_mode.init_dev_mode()

    def return_to_menu(self):
        self.state = "menu"
        self.is_dev_mode = False
        self.game_over = False
        self.level_complete = False
        self.show_help = False
        self.is_drawing = False
        # Reset the game objects
        self.init_game_objects()

    def check_collision(self, x, y):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                cell_x = int((x + dx * self.player.radius) // CELL_SIZE)
                cell_y = int((y + dy * self.player.radius) // CELL_SIZE)
                if (cell_x < 0 or cell_x >= MAZE_WIDTH or
                    cell_y < 0 or cell_y >= MAZE_HEIGHT or
                    self.level_manager.get_current_level().maze[cell_y][cell_x] == 'X'):
                    return True
        return False

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.options = ["Play", "Level Editor"]
        self.selected = 0

    def draw(self, screen):
        screen.fill((50, 50, 50))  # Dark gray background

        title = self.title_font.render("Circle Maze Game", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)

        for i, option in enumerate(self.options):
            color = GOLD if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            
            # Draw a rounded rectangle behind the text
            pygame.draw.rect(screen, GREEN, rect.inflate(20, 10), border_radius=10)
            pygame.draw.rect(screen, BLACK, rect.inflate(20, 10), 2, border_radius=10)
            
            screen.blit(text, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:
                    self.game.start_game()
                elif self.selected == 1:
                    self.game.start_level_editor()

class LevelManager:
    def __init__(self, levels_file):
        self.levels_file = levels_file
        self.levels = []
        self.current_level_index = 0

    def load_levels_from_file(self):
        with open(self.levels_file, 'r') as f:
            levels_data = json.load(f)
        self.levels = [Level(level_data["maze"], level_data["level_number"]) for level_data in levels_data]
        print(f"Levels loaded from {self.levels_file}")

    def save_levels_to_file(self):
        levels_data = [{"maze": level.maze, "level_number": level.level_number} for level in self.levels]
        with open(self.levels_file, 'w') as f:
            json.dump(levels_data, f)
        print(f"Levels saved to {self.levels_file}")

    def get_current_level(self):
        return self.levels[self.current_level_index]

    def next_level(self):
        self.current_level_index = (self.current_level_index + 1) % len(self.levels)
        return self.get_current_level()

    def prev_level(self):
        self.current_level_index = (self.current_level_index - 1) % len(self.levels)
        return self.get_current_level()

    def new_level(self):
        new_maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        self.levels.append(Level(new_maze, len(self.levels) + 1))
        self.current_level_index = len(self.levels) - 1
        return self.get_current_level()

class DevMode:
    def __init__(self, game):
        self.game = game
        self.selected_item = ' '

    def handle_input(self, pos):
        x = (pos[0] - self.game.offset_x) // CELL_SIZE
        y = (pos[1] - self.game.offset_y) // CELL_SIZE
        if 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT:
            if self.selected_item in ['S', 'E', '*']:
                self.remove_duplicate(self.selected_item, x, y)
            self.game.level_manager.get_current_level().maze[y][x] = self.selected_item

    def handle_dev_mode_input(self, event):
        if event.key == pygame.K_h:
            self.game.show_help = not self.game.show_help
        elif event.key == pygame.K_SPACE:
            self.game.save_current_level()
        elif event.key == pygame.K_e:
            self.erase_maze()
        elif event.key == pygame.K_n:
            self.game.level_manager.new_level()
        elif event.key == pygame.K_LEFTBRACKET:
            self.game.level_manager.prev_level()
        elif event.key == pygame.K_RIGHTBRACKET:
            self.game.level_manager.next_level()
        elif event.key == pygame.K_p:
            self.selected_item = 'S'  # Start/Player
        elif event.key == pygame.K_n:
            self.selected_item = 'E'  # Enemy
        elif event.key == pygame.K_s:
            self.selected_item = '*'  # Star
        elif event.key == pygame.K_m:
            self.selected_item = 'D'  # Diamond
        elif event.key == pygame.K_w:
            self.selected_item = 'X'  # Wall
        elif event.key == pygame.K_c:
            self.selected_item = ' '  # Clear/Empty

    def remove_duplicate(self, char, new_x, new_y):
        maze = self.game.level_manager.get_current_level().maze
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == char and (x != new_x or y != new_y):
                    maze[y][x] = ' '

    def erase_maze(self):
        self.game.level_manager.get_current_level().maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        print("Maze erased")

    def init_dev_mode(self):
        if not self.game.level_manager.levels:
            self.game.level_manager.levels.append(Level([['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)], 1))
        if 'S' not in [cell for row in self.game.level_manager.get_current_level().maze for cell in row]:
            self.game.level_manager.get_current_level().maze[1][1] = 'S'
        if 'E' not in [cell for row in self.game.level_manager.get_current_level().maze for cell in row]:
            self.game.level_manager.get_current_level().maze[MAZE_HEIGHT-2][MAZE_WIDTH-2] = 'E'
        self.game.init_game_objects()

if __name__ == "__main__":
    game = Game()
    game.run()
