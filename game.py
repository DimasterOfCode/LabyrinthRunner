import os
import sys

import pygame
import pygame.gfxdraw

from constants import WIDTH, HEIGHT, SCORE_AREA_HEIGHT, MAZE_WIDTH, CELL_SIZE, FPS
from game_modes import MenuMode, RunnerCustomizationMode, LevelEditorMode, PlayMode
from level_manager import LevelManager
from sound_manager import SoundManager  # Add this import

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Labyrinth Runner")
        self.clock = pygame.time.Clock()
        
        self.level_manager = LevelManager("levels.json")
        self.load_or_generate_levels()

        self.offset_x = (WIDTH - MAZE_WIDTH * CELL_SIZE) // 2
        self.offset_y = SCORE_AREA_HEIGHT
        self.running = True
        
        # Initialize modes dictionary
        self.modes = {}
        
        # Create instances of game modes
        self.modes["menu"] = MenuMode(self)
        self.modes["runner_customization"] = RunnerCustomizationMode(self)
        self.modes["level_editor"] = LevelEditorMode(self, self.level_manager)
        self.modes["play"] = PlayMode(self, self.level_manager)
        
        self.current_mode = self.modes["menu"]

        # Initialize the sound manager
        self.sound_manager = SoundManager()

        # Fixed timestep variables
        self.TICKS_PER_SECOND = 60
        self.SKIP_TICKS = 1000 / self.TICKS_PER_SECOND
        self.MAX_FRAMESKIP = 5

        self.fps_font = pygame.font.Font(None, 30)
        self.fps = 0
        self.fps_update_time = 0

    def play_game_over_sound(self):
        self.sound_manager.play_sound('game_over')

    def play_star_consume_sound(self):
        self.sound_manager.play_sound('star_consume')

    def set_mode(self, mode_name):
        self.current_mode = self.modes[mode_name]
        if mode_name == "play":
            self.modes["play"].init_game_objects()

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

            self.current_mode.render(self.screen, interpolation)  # Call render method of current mode
            self.update_fps()
            self.draw_fps(self.screen)
            pygame.display.flip()

            self.clock.tick(FPS)  # Limit to 60 FPS

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.current_mode.handle_event(event)

    def load_or_generate_levels(self):
        if os.path.exists(self.level_manager.levels_file):
            self.level_manager.load_levels_from_file()
        else:
            print("No levels file found. Entering Level Editor.")
            self.set_mode("level_editor")

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


if __name__ == "__main__":
    game = Game()
    game.run()