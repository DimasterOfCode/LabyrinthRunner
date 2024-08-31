import pygame
import sys
import random

# Constants
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 40
MAZE_WIDTH, MAZE_HEIGHT = 19, 15
SCORE_AREA_HEIGHT = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (200, 200, 0)
LIGHT_BROWN = (205, 133, 63)

# Game objects
class Circle:
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Circle Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.level = 1
        self.init_level()

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT

    def init_level(self):
        self.maze = self.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.circle = self.create_circle()
        self.coins = self.create_coins(10)
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

    def create_circle(self):
        for y, row in enumerate(self.maze):
            if 'S' in row:
                x = row.index('S') * CELL_SIZE + CELL_SIZE // 2
                y = y * CELL_SIZE + CELL_SIZE // 2
                return Circle(x, y, 15, 4)

    def create_coins(self, num_coins):
        coins = []
        empty_cells = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == ' ']
        for _ in range(num_coins):
            if empty_cells:
                x, y = random.choice(empty_cells)
                coins.append(Coin(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, 10))
                empty_cells.remove((x, y))
        return coins

    def check_collision(self, x, y):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                cell_x = int((x + dx * self.circle.radius) // CELL_SIZE)
                cell_y = int((y + dy * self.circle.radius) // CELL_SIZE)
                if self.maze[cell_y][cell_x] == 'X':
                    return True
        return False

    def collect_coins(self):
        circle_rect = pygame.Rect(self.circle.x - self.circle.radius, self.circle.y - self.circle.radius, 
                                  self.circle.radius * 2, self.circle.radius * 2)
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin.x - coin.radius, coin.y - coin.radius, 
                                    coin.radius * 2, coin.radius * 2)
            if circle_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                self.score += 10
        
        if not self.coins:
            self.level_complete()

    def level_complete(self):
        self.level += 1
        self.init_level()

    def draw(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, LIGHT_GREEN, (0, 0, WIDTH, SCORE_AREA_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (0, SCORE_AREA_HEIGHT), (WIDTH, SCORE_AREA_HEIGHT), 2)

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 'X':
                    pygame.draw.rect(self.screen, GREEN, (x * CELL_SIZE + self.offset_x, y * CELL_SIZE + self.offset_y, CELL_SIZE, CELL_SIZE))

        for coin in self.coins:
            coin.draw(self.screen, self.offset_x, self.offset_y)

        self.circle.draw(self.screen, self.offset_x, self.offset_y)

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

            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]

            new_x = self.circle.x + dx * self.circle.speed
            new_y = self.circle.y + dy * self.circle.speed

            if not self.check_collision(new_x, new_y):
                self.circle.move(dx, dy)

            self.circle.x = max(self.circle.radius, min(WIDTH - self.circle.radius, self.circle.x))
            self.circle.y = max(self.circle.radius, min(HEIGHT - self.circle.radius, self.circle.y))

            self.collect_coins()
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
