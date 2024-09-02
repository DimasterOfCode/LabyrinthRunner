import pygame
import sys
import random
from collections import deque
import time
import json
import os

# Constants
FPS = 60
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 20
MAZE_WIDTH, MAZE_HEIGHT = 40, 30
SCORE_AREA_HEIGHT = 40
ENEMY_SPEED = CELL_SIZE // 6
PLAYER_SPEED = CELL_SIZE // 4
ESCAPE_ROUTES = max(100, MAZE_WIDTH // 10)
DEV_MODE = True
ENEMY_CHASE_DELAY = 2
COIN_RADIUS = CELL_SIZE // 5  # New constant for coin radius

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

# Game objects
class Player:
    def __init__(self, game, x, y, radius, speed):
        self.game = game
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
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

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, YELLOW, (self.x + offset_x, self.y + offset_y), self.radius)

class Enemy:
    def __init__(self, game, x, y, radius, speed):
        self.game = game
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
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

class Star:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen, offset_x, offset_y):
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

class Diamond:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = CELL_SIZE // 2

    def draw(self, screen, offset_x, offset_y):
        points = [
            (self.x + offset_x, self.y - self.radius + offset_y),
            (self.x + self.radius + offset_x, self.y + offset_y),
            (self.x + offset_x, self.y + self.radius + offset_y),
            (self.x - self.radius + offset_x, self.y + offset_y),
        ]
        pygame.draw.polygon(screen, CYAN, points)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Circle Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.level = 1
        self.dev_mode = False
        self.dev_maze = None
        self.dev_selected_item = ' '  # Default to empty space
        self.maze_file = "custom_maze.json"
        
        if os.path.exists(self.maze_file):
            self.load_maze_from_file()
        else:
            self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        
        self.player = self.create_player()
        if self.player is None:
            raise ValueError("Failed to create player")
        self.enemy = None
        self.star = None
        self.diamonds = []
        self.init_level()

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT
        self.game_over = False
        self.level_complete = False
        self.is_drawing = False  # New attribute to track if we're currently drawing

    def init_dev_mode(self):
        if self.dev_maze is None:
            self.dev_maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
            self.dev_maze[1][1] = 'S'
            self.dev_maze[MAZE_HEIGHT-2][MAZE_WIDTH-2] = 'E'
        self.coins = []
        self.enemy = self.create_enemy()
        self.star = None
        self.diamonds = []
        self.score = 0

    def init_level(self):
        self.coins = self.create_coins(0)
        self.enemy = self.create_enemy()
        self.star = self.create_star()
        self.diamonds = self.create_diamonds()
        self.score = 0

    def generate_maze(self, width, height):
        maze = [['X' for _ in range(width)] for _ in range(height)]
        
        def carve_path(x, y):
            maze[y][x] = ' '
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 'X':
                    maze[ny][nx] = ' '
                    return nx, ny
            return None

        x, y = random.randrange(1, width-1), random.randrange(1, height-1)
        maze[y][x] = 'S'
        
        while True:
            next_pos = carve_path(x, y)
            if next_pos is None:
                break
            x, y = next_pos
        
        return [''.join(row) for row in maze]

    def create_player(self):
        current_maze = self.dev_maze if self.dev_mode else self.maze
        for y, row in enumerate(current_maze):
            if 'S' in row:
                x = row.index('S')
                return Player(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, PLAYER_SPEED)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Player(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, PLAYER_SPEED)
        
        raise ValueError("No valid position found for the player")

    def create_coins(self, num_coins):
        coins = []
        current_maze = self.dev_maze if self.dev_mode else self.maze
        for y, row in enumerate(current_maze):
            for x, cell in enumerate(row):
                if cell == ' ':
                    coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return coins

    def create_enemy(self):
        current_maze = self.dev_maze if self.dev_mode else self.maze
        for y, row in enumerate(current_maze):
            if 'E' in row:
                x = row.index('E')
                return Enemy(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, ENEMY_SPEED)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Enemy(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, ENEMY_SPEED)
        
        return None

    def create_star(self):
        current_maze = self.dev_maze if self.dev_mode else self.maze
        for y, row in enumerate(current_maze):
            if '*' in row:
                x = row.index('*')
                return Star(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2)
        
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Star(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2)
        return None

    def create_diamonds(self):
        diamonds = []
        current_maze = self.dev_maze if self.dev_mode else self.maze
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
                    self.maze[next_y][next_x] != 'X' and (next_x, next_y) not in visited):
                    queue.append(path + [(next_x, next_y)])
                    visited.add((next_x, next_y))
        
        return None

    def update_enemy(self):
        if self.enemy:
            if self.enemy.should_chase():
                if not self.enemy.path:
                    start = (int(self.enemy.x // CELL_SIZE), int(self.enemy.y // CELL_SIZE))
                    goal = (int(self.player.x // CELL_SIZE), int(self.player.y // CELL_SIZE))
                    path = self.find_path(start, goal)
                    if path:
                        self.enemy.path = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for x, y in path[1:]]
                
                self.enemy.move_along_path()

    def check_collision(self, x, y):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                cell_x = int((x + dx * self.player.radius) // CELL_SIZE)
                cell_y = int((y + dy * self.player.radius) // CELL_SIZE)
                if (cell_x < 0 or cell_x >= MAZE_WIDTH or
                    cell_y < 0 or cell_y >= MAZE_HEIGHT or
                    self.maze[cell_y][cell_x] == 'X'):
                    return True
        return False

    def collect_coins(self):
        player_rect = pygame.Rect(self.player.x - self.player.radius, self.player.y - self.player.radius,  
                                  self.player.radius * 2, self.player.radius * 2)
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin.x - coin.radius, coin.y - coin.radius, 
                                    coin.radius * 2, coin.radius * 2)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                self.score += 10
        
        if self.star:
            star_rect = pygame.Rect(self.star.x - self.star.radius, self.star.y - self.star.radius, 
                                    self.star.radius * 2, self.star.radius * 2)
            if player_rect.colliderect(star_rect):
                self.level_complete = True
                self.star = None

        for diamond in self.diamonds[:]:
            diamond_rect = pygame.Rect(diamond.x - diamond.radius, diamond.y - diamond.radius, 
                                       diamond.radius * 2, diamond.radius * 2)
            if player_rect.colliderect(diamond_rect):
                self.diamonds.remove(diamond)
                self.score += 10000

    def next_level(self):
        self.level += 1
        self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = self.create_player()
        self.init_level()
        self.level_complete = False
        
        if self.enemy:
            self.enemy.start_time = time.time()

    def check_enemy_collision(self):
        player_rect = pygame.Rect(self.player.x - self.player.radius, self.player.y - self.player.radius,
                                  self.player.radius * 2, self.player.radius * 2)
        enemy_rect = pygame.Rect(self.enemy.x - self.enemy.radius, self.enemy.y - self.enemy.radius,
                                 self.enemy.radius * 2, self.enemy.radius * 2)
        if player_rect.colliderect(enemy_rect):
            self.game_over = True

    def handle_dev_mode_input(self, pos):
        x = (pos[0] - self.offset_x) // CELL_SIZE
        y = (pos[1] - self.offset_y) // CELL_SIZE
        if 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT:
            if self.dev_selected_item in ['S', 'E', '*']:
                self.remove_duplicate(self.dev_selected_item, x, y)
            self.dev_maze[y][x] = self.dev_selected_item

    def remove_duplicate(self, char, new_x, new_y):
        for y, row in enumerate(self.dev_maze):
            for x, cell in enumerate(row):
                if cell == char and (x != new_x or y != new_y):
                    self.dev_maze[y][x] = ' '

    def save_dev_maze(self):
        self.maze = [''.join(row) for row in self.dev_maze]
        self.dev_mode = False
        self.player = self.create_player()
        self.enemy = self.create_enemy()
        self.init_level()
        self.save_maze_to_file()

    def toggle_dev_mode(self):
        self.dev_mode = not self.dev_mode
        if self.dev_mode:
            self.init_dev_mode()
        else:
            self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
            self.init_level()
        self.player = self.create_player()
        self.enemy = self.create_enemy()

    def erase_dev_maze(self):
        self.dev_maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        print("Maze erased")

    def draw(self):
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, LIGHT_GREEN, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == 'S':
                    pygame.draw.rect(self.screen, WHITE, (x * CELL_SIZE + self.offset_x, y * CELL_SIZE + self.offset_y, CELL_SIZE, CELL_SIZE))

        for coin in self.coins:
            coin.draw(self.screen, self.offset_x, self.offset_y)

        if self.enemy:
            self.enemy.draw(self.screen, self.offset_x, self.offset_y)
            if not self.enemy.should_chase():
                countdown = int(self.enemy.chase_delay - (time.time() - self.enemy.start_time))
                countdown_text = self.font.render(f"Chase starts in: {countdown}", True, RED)
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                self.screen.blit(countdown_text, countdown_rect)

        if self.player:
            self.player.draw(self.screen, self.offset_x, self.offset_y)

        if self.star:
            self.star.draw(self.screen, self.offset_x, self.offset_y)

        for diamond in self.diamonds:
            diamond.draw(self.screen, self.offset_x, self.offset_y)

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(midleft=(10, SCORE_AREA_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        level_text = self.font.render(f"Level: {self.level}", True, BLACK)
        level_rect = level_text.get_rect(midright=(WIDTH - 10, SCORE_AREA_HEIGHT // 2))
        self.screen.blit(level_text, level_rect)

        if self.level_complete:
            level_complete_text = self.font.render("Level Complete! Press N for next level", True, GOLD)
            level_complete_rect = level_complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(level_complete_text, level_complete_rect)

        if self.dev_mode:
            for y, row in enumerate(self.dev_maze):
                for x, cell in enumerate(row):
                    rect = pygame.Rect(x * CELL_SIZE + self.offset_x, y * CELL_SIZE + self.offset_y, CELL_SIZE, CELL_SIZE)
                    if cell == 'X':
                        pygame.draw.rect(self.screen, BLACK, rect)
                    elif cell == ' ':
                        pygame.draw.rect(self.screen, WHITE, rect)
                    elif cell == 'S':
                        pygame.draw.rect(self.screen, LIGHT_BROWN, rect)
                    elif cell == 'E':
                        pygame.draw.rect(self.screen, RED, rect)
                    elif cell == '*':
                        pygame.draw.rect(self.screen, GOLD, rect)
                    elif cell == 'D':
                        pygame.draw.rect(self.screen, CYAN, rect)
            
            dev_text = self.font.render("Dev Mode: P-Player, N-Enemy, S-Star, M-Diamond, W-Wall, C-Clear, SPACE to save, L to load, ESC to exit", True, BLACK)
            dev_rect = dev_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
            self.screen.blit(dev_text, dev_rect)

            selected_text = self.font.render(f"Selected: {self.dev_selected_item if self.dev_selected_item != ' ' else 'Empty'}", True, BLACK)
            selected_rect = selected_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 40))
            self.screen.blit(selected_text, selected_rect)

            draw_text = self.font.render("Click and drag to draw", True, BLACK)
            draw_rect = draw_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 70))
            self.screen.blit(draw_text, draw_rect)
        else:
            dev_hint = self.font.render("Press D for Dev Mode, L to Load Maze", True, BLACK)
            dev_hint_rect = dev_hint.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
            self.screen.blit(dev_hint, dev_hint_rect)

    def save_maze_to_file(self):
        maze_data = {
            "maze": self.dev_maze,
            "level": self.level,
            "score": self.score
        }
        with open(self.maze_file, 'w') as f:
            json.dump(maze_data, f)
        print(f"Maze saved to {self.maze_file}")

    def load_maze_from_file(self):
        with open(self.maze_file, 'r') as f:
            maze_data = json.load(f)
        self.dev_maze = maze_data["maze"]
        self.level = maze_data["level"]
        self.score = maze_data["score"]
        self.maze = [''.join(row) for row in self.dev_maze]
        self.player = self.create_player()
        self.enemy = self.create_enemy()
        self.star = self.create_star()
        self.coins = self.create_coins(0)
        self.diamonds = self.create_diamonds()
        print(f"Maze loaded from {self.maze_file}")

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.dev_mode:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.is_drawing = True
                        self.handle_dev_mode_input(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.is_drawing = False
                    elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                        self.handle_dev_mode_input(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.toggle_dev_mode()
                    elif self.dev_mode:
                        if event.key == pygame.K_SPACE:
                            self.save_dev_maze()
                        elif event.key == pygame.K_e:
                            self.erase_dev_maze()
                        elif event.key == pygame.K_p:
                            self.dev_selected_item = 'S'  # Start/Player
                        elif event.key == pygame.K_n:
                            self.dev_selected_item = 'E'  # Enemy
                        elif event.key == pygame.K_s:
                            self.dev_selected_item = '*'  # Star
                        elif event.key == pygame.K_m:
                            self.dev_selected_item = 'D'  # Diamond
                        elif event.key == pygame.K_w:
                            self.dev_selected_item = 'X'  # Wall
                        elif event.key == pygame.K_c:
                            self.dev_selected_item = ' '  # Clear/Empty
                    elif event.key == pygame.K_l:
                        self.load_maze_from_file()
                    elif self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.__init__()
                    elif self.level_complete:
                        if event.key == pygame.K_n:
                            self.next_level()
                    else:
                        if event.key == pygame.K_RIGHT:
                            self.player.set_direction((1, 0))
                        elif event.key == pygame.K_LEFT:
                            self.player.set_direction((-1, 0))
                        elif event.key == pygame.K_DOWN:
                            self.player.set_direction((0, 1))
                        elif event.key == pygame.K_UP:
                            self.player.set_direction((0, -1))
                if event.type == pygame.KEYUP and self.dev_mode:
                    self.dev_selected_item = ' '  # Reset to empty space when key is released

            if not self.game_over and not self.dev_mode and not self.level_complete:
                self.player.update()
                self.update_enemy()
                self.collect_coins()
                self.check_enemy_collision()

            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
