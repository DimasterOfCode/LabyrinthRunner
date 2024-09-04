import pygame
import math

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.game_over_sound = self.create_game_over_sound()
        self.star_consume_sound = self.create_star_consume_sound()

    def create_game_over_sound(self):
        duration = 1  # Duration of the sound in seconds
        sample_rate = 22050  # Sample rate in Hz
        num_samples = int(duration * sample_rate)
        
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            frequency = 440 * (1 - t)  # Start at 440 Hz and decrease
            value = int(32767 * math.sin(2 * math.pi * frequency * t))
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
            buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def play_game_over_sound(self):
        self.game_over_sound.play()

    def play_star_consume_sound(self):
        self.star_consume_sound.play()