import time
import pygame
from constants import *


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
        self.dx = 0
        self.dy = 0

    def move(self, dx, dy):
        self.dx = dx * self.speed
        self.dy = dy * self.speed
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen, offset_x, offset_y, interpolated_x=None, interpolated_y=None):
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        pygame.draw.circle(screen, self.color, (int(x + offset_x), int(y + offset_y)), self.radius)

class Player(MovableObject):
    SYMBOL = 'S'
    def __init__(self, x, y, radius, speed, collision_checker, color=GOLD):
        super().__init__(x, y, radius, speed)
        self.collision_checker = collision_checker
        self.direction = None
        self.color = color

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen, offset_x, offset_y, interpolated_x=None, interpolated_y=None):
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        pygame.draw.circle(screen, self.color, (int(x + offset_x), int(y + offset_y)), self.radius)
        eye_radius = max(2, self.radius // 5)
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, BLACK, (int(x - eye_offset + offset_x), int(y - eye_offset + offset_y)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(x + eye_offset + offset_x), int(y - eye_offset + offset_y)), eye_radius)
        smile_rect = (int(x - self.radius // 2 + offset_x), int(y + offset_y), self.radius, self.radius // 2)
        pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, max(1, self.radius // 5))

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
    def __init__(self, x, y, radius, speed, path_finder):
        super().__init__(x, y, radius, speed)
        self.path_finder = path_finder
        self.path = []
        self.start_time = time.time()
        self.chase_delay = ENEMY_CHASE_DELAY
        self.color = RED
        self.target = None

    def update(self, player_pos):
        if self.should_chase():
            if not self.path or self.target != player_pos:
                self.target = player_pos
                start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
                goal = (int(player_pos[0] // CELL_SIZE), int(player_pos[1] // CELL_SIZE))
                self.path = self.path_finder(start, goal)
                if self.path:
                    self.path.pop(0)  # Remove the starting position

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
                else:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed

    def draw(self, screen, offset_x, offset_y, interpolated_x=None, interpolated_y=None):
        x = interpolated_x if interpolated_x is not None else self.x
        y = interpolated_y if interpolated_y is not None else self.y
        
        # Draw the main body
        pygame.draw.circle(screen, self.color, (int(x + offset_x), int(y + offset_y)), self.radius)
        
        # Draw angry eyes
        eye_radius = max(2, self.radius // 5)
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, BLACK, (int(x - eye_offset + offset_x), int(y - eye_offset + offset_y)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(x + eye_offset + offset_x), int(y - eye_offset + offset_y)), eye_radius)
        
        # Draw angry eyebrows
        eyebrow_length = self.radius // 2
        eyebrow_thickness = max(1, self.radius // 10)
        pygame.draw.line(screen, BLACK, 
                         (int(x - eye_offset - eyebrow_length//2 + offset_x), int(y - eye_offset - eye_radius + offset_y)),
                         (int(x - eye_offset + eyebrow_length//2 + offset_x), int(y - eye_offset - eye_radius - eyebrow_thickness + offset_y)),
                         eyebrow_thickness)
        pygame.draw.line(screen, BLACK, 
                         (int(x + eye_offset - eyebrow_length//2 + offset_x), int(y - eye_offset - eye_radius - eyebrow_thickness + offset_y)),
                         (int(x + eye_offset + eyebrow_length//2 + offset_x), int(y - eye_offset - eye_radius + offset_y)),
                         eyebrow_thickness)
        
        # Draw angry mouth
        mouth_width = self.radius
        mouth_height = self.radius // 3
        pygame.draw.arc(screen, BLACK, 
                        (int(x - mouth_width//2 + offset_x), int(y + offset_y), mouth_width, mouth_height),
                        3.14, 2 * 3.14, max(1, self.radius // 10))

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

