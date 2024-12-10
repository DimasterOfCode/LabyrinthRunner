FPS = 60
WIDTH, HEIGHT = 800, 680
CELL_SIZE = 20
MAZE_WIDTH, MAZE_HEIGHT = 40, 30
SCORE_AREA_HEIGHT = 40
ENEMY_SPEED = CELL_SIZE // 6
PLAYER_SPEED = CELL_SIZE // 4
ESCAPE_ROUTES = max(10, MAZE_WIDTH // 10)
DEV_MODE = True
ENEMY_CHASE_DELAY = 3
COIN_RADIUS = CELL_SIZE // 7  # New constant for coin radius

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (200, 200, 0)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)  # New color for diamonds
COIN_COLOR = YELLOW  # New constant for coin color

# Theme Colors
THEME_PRIMARY = (50, 50, 100)  # Dark blue
THEME_SECONDARY = (100, 100, 255)  # Light blue
THEME_ACCENT = (255, 215, 0)  # Gold
THEME_BACKGROUND = (20, 20, 50)  # Very dark blue
THEME_TEXT = (255, 255, 255)  # White
THEME_TEXT_SECONDARY = (200, 200, 200)  # Light gray

# Player constants
PLAYER_RADIUS = CELL_SIZE // 2.2  # Changed from CELL_SIZE // 3.2 back to original CELL_SIZE // 3
PLAYER_SPEED = 5  # Player movement speed

# Particle constants
PARTICLE_LIFETIME = 0.5  # seconds
PARTICLE_FADE_SPEED = 5
PARTICLE_SIZE = 3
PARTICLE_COLOR = (135, 206, 235)  # Light blue