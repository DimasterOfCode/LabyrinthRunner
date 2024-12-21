import pygame
import math
from constants import *

# Hat Items
class NoHat:
    def __init__(self):
        self.id = "none"
        self.name = "No Hat"
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        pass  # Nothing to draw

class TopHat:
    def __init__(self):
        self.id = "top_hat"
        self.name = "Top Hat"
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        hat_y_offset = scaled_radius * 0.05
        
        # Draw brim
        brim_width = scaled_radius * 1.8
        pygame.draw.ellipse(screen, BLACK,
            (int(screen_x - brim_width//2),
             int(screen_y - scaled_radius - hat_y_offset),
             int(brim_width), int(scaled_radius * 0.3)))
        
        # Draw top
        hat_height = scaled_radius * 1.2
        hat_width = scaled_radius * 1.2
        pygame.draw.rect(screen, BLACK,
            (int(screen_x - hat_width//2),
             int(screen_y - scaled_radius - hat_y_offset - hat_height),
             int(hat_width), int(hat_height)))

# Face Items
class HappyFace:
    def __init__(self):
        self.id = "happy"
        self.name = "Happy Face"
    
    def draw(self, screen, pos, radius, scale=1.0):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        
        # Draw eyes
        eye_radius = max(2, scaled_radius // 5)
        eye_offset = scaled_radius // 3
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x - eye_offset), int(screen_y - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x + eye_offset), int(screen_y - eye_offset)), eye_radius)
        
        # Draw smile
        smile_rect = pygame.Rect(
            int(screen_x - scaled_radius//2),
            int(screen_y),
            scaled_radius,
            scaled_radius//2
        )
        pygame.draw.arc(screen, BLACK, smile_rect, 3.14, 2 * 3.14, 
            max(1, scaled_radius//5))

class SadFace:
    def __init__(self):
        self.id = "sad"
        self.name = "Sad Face"
    
    def draw(self, screen, pos, radius, scale=1.0):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        
        # Draw eyes
        eye_radius = max(2, scaled_radius // 5)
        eye_offset = scaled_radius // 3
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x - eye_offset), int(screen_y - eye_offset)), eye_radius)
        pygame.draw.circle(screen, BLACK, 
            (int(screen_x + eye_offset), int(screen_y - eye_offset)), eye_radius)
        
        # Draw frown
        frown_rect = pygame.Rect(
            int(screen_x - scaled_radius//2),
            int(screen_y + scaled_radius//4),
            scaled_radius,
            scaled_radius//2
        )
        pygame.draw.arc(screen, BLACK, frown_rect, 0, 3.14, 
            max(1, scaled_radius//5))

# Trail Items
class NoTrail:
    def __init__(self):
        self.id = "none"
        self.name = "No Trail"
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        pass  # Nothing to draw

class CircleTrail:
    def __init__(self):
        self.id = "circles"
        self.name = "Circle Trail"
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        screen_x, screen_y = pos
        particle_spacing = int(25 * scale)
        base_particle_size = int(18 * scale)
        start_x = screen_x - particle_spacing * 10
        
        for i in range(3):
            particle_size = base_particle_size - (i * 2.0)
            opacity = 200 - (i * 50)
            particle_color = list(color or (135, 206, 235))
            particle_color.append(opacity)
            
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            
            for r in range(int(particle_size), 0, -1):
                current_opacity = int(opacity * (r / particle_size) * 0.8)
                current_color = list(color or (135, 206, 235))
                current_color.append(current_opacity)
                pygame.draw.circle(particle_surface, current_color, 
                                 (particle_size, particle_size), r)
            
            x_pos = start_x + ((2 - i) * (particle_spacing + particle_size))
            screen.blit(particle_surface, (x_pos, screen_y + 5))

# Create instances of all items
ITEMS = {
    "hat": {
        "none": NoHat(),
        "top_hat": TopHat()
    },
    "face": {
        "happy": HappyFace(),
        "sad": SadFace()
    },
    "trail": {
        "none": NoTrail(),
        "circles": CircleTrail()
    }
} 