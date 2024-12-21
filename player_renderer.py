import pygame
from items import ITEMS

class PlayerRenderer:
    @staticmethod
    def draw_player(screen, pos, radius, color, face_type, hat_type, scale=1.0, trail_type="none", trail_color=None):
        screen_x, screen_y = pos
        scaled_radius = int(radius * scale)

        # Draw trail first (behind player)
        PlayerRenderer.draw_trail(screen, pos, radius, scale, trail_type, trail_color)
        
        # Draw body
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), scaled_radius)
        
        # Draw face
        ITEMS["face"][face_type].draw(screen, pos, radius, scale)
        
        # Draw hat
        ITEMS["hat"][hat_type].draw(screen, pos, radius, scale, color)

    @staticmethod
    def draw_trail(screen, pos, radius, scale=1.0, trail_type="none", trail_color=None):
        """Draw just the trail effect"""
        ITEMS["trail"][trail_type].draw(screen, pos, radius, scale, trail_color)