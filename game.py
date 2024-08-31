import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 680  # Increased height to accommodate score area and maze
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circle Maze Game")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (200, 200, 0)
GREEN = (0, 128, 0)  # Add this line for the green color
LIGHT_GREEN = (144, 238, 144)  # Add this line for light green color
LIGHT_BROWN = (205, 133, 63)  # Add this line for light brown color

# Circle properties
circle_radius = 15
circle_speed = 4
eye_radius = 2
smile_width = 4
smile_height = 2

# Coin properties
coin_radius = 10
coins = []

# Score
score = 0
font = pygame.font.Font(None, 36)

# Score area properties
score_area_height = 40

# Maze properties
cell_size = 40
maze_width = 19  # Odd number for symmetry
maze_height = 15  # Reduced height to fit the new layout

# Calculate the offset to center the maze
maze_pixel_width = maze_width * cell_size
maze_pixel_height = maze_height * cell_size
offset_x = (width - maze_pixel_width) // 2
offset_y = score_area_height

# Function to generate a random maze without an exit
def generate_maze(width, height):
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

# Generate the random maze
maze = generate_maze(maze_width, maze_height)

# Function to add coins
def add_coins(num_coins):
    empty_cells = [(x, y) for y, row in enumerate(maze) for x, cell in enumerate(row) if cell == ' ']
    for _ in range(num_coins):
        if empty_cells:
            x, y = random.choice(empty_cells)
            coins.append((x * cell_size + cell_size // 2, y * cell_size + cell_size // 2))
            empty_cells.remove((x, y))

# Add initial coins
add_coins(10)  # You can adjust the number of coins

# Find start position (S)
for y, row in enumerate(maze):
    if 'S' in row:
        circle_x = row.index('S') * cell_size + cell_size // 2
        circle_y = y * cell_size + cell_size // 2
        break

# Set up the clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

# Main game loop
running = True
while running:
    # Control the frame rate
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle arrow key presses
    keys = pygame.key.get_pressed()
    new_x, new_y = circle_x, circle_y
    if keys[pygame.K_LEFT]:
        new_x -= circle_speed
    if keys[pygame.K_RIGHT]:
        new_x += circle_speed
    if keys[pygame.K_UP]:
        new_y -= circle_speed
    if keys[pygame.K_DOWN]:
        new_y += circle_speed

    # Check collision with walls
    def check_collision(x, y):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                cell_x = int((x + dx * circle_radius) // cell_size)
                cell_y = int((y + dy * circle_radius) // cell_size)
                if maze[cell_y][cell_x] == 'X':
                    return True
        return False

    if not check_collision(new_x, new_y):
        circle_x, circle_y = new_x, new_y

    # Keep the circle within the screen bounds
    circle_x = max(circle_radius, min(width - circle_radius, circle_x))
    circle_y = max(circle_radius, min(height - circle_radius, circle_y))

    # Check coin collection
    circle_rect = pygame.Rect(circle_x - circle_radius, circle_y - circle_radius, 
                              circle_radius * 2, circle_radius * 2)
    for coin in coins[:]:
        coin_rect = pygame.Rect(coin[0] - coin_radius, coin[1] - coin_radius, 
                                coin_radius * 2, coin_radius * 2)
        if circle_rect.colliderect(coin_rect):
            coins.remove(coin)
            score += 10  # Increase score when collecting a coin

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw score area background
    pygame.draw.rect(screen, LIGHT_GREEN, (0, 0, width, score_area_height))

    # Draw a border between score area and maze
    pygame.draw.line(screen, BLACK, (0, score_area_height), (width, score_area_height), 2)

    # Draw the maze (centered and below score area)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'X':
                pygame.draw.rect(screen, GREEN, (x * cell_size + offset_x, y * cell_size + offset_y, cell_size, cell_size))

    # Draw coins (adjusted position)
    for coin in coins:
        pygame.draw.circle(screen, YELLOW, (coin[0] + offset_x, coin[1] + offset_y), coin_radius)

    # Draw the circle at the updated position (adjusted position)
    pygame.draw.circle(screen, LIGHT_BROWN, (int(circle_x + offset_x), int(circle_y + offset_y)), circle_radius)
    
    # Draw the face (adjusted position)
    # Left eye
    pygame.draw.circle(screen, BLACK, (int(circle_x - 3 + offset_x), int(circle_y - 2 + offset_y)), eye_radius)
    # Right eye
    pygame.draw.circle(screen, BLACK, (int(circle_x + 3 + offset_x), int(circle_y - 2 + offset_y)), eye_radius)
    # Smile
    pygame.draw.arc(screen, BLACK, 
                    (int(circle_x - smile_width + offset_x), int(circle_y + offset_y), 
                     smile_width * 2, smile_height * 2),
                    3.14, 2 * 3.14, 1)

    # Display score (adjusted position)
    score_text = font.render(f"Score: {score}", True, BLACK)  # Changed text color to BLACK for better contrast
    score_rect = score_text.get_rect()
    score_rect.midleft = (10, score_area_height // 2)
    screen.blit(score_text, score_rect)

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
