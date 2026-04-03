import pygame
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.current_track = None

    def play_ambient(self, name: str):
        if self.current_track == name:
            return

        path = f"data/audio/{name}.ogg"
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1) # Loop forever
                self.current_track = name
            except Exception as e:
                print(f"Failed to play audio {name}: {e}")
        else:
            # Silent fallback or placeholder
            print(f"Audio file not found: {path}")

    def stop(self):
        pygame.mixer.music.stop()
        self.current_track = None
