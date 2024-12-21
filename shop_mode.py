import pygame
import math
from constants import *
from game_mode import GameMode
from items import ITEMS
from player_renderer import PlayerRenderer

class ShopMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.selected_item = None
        self.grid_size = 120  # Size of each grid cell
        self.padding = 20     # Padding between cells
        self.scroll_offset = 0
        self.scroll_speed = 20
        
        # Flatten items into a single list for display
        self.items = []
        for category in ITEMS:
            for item_id, item in ITEMS[category].items():
                if item_id != "none":  # Skip "none" items
                    self.items.append({
                        "category": category,
                        "id": item_id,
                        "item": item,
                        "price": 100  # Default price, you can customize this
                    })

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.set_mode("menu")
                self.game.sound_manager.play_sound('menu_move')
            elif event.key == pygame.K_UP:
                self.scroll_offset = min(0, self.scroll_offset + self.scroll_speed)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset -= self.scroll_speed

    def render(self, screen, interpolation):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Draw background
        screen.fill(THEME_BACKGROUND)
        
        # Draw title
        title = self.font.render("Shop", True, THEME_TEXT)
        title_rect = title.get_rect(midtop=(screen_width//2, 20))
        screen.blit(title, title_rect)
        
        # Draw instructions
        instructions = self.small_font.render("Press ESC to return to menu", True, THEME_TEXT)
        instructions_rect = instructions.get_rect(midbottom=(screen_width//2, screen_height - 10))
        screen.blit(instructions, instructions_rect)
        
        # Calculate grid layout
        cols = max(1, (screen_width - self.padding) // (self.grid_size + self.padding))
        start_x = (screen_width - (cols * (self.grid_size + self.padding) - self.padding)) // 2
        start_y = 100 + self.scroll_offset
        
        # Draw items in grid
        for i, item_data in enumerate(self.items):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (self.grid_size + self.padding)
            y = start_y + row * (self.grid_size + self.padding)
            
            # Skip if item is completely off screen
            if y + self.grid_size < 0 or y > screen_height:
                continue
            
            # Draw item background
            item_rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
            pygame.draw.rect(screen, THEME_SECONDARY, item_rect, border_radius=10)
            pygame.draw.rect(screen, THEME_TEXT, item_rect, 2, border_radius=10)
            
            # Draw item with adjusted position and size
            item = item_data["item"]
            category = item_data["category"]
            
            # Calculate item display area (80% of grid size)
            display_size = int(self.grid_size * 0.8)
            item_x = x + (self.grid_size - display_size) // 2
            item_y = y + (self.grid_size - display_size) // 2
            
            # Create a surface for the item
            item_surface = pygame.Surface((display_size, display_size), pygame.SRCALPHA)
            
            # Draw the item centered on its surface
            item_center = (display_size // 2, display_size // 2)
            
            if category == "trail":
                # Use preview rendering for trails
                mock_player_pos = (display_size * 0.7, display_size // 2)
                item.draw_preview(item_surface, 
                    mock_player_pos,
                    display_size // 4,
                    scale=1.0,
                    color=THEME_TEXT)
            elif category == "hat":
                # Adjust hat position to be centered
                hat_center = (display_size // 2, display_size // 2 + display_size // 6)
                item.draw(item_surface, hat_center, display_size // 3)
            else:
                # Default drawing for other items
                item.draw(item_surface, item_center, display_size // 3)
            
            # Blit the item surface onto the screen
            screen.blit(item_surface, (item_x, item_y))
            
            # Draw item name
            name = self.small_font.render(item.name, True, THEME_TEXT)
            name_rect = name.get_rect(midtop=(x + self.grid_size//2, y + self.grid_size - 30))
            screen.blit(name, name_rect)
            
            # Draw price
            price = self.small_font.render(f"{item_data['price']} coins", True, GOLD)
            price_rect = price.get_rect(midbottom=(x + self.grid_size//2, y + self.grid_size - 5))
            screen.blit(price, price_rect) 

    def draw_star(self, surface, pos, size, color):
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
        
        pygame.draw.polygon(surface, color, points)