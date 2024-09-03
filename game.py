import os
import sys
import math  # Add this import

import pygame
import pygame.gfxdraw

from constants import WIDTH, HEIGHT, SCORE_AREA_HEIGHT, MAZE_WIDTH, CELL_SIZE, FPS
from game_modes import MenuMode, RunnerCustomizationMode, LevelEditorMode, PlayMode
from level_manager import LevelManager


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

        # Initialize the mixer for sound playback
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        # Create sounds
        self.game_over_sound = self.create_game_over_sound()
        self.star_consume_sound = self.create_star_consume_sound()

        # Fixed timestep variables
        self.TICKS_PER_SECOND = 60
        self.SKIP_TICKS = 1000 / self.TICKS_PER_SECOND
        self.MAX_FRAMESKIP = 5

        self.fps_font = pygame.font.Font(None, 30)
        self.fps = 0
        self.fps_update_time = 0

    def create_game_over_sound(self):
        duration = 1  # Duration of the sound in seconds
        sample_rate = 22050  # Sample rate in Hz
        num_samples = int(duration * sample_rate)
        
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            frequency = 440 * (1 - t)  # Start at 440 Hz and decrease
            value = int(32767 * math.sin(2 * math.pi * frequency * t))
            # Convert to 16-bit little-endian binary data
            buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def create_star_consume_sound(self):
        duration = 0.2  # Duration of the sound in seconds
        sample_rate = 22050  # Sample rate in Hz
        num_samples = int(duration * sample_rate)
        
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            frequency = 880 + 440 * t  # Start at 880 Hz and increase to 1320 Hz
            value = int(32767 * math.sin(2 * math.pi * frequency * t))
            # Convert to 16-bit little-endian binary data
            buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def play_game_over_sound(self):
        self.game_over_sound.play()

    def play_star_consume_sound(self):
        self.star_consume_sound.play()

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