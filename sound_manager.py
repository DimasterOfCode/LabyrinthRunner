import pygame
import math

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.sounds = {
            'game_over': self.create_sound(duration=1.0, start_freq=440, end_freq=0),
            'star_consume': self.create_sound(duration=0.2, start_freq=880, end_freq=1320),
            'coin_collect': self.create_sound(duration=0.1, start_freq=660, end_freq=880),
            'level_start': self.create_sound(duration=0.5, start_freq=440, end_freq=660)
        }

    def create_sound(self, duration, start_freq, end_freq):
        sample_rate = 22050
        num_samples = int(duration * sample_rate)
        
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            frequency = start_freq + (end_freq - start_freq) * t
            value = int(32767 * math.sin(2 * math.pi * frequency * t))
            buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"Sound '{sound_name}' not found.")

    def set_volume(self, sound_name, volume):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
        else:
            print(f"Sound '{sound_name}' not found.")

    def set_global_volume(self, volume):
        pygame.mixer.music.set_volume(volume)