import pygame
import sys
import random
from collections import deque
import time  # Add this import

# Constants
FPS = 60
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 20
MAZE_WIDTH, MAZE_HEIGHT = 40, 30
SCORE_AREA_HEIGHT = 40
ENEMY_SPEED = CELL_SIZE // 20
PLAYER_SPEED = CELL_SIZE // 1
ESCAPE_ROUTES = max(100, MAZE_WIDTH // 10)  # New constant for number of escape routes
DEV_MODE = True  # New constant for dev mode

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (200, 200, 0)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)

# Game objects
class Player:
    def __init__(self, game, x, y, radius, speed):
        self.game = game  # Add this line
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
        # Draw eyes
        eye_radius = max(2, self.radius // 5)
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset + offset_x), int(self.y - eye_offset + offset_y)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset + offset_x), int(self.y - eye_offset + offset_y)), eye_radius)
        # Draw smile
        smile_rect = (int(self.x - self.radius // 2 + offset_x), int(self.y + offset_y), 
                      self.radius, self.radius // 2)
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
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, YELLOW, (self.x + offset_x, self.y + offset_y), self.radius)

class Enemy:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.path = []

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
        self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = self.create_player()
        if self.player is None:
            raise ValueError("Failed to create player")
        self.init_level()  # Initialize other game elements

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT
        self.game_over = False

    def init_dev_mode(self):
        if self.dev_maze is None:
            self.dev_maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
            # Add a default start position
            self.dev_maze[1][1] = 'S'
        self.coins = []
        self.enemy = None
        self.score = 0

    def init_level(self):
        self.coins = self.create_coins(10)
        self.enemy = self.create_enemy()
        self.score = 0

    def generate_maze(self, width, height):
        # Initialize the maze with walls
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

        # Start carving from a random point
        x, y = random.randrange(1, width-1), random.randrange(1, height-1)
        maze[y][x] = 'S'  # Set start point
        
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
        
        # If 'S' is not found, place the player at a random empty cell
        empty_cells = [(x, y) for y, row in enumerate(current_maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Player(self, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, PLAYER_SPEED)
        
        # If there are no empty cells, raise an exception
        raise ValueError("No valid position found for the player")

    def create_coins(self, num_coins):
        coins = []
        empty_cells = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == ' ']
        for _ in range(num_coins):
            if empty_cells:
                x, y = random.choice(empty_cells)
                coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 3))
                empty_cells.remove((x, y))
        return coins

    def create_enemy(self):
        empty_cells = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Enemy(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 1, ENEMY_SPEED)
        return None

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
        
        if not self.coins:
            self.level_complete()

    def level_complete(self):
        self.level += 1
        self.init_level()

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
            if self.dev_maze[y][x] == 'X':
                self.dev_maze[y][x] = ' '
            elif self.dev_maze[y][x] == ' ':
                # Remove the old start position if it exists
                for row in self.dev_maze:
                    if 'S' in row:
                        row[row.index('S')] = ' '
                self.dev_maze[y][x] = 'S'
            elif self.dev_maze[y][x] == 'S':
                self.dev_maze[y][x] = 'X'

    def save_dev_maze(self):
        self.maze = [''.join(row) for row in self.dev_maze]
        self.dev_mode = False
        self.player = self.create_player()
        self.init_level()

    def toggle_dev_mode(self):
        self.dev_mode = not self.dev_mode
        if self.dev_mode:
            self.init_dev_mode()
        else:
            self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
            self.init_level()
        self.player = self.create_player()

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

        if self.player:
            self.player.draw(self.screen, self.offset_x, self.offset_y)

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
            
            dev_text = self.font.render("Dev Mode: Click to toggle cells, SPACE to save, D to exit", True, BLACK)
            dev_rect = dev_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
            self.screen.blit(dev_text, dev_rect)
        else:
            # Add instructions for entering dev mode
            dev_hint = self.font.render("Press D for Dev Mode", True, BLACK)
            dev_hint_rect = dev_hint.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
            self.screen.blit(dev_hint, dev_hint_rect)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and self.dev_mode:
                    self.handle_dev_mode_input(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.toggle_dev_mode()
                    elif self.dev_mode and event.key == pygame.K_SPACE:
                        self.save_dev_maze()
                    elif self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.__init__()
                    else:
                        if event.key == pygame.K_RIGHT:
                            self.player.set_direction((1, 0))
                        elif event.key == pygame.K_LEFT:
                            self.player.set_direction((-1, 0))
                        elif event.key == pygame.K_DOWN:
                            self.player.set_direction((0, 1))
                        elif event.key == pygame.K_UP:
                            self.player.set_direction((0, -1))

            if not self.game_over and not self.dev_mode:
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
