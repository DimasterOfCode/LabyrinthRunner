import os
import sys

import pygame
import pygame.gfxdraw
from constants import WIDTH, HEIGHT, SCORE_AREA_HEIGHT, MAZE_WIDTH, CELL_SIZE, FPS
from level_manager import LevelManager
from sound_manager import SoundManager  # Add this import

from menu_mode import MenuMode
from runner_customization_mode import RunnerCustomizationMode
from level_editor_mode import LevelEditorMode
from play_mode import PlayMode, GameState  # Add GameState import here
from shop_mode import ShopMode

class Game:
    def __init__(self):
        pygame.init()
        # Store original dimensions
        self.window_width = WIDTH
        self.window_height = HEIGHT
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Labyrinth Runner")
        self.clock = pygame.time.Clock()
        
        self.level_manager = LevelManager("levels.json")
        self.level_manager.load_or_generate_levels()

        # Initialize the sound manager
        self.sound_manager = SoundManager()

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT
        self.running = True
        
        # Initialize modes dictionary
        self.modes = {}
        
        # Create instances of game modes
        self.modes["menu"] = MenuMode(self)
        self.modes["shop"] = ShopMode(self)
        self.modes["runner_customization"] = RunnerCustomizationMode(self)
        self.modes["level_editor"] = LevelEditorMode(self, self.level_manager)
        self.modes["play"] = PlayMode(self, self.level_manager)
        
        self.current_mode = self.modes["menu"]

        # Fixed timestep variables
        self.TICKS_PER_SECOND = 60
        self.SKIP_TICKS = 1000 / self.TICKS_PER_SECOND
        self.MAX_FRAMESKIP = 5

        self.fps_font = pygame.font.Font(None, 30)
        self.fps = 0
        self.fps_update_time = 0

        # Fog of war settings
        self.fog_radius = 3  # Number of cells visible around the player
        self.fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Camera/viewport settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 4.0  # Increased from 2.0 to 4.0 for 2x more zoom
        
        # Calculate the visible area (adjusted for zoom)
        self.viewport_width = WIDTH / self.zoom
        self.viewport_height = (HEIGHT - SCORE_AREA_HEIGHT) / self.zoom

        # Initialize level scores dictionary with default values
        self.level_scores = {}  # Empty dictionary that will auto-populate as needed

    def play_game_over_sound(self):
        self.sound_manager.play_sound('game_over')

    def play_star_consume_sound(self):
        self.sound_manager.play_sound('star_consume')

    def set_mode(self, mode_name):
        self.current_mode = self.modes[mode_name]
        if mode_name == "play":
            self.modes["play"].start_level()

    def update_fog_of_war(self, player_x, player_y):
        # Fill with completely opaque black (alpha = 255)
        self.fog_surface.fill((0, 0, 0, 255))
        
        # Convert player world coordinates to screen coordinates
        screen_x = (player_x - self.camera_x) * self.zoom
        screen_y = (player_y - self.camera_y) * self.zoom + SCORE_AREA_HEIGHT
        
        # Scale the fog radius according to zoom
        scaled_radius = self.fog_radius * CELL_SIZE * self.zoom
        
        # Create a fully transparent circle (alpha = 0) around the player's screen position
        pygame.draw.circle(self.fog_surface, (0, 0, 0, 0), 
                          (int(screen_x), int(screen_y)), 
                          int(scaled_radius))

    def render(self, screen, interpolation):
        if isinstance(self.current_mode, PlayMode):
            # Get player position before rendering UI elements
            player = self.current_mode.player
            if player is None:
                return
            
            # First render the game elements
            screen.fill((0, 0, 0))
            self.current_mode.render_maze(screen)
            
            # Only apply interpolation if the player is moving
            if player.is_moving:
                self.current_mode.render_game_objects(screen, interpolation)
            else:
                # Render without interpolation when player is stationary
                self.current_mode.render_game_objects(screen, 0)
            
            # Then render the fog of war
            self.update_fog_of_war(player.x, player.y)
            screen.blit(self.fog_surface, (0, 0))
            
            # Finally render the UI elements and overlays
            self.current_mode.render_ui_elements(screen)
            self.current_mode.render_state_overlay(screen)
        else:
            # For non-PlayMode screens, just use their normal render
            self.current_mode.render(screen, interpolation)

        self.update_fps()
        self.draw_fps(screen)
        pygame.display.flip()

    def run(self):
        next_game_tick = pygame.time.get_ticks()
        loops = 0

        while self.running:
            loops = 0
            while pygame.time.get_ticks() > next_game_tick and loops < self.MAX_FRAMESKIP:
                self.handle_events()
                self.current_mode.update()
                
                next_game_tick += self.SKIP_TICKS
                loops += 1

            # Calculate interpolation for smooth rendering
            interpolation = (pygame.time.get_ticks() + self.SKIP_TICKS - next_game_tick) / self.SKIP_TICKS

            self.render(self.screen, interpolation)
            self.clock.tick(FPS)  # Limit to 60 FPS

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Handle F11 key for fullscreen toggle
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                # Handle Alt+Enter for fullscreen toggle
                elif event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
                    self.toggle_fullscreen()
                else:
                    self.current_mode.handle_event(event)
            else:
                self.current_mode.handle_event(event)

    def update_fps(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.fps_update_time > 1000:  # Update FPS every second
            self.fps = self.clock.get_fps()
            self.fps_update_time = current_time

    def draw_fps(self, screen):
        # fps_surface = self.fps_font.render(f'FPS: {self.fps:.2f}', True, (255, 255, 255))
        # fps_rect = fps_surface.get_rect(midtop=(WIDTH // 2, 10))  # Position in mid top
        # screen.blit(fps_surface, fps_rect)
        pass

    def update_level_score(self, level, score):
        # If the level doesn't exist in scores yet, initialize it with 0
        if level not in self.level_scores:
            self.level_scores[level] = 0
            
        # Update the score for a level if it's higher than the current best
        if score > self.level_scores[level]:
            self.level_scores[level] = score

    def toggle_fullscreen(self):
        try:
            self.is_fullscreen = not self.is_fullscreen
            if self.is_fullscreen:
                self.window_width, self.window_height = self.screen.get_size()
                self.screen = pygame.display.set_mode(
                    (0, 0),
                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                )
            else:
                self.screen = pygame.display.set_mode(
                    (self.window_width, self.window_height),
                    pygame.HWSURFACE | pygame.DOUBLEBUF
                )
            
            # Get new screen dimensions
            current_width, current_height = self.screen.get_size()
            
            # Update fog surface for new dimensions
            self.fog_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            
            # Update viewport dimensions based on new screen size
            self.viewport_width = current_width / self.zoom
            self.viewport_height = (current_height - SCORE_AREA_HEIGHT) / self.zoom
            
            # Notify current mode of screen resize
            if hasattr(self.current_mode, 'on_screen_resize'):
                self.current_mode.on_screen_resize(current_width, current_height)
            
        except pygame.error:
            print("Failed to toggle fullscreen mode. Reverting to windowed mode.")
            self.is_fullscreen = False
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.HWSURFACE | pygame.DOUBLEBUF
            )


if __name__ == "__main__":
    game = Game()
    game.run()