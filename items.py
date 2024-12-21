import pygame
import math
from constants import *

class SlotItem:
    """Base class for all customization items"""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        """Default draw method - override in subclasses"""
        pass

    def draw_preview(self, screen, pos, radius, scale=1.0, color=None):
        """Default preview method - can be overridden for custom preview rendering"""
        self.draw(screen, pos, radius, scale, color)

class NoItem(SlotItem):
    """Generic empty slot item"""
    def __init__(self, name="None"):
        super().__init__("none", name)

# Hat Items
class TopHat(SlotItem):
    def __init__(self):
        super().__init__("top_hat", "Top Hat")
    
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

class Crown(SlotItem):
    def __init__(self):
        super().__init__("crown", "Royal Crown")
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        hat_y_offset = scaled_radius * 0.05
        
        # Draw crown base
        crown_width = scaled_radius * 1.6
        crown_height = scaled_radius * 0.8
        
        # Draw points
        points = []
        num_points = 5
        for i in range(num_points):
            x = screen_x - crown_width//2 + (crown_width * i//(num_points-1))
            y = screen_y - scaled_radius - crown_height - hat_y_offset
            points.append((x, y))
            if i < num_points-1:  # Add valley between points
                valley_x = screen_x - crown_width//2 + (crown_width * (i+0.5)//(num_points-1))
                valley_y = screen_y - scaled_radius - crown_height//2 - hat_y_offset
                points.append((valley_x, valley_y))
        
        # Add base points
        points.append((screen_x + crown_width//2, screen_y - scaled_radius - hat_y_offset))
        points.append((screen_x - crown_width//2, screen_y - scaled_radius - hat_y_offset))
        
        pygame.draw.polygon(screen, GOLD, points)
        
        # Add jewels
        jewel_radius = scaled_radius * 0.15
        for i in range(num_points):
            x = screen_x - crown_width//2 + (crown_width * i//(num_points-1))
            y = screen_y - scaled_radius - crown_height - hat_y_offset
            pygame.draw.circle(screen, RED, (int(x), int(y)), int(jewel_radius))

class BaseballCap(SlotItem):
    def __init__(self):
        super().__init__("baseball_cap", "Baseball Cap")
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        hat_y_offset = scaled_radius * 0.05
        
        cap_color = color or RED
        
        # Draw cap base
        cap_width = scaled_radius * 1.5
        cap_height = scaled_radius * 0.6
        
        # Draw curved top
        pygame.draw.arc(screen, cap_color,
            (int(screen_x - cap_width//2),
             int(screen_y - scaled_radius - cap_height),
             int(cap_width), int(cap_height * 2)),
            math.pi, 2 * math.pi)
        
        # Draw brim
        brim_points = [
            (screen_x - cap_width//2, screen_y - scaled_radius + hat_y_offset),
            (screen_x - cap_width//1.5, screen_y - scaled_radius - cap_height//2),
            (screen_x - cap_width//3, screen_y - scaled_radius - cap_height//1.5)
        ]
        pygame.draw.polygon(screen, cap_color, brim_points)

# Face Items
class HappyFace(SlotItem):
    def __init__(self):
        super().__init__("happy", "Happy Face")
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
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

class SadFace(SlotItem):
    def __init__(self):
        super().__init__("sad", "Sad Face")
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
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

class CoolFace(SlotItem):
    def __init__(self):
        super().__init__("cool", "Cool Face")
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)
        
        # Draw sunglasses
        glass_width = scaled_radius * 0.4
        glass_height = scaled_radius * 0.25
        glass_y = screen_y - scaled_radius * 0.3
        
        # Left lens
        pygame.draw.ellipse(screen, BLACK,
            (int(screen_x - glass_width * 1.5), int(glass_y),
             int(glass_width), int(glass_height)))
        
        # Right lens
        pygame.draw.ellipse(screen, BLACK,
            (int(screen_x + glass_width * 0.5), int(glass_y),
             int(glass_width), int(glass_height)))
        
        # Bridge
        pygame.draw.line(screen, BLACK,
            (int(screen_x - glass_width * 0.5), int(glass_y + glass_height * 0.5)),
            (int(screen_x + glass_width * 0.5), int(glass_y + glass_height * 0.5)),
            max(1, int(scaled_radius * 0.05)))
        
        # Draw smirk
        smirk_rect = pygame.Rect(
            int(screen_x - scaled_radius//3),
            int(screen_y + scaled_radius//4),
            scaled_radius//2,
            scaled_radius//3
        )
        pygame.draw.arc(screen, BLACK, smirk_rect, 0, 3.14, 
            max(1, scaled_radius//5))

# Trail Items
class CircleTrail(SlotItem):
    def __init__(self):
        super().__init__("circles", "Circle Trail")
    
    def draw_preview(self, screen, pos, radius, scale=1.0, color=None):
        """Special preview rendering for shop tiles"""
        screen_x, screen_y = pos
        particle_spacing = int(15 * scale)
        base_particle_size = int(18 * scale)
        start_x = screen_x
        
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
            
            x_pos = start_x - (i * particle_spacing)
            screen.blit(particle_surface, (x_pos, screen_y + 5))

    def draw(self, screen, pos, radius, scale=1.0, color=None):
        """Normal in-game rendering"""
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

class StarTrail(SlotItem):
    def __init__(self):
        super().__init__("stars", "Star Trail")
    
    def draw_preview(self, screen, pos, radius, scale=1.0, color=None):
        """Special preview rendering for shop tiles"""
        screen_x, screen_y = pos
        particle_spacing = int(15 * scale)
        star_size = int(15 * scale)
        start_x = screen_x
        
        for i in range(3):
            opacity = 200 - (i * 50)
            star_color = list(color or (255, 215, 0))  # Gold default
            star_color.append(opacity)
            
            x_pos = start_x - (i * particle_spacing)
            self.draw_star(screen, (x_pos, screen_y), star_size, star_color)
    
    def draw(self, screen, pos, radius, scale=1.0, color=None):
        """Normal in-game rendering"""
        screen_x, screen_y = pos
        particle_spacing = int(30 * scale)
        star_size = int(15 * scale)
        start_x = screen_x - particle_spacing * 10
        
        for i in range(3):
            opacity = 200 - (i * 50)
            star_color = list(color or (255, 215, 0))  # Gold default
            star_color.append(opacity)
            x_pos = start_x + ((2 - i) * particle_spacing)
            self.draw_star(screen, (x_pos, screen_y), star_size, star_color)
    
    def draw_star(self, screen, pos, size, color):
        x, y = pos
        points = []
        for i in range(5):
            # Outer points
            angle = i * (2 * math.pi / 5) - math.pi / 2
            points.append((
                x + size * math.cos(angle),
                y + size * math.sin(angle)
            ))
            # Inner points
            angle += math.pi / 5
            points.append((
                x + size * 0.4 * math.cos(angle),
                y + size * 0.4 * math.sin(angle)
            ))
        
        pygame.draw.polygon(screen, color, points)

# Create instances of all items
ITEMS = {
    "hat": {
        "none": NoItem("No Hat"),
        "top_hat": TopHat(),
        "crown": Crown(),
        "baseball_cap": BaseballCap()
    },
    "face": {
        "happy": HappyFace(),
        "sad": SadFace(),
        "cool": CoolFace()
    },
    "trail": {
        "none": NoItem("No Trail"),
        "circles": CircleTrail(),
        "stars": StarTrail()
    }
} 