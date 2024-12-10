import time
import pygame
from constants import *


class GameObject:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen, game):
        # Convert world coordinates to screen coordinates
        screen_x = (self.x - game.camera_x) * game.zoom
        screen_y = (self.y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        return screen_x, screen_y

class MovableObject(GameObject):
    def __init__(self, x, y, radius, speed):
        super().__init__(x, y, radius)
        self.speed = speed
        self.dx = 0
        self.dy = 0

    def move(self, dx, dy):
        self.dx = dx * self.speed
        self.dy = dy * self.speed
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen, game, interpolated_x=None, interpolated_y=None):
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        
        # Convert world coordinates to screen coordinates
        screen_x = (x - game.camera_x) * game.zoom
        screen_y = (y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        
        # Scale the radius according to zoom
        scaled_radius = self.radius * game.zoom
        
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(scaled_radius))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = list(color)  # Convert to list for alpha modification
        self.color.append(255)    # Add alpha channel
        self.birth_time = time.time()
        self.size = PARTICLE_SIZE

    def update(self):
        age = time.time() - self.birth_time
        if age > PARTICLE_LIFETIME:
            return False
        
        # Fade out over lifetime
        self.color[3] = max(0, 255 * (1 - age / PARTICLE_LIFETIME))
        return True

    def draw(self, screen, game):
        if self.color[3] > 0:  # Only draw if not completely transparent
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, self.color, (self.size, self.size), self.size)
            screen_x = (self.x - game.camera_x) * game.zoom
            screen_y = (self.y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
            screen.blit(surface, (int(screen_x - self.size), int(screen_y - self.size)))

class Player(MovableObject):
    SYMBOL = 'S'
    def __init__(self, x, y, radius, speed, collision_checker, color=GOLD, face_type="happy", trail_color=PARTICLE_COLOR):
        super().__init__(x, y, radius, speed)
        self.collision_checker = collision_checker
        self.direction = None
        self.color = color
        self.face_type = face_type
        self.trail_color = trail_color  # Store trail color
        self.particles = []
        self.last_particle_time = time.time()

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen, game, interpolated_x=None, interpolated_y=None):
        # Draw particles first (behind player)
        for particle in self.particles:
            particle.draw(screen, game)
            
        # Draw player
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        
        # Convert world coordinates to screen coordinates
        screen_x = (x - game.camera_x) * game.zoom
        screen_y = (y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        
        # Scale the radius according to zoom
        scaled_radius = int(self.radius * game.zoom)  # Convert to int
        
        # Draw the player circle
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), scaled_radius)
        
        # Draw eyes
        eye_radius = max(2, scaled_radius // 5)
        eye_offset = scaled_radius // 3
        pygame.draw.circle(screen, BLACK, (int(screen_x - eye_offset), int(screen_y - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(screen_x + eye_offset), int(screen_y - eye_offset)), eye_radius)
        
        # Draw mouth - ensure all rect coordinates are integers
        if self.face_type == "happy":
            smile_rect = pygame.Rect(
                int(screen_x - scaled_radius//2),
                int(screen_y),
                scaled_radius,
                scaled_radius//2
            )
            pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, max(1, scaled_radius//5))
        else:  # sad face
            frown_rect = pygame.Rect(
                int(screen_x - scaled_radius//2),
                int(screen_y + scaled_radius//4),
                scaled_radius,
                scaled_radius//2
            )
            pygame.draw.arc(screen, BLACK, frown_rect, 0, 3.14, max(1, scaled_radius//5))

    def set_direction(self, direction):
        if self.direction is None:
            self.direction = direction

    def update(self):
        if self.direction:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not self.collision_checker(new_x, new_y, self.radius):
                self.move(dx, dy)
                # Add particles with custom trail color when moving
                current_time = time.time()
                if current_time - self.last_particle_time > 0.02:
                    self.particles.append(Particle(self.x, self.y, self.trail_color))
                    self.last_particle_time = current_time
            else:
                self.direction = None

        # Update particles
        self.particles = [p for p in self.particles if p.update()]

class Coin(GameObject):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS

    def draw(self, screen, game):
        # Convert world coordinates to screen coordinates
        screen_x = (self.x - game.camera_x) * game.zoom
        screen_y = (self.y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        scaled_radius = int(self.radius * game.zoom)
        pygame.draw.circle(screen, COIN_COLOR, (int(screen_x), int(screen_y)), scaled_radius)

class Enemy(GameObject):
    SYMBOL = 'E'
    def __init__(self, x, y, radius, speed, find_path_func):
        super().__init__(x, y, radius)
        self.speed = speed
        self.find_path_func = find_path_func
        self.path = []
        self.target = None
        self.color = RED
        self.dx = 0
        self.dy = 0

    def update(self, player_pos):
        if not self.path:
            self.set_new_path(player_pos)
        self.move_along_path()

    def draw(self, screen, game, interpolated_x=None, interpolated_y=None):
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        
        # Convert world coordinates to screen coordinates
        screen_x = (x - game.camera_x) * game.zoom
        screen_y = (y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        scaled_radius = int(self.radius * game.zoom)
        
        # Draw the main body
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), scaled_radius)
        
        # Draw angry eyes
        eye_radius = max(2, scaled_radius // 5)
        eye_offset = scaled_radius // 3
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x - eye_offset), int(screen_y - eye_offset)), 
            eye_radius)
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x + eye_offset), int(screen_y - eye_offset)), 
            eye_radius)
        
        # Draw angry eyebrows
        eyebrow_length = scaled_radius // 2
        eyebrow_thickness = max(1, scaled_radius // 10)
        pygame.draw.line(screen, BLACK, 
            (int(screen_x - eye_offset - eyebrow_length//2), 
             int(screen_y - eye_offset - eye_radius)),
            (int(screen_x - eye_offset + eyebrow_length//2), 
             int(screen_y - eye_offset - eye_radius - eyebrow_thickness)),
            eyebrow_thickness)
        pygame.draw.line(screen, BLACK, 
            (int(screen_x + eye_offset - eyebrow_length//2), 
             int(screen_y - eye_offset - eye_radius - eyebrow_thickness)),
            (int(screen_x + eye_offset + eyebrow_length//2), 
             int(screen_y - eye_offset - eye_radius)),
            eyebrow_thickness)
        
        # Draw angry mouth
        mouth_width = scaled_radius
        mouth_height = scaled_radius // 3
        mouth_rect = pygame.Rect(
            int(screen_x - mouth_width//2),
            int(screen_y),
            mouth_width,
            mouth_height
        )
        pygame.draw.arc(screen, BLACK, mouth_rect, 3.14, 2 * 3.14, max(1, scaled_radius // 10))

    def set_new_path(self, player_pos):
        start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
        goal = (int(player_pos[0] // CELL_SIZE), int(player_pos[1] // CELL_SIZE))
        self.path = self.find_path_func(start, goal)
        if self.path:
            self.path.pop(0)  # Remove the starting position

    def move_along_path(self):
        if self.path:
            next_x, next_y = self.path[0]
            target_x = next_x * CELL_SIZE + CELL_SIZE // 2
            target_y = next_y * CELL_SIZE + CELL_SIZE // 2

            dx = target_x - self.x
            dy = target_y - self.y
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5

            if distance < self.speed:
                self.x, self.y = target_x, target_y
                self.path.pop(0)
                self.dx = 0  # Add this line
                self.dy = 0  # Add this line
            else:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                self.x += move_x
                self.y += move_y
                self.dx = move_x  # Add this line
                self.dy = move_y  # Add this line

class Star(GameObject):
    SYMBOL = '*'
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen, game):
        # Convert world coordinates to screen coordinates
        screen_x = (self.x - game.camera_x) * game.zoom
        screen_y = (self.y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        scaled_radius = int(self.radius * game.zoom)
        
        # Draw white background circle
        pygame.draw.rect(screen, WHITE, (
            int(screen_x - scaled_radius),
            int(screen_y - scaled_radius),
            scaled_radius * 2,
            scaled_radius * 2
        ))
        
        # Draw star
        pygame.draw.polygon(screen, GOLD, [
            (screen_x, screen_y - scaled_radius),
            (screen_x + scaled_radius * 0.3, screen_y + scaled_radius * 0.4),
            (screen_x + scaled_radius, screen_y + scaled_radius * 0.4),
            (screen_x + scaled_radius * 0.5, screen_y + scaled_radius),
            (screen_x + scaled_radius * 0.7, screen_y + scaled_radius * 1.6),
            (screen_x, screen_y + scaled_radius * 1.2),
            (screen_x - scaled_radius * 0.7, screen_y + scaled_radius * 1.6),
            (screen_x - scaled_radius * 0.5, screen_y + scaled_radius),
            (screen_x - scaled_radius, screen_y + scaled_radius * 0.4),
            (screen_x - scaled_radius * 0.3, screen_y + scaled_radius * 0.4),
        ])

class Diamond(GameObject):
    SYMBOL = 'D'
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = CELL_SIZE // 2

    def draw(self, screen, game):
        # Convert world coordinates to screen coordinates
        screen_x = (self.x - game.camera_x) * game.zoom
        screen_y = (self.y - game.camera_y) * game.zoom + SCORE_AREA_HEIGHT
        scaled_radius = int(self.radius * game.zoom)
        
        # Draw white background circle
        pygame.draw.rect(screen, WHITE, (
            int(screen_x - scaled_radius),
            int(screen_y - scaled_radius),
            scaled_radius * 2,
            scaled_radius * 2
        ))
        
        # Draw diamond
        points = [
            (screen_x, screen_y - scaled_radius),
            (screen_x + scaled_radius, screen_y),
            (screen_x, screen_y + scaled_radius),
            (screen_x - scaled_radius, screen_y),
        ]
        pygame.draw.polygon(screen, CYAN, points)

