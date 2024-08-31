import pygame
import sys
import random
from collections import deque

# Constants
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 40
MAZE_WIDTH, MAZE_HEIGHT = 20, 15  # Changed from 19 to 20
SCORE_AREA_HEIGHT = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (200, 200, 0)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)  # Add this line for the enemy color

# Game objects
class Player:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, LIGHT_BROWN, (int(self.x + offset_x), int(self.y + offset_y)), self.radius)
        # Draw eyes
        pygame.draw.circle(screen, BLACK, (int(self.x - 3 + offset_x), int(self.y - 2 + offset_y)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 3 + offset_x), int(self.y - 2 + offset_y)), 2)
        # Draw smile
        pygame.draw.arc(screen, BLACK, 
                        (int(self.x - 4 + offset_x), int(self.y + offset_y), 
                         8, 4),
                        3.14, 2 * 3.14, 1)

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
        self.player = None  # Change this line
        self.init_level()

        self.offset_x = 0  # Changed from (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2 to 0
        self.offset_y = SCORE_AREA_HEIGHT
        self.game_over = False  # Add this line

    def init_level(self):
        self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = self.create_player()  # Change this line
        self.coins = self.create_coins(10)
        self.enemy = self.create_enemy()
        self.score = 0

    def generate_maze(self, width, height):
        # Initialize the maze with walls
        maze = [['X' for _ in range(width)] for _ in range(height)]
        
        def carve_path(x, y):
            maze[y][x] = ' '
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 < nx < width-2 and 1 < ny < height-2 and maze[ny][nx] == 'X':
                    maze[y + dy//2][x + dx//2] = ' '
                    carve_path(nx, ny)
        
        # Start carving from a random point
        start_x, start_y = random.randrange(3, width-3, 2), random.randrange(3, height-3, 2)
        carve_path(start_x, start_y)
        
        # Add start point
        start_x, start_y = random.randrange(1, width-1), random.randrange(1, height-1)
        while maze[start_y][start_x] == 'X':
            start_x, start_y = random.randrange(1, width-1), random.randrange(1, height-1)
        maze[start_y][start_x] = 'S'
        
        return [''.join(row) for row in maze]

    def create_player(self):  # Rename this method
        for y, row in enumerate(self.maze):
            if 'S' in row:
                x = row.index('S') * CELL_SIZE + CELL_SIZE // 2
                y = y * CELL_SIZE + CELL_SIZE // 2
                return Player(x, y, 15, 4)  # Change this line

    def create_coins(self, num_coins):
        coins = []
        empty_cells = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == ' ']
        for _ in range(num_coins):
            if empty_cells:
                x, y = random.choice(empty_cells)
                coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, 10))
                empty_cells.remove((x, y))
        return coins

    def create_enemy(self):
        empty_cells = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == ' ']
        if empty_cells:
            x, y = random.choice(empty_cells)
            return Enemy(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, 15, 2)
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
                cell_x = int((x + dx * self.player.radius) // CELL_SIZE)  # Change this line
                cell_y = int((y + dy * self.player.radius) // CELL_SIZE)  # Change this line
                if self.maze[cell_y][cell_x] == 'X':
                    return True
        return False

    def collect_coins(self):
        player_rect = pygame.Rect(self.player.x - self.player.radius, self.player.y - self.player.radius,   # Change these lines
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

    def draw(self):
        self.screen.fill(GREEN)  # Changed from WHITE to GREEN
        pygame.draw.rect(self.screen, LIGHT_GREEN, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == 'S':  # Draw white rectangles for paths
                    pygame.draw.rect(self.screen, WHITE, (x * CELL_SIZE + self.offset_x, y * CELL_SIZE + self.offset_y, CELL_SIZE, CELL_SIZE))

        for coin in self.coins:
            coin.draw(self.screen, self.offset_x, self.offset_y)

        if self.enemy:  # Add these lines
            self.enemy.draw(self.screen, self.offset_x, self.offset_y)

        self.player.draw(self.screen, self.offset_x, self.offset_y)  # Change this line

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

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.__init__()  # Restart the game

            if not self.game_over:
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]

                new_x = self.player.x + dx * self.player.speed  # Change this line
                new_y = self.player.y + dy * self.player.speed  # Change this line

                if not self.check_collision(new_x, new_y):
                    self.player.move(dx, dy)  # Change this line

                self.player.x = max(self.player.radius, min(WIDTH - self.player.radius, self.player.x))  # Change this line
                self.player.y = max(self.player.radius, min(HEIGHT - self.player.radius, self.player.y))  # Change this line

                self.update_enemy()
                self.collect_coins()
                self.check_enemy_collision()  # Add this line

            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
