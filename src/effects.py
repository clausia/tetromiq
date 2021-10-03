from pathlib import Path
import pygame


class Effects:

    def __init__(self):
        self.bg_music = pygame.mixer.Sound(Path('./resources/music.mp3'))
        self.bg_music.set_volume(0.3)
        self.bg_music.play(loops=-1)
        self.line_created_sound = pygame.mixer.Sound(Path('./resources/line-created.wav'))
        self.piece_moved_sound = pygame.mixer.Sound(Path('./resources/piece-moved.wav'))
        self.piece_moved_sound.set_volume(0.1)
        self.piece_rotated_sound = pygame.mixer.Sound(Path('./resources/piece-rotated.wav'))
        self.piece_split_sound = pygame.mixer.Sound(Path('./resources/piece-split.wav'))
        self.superposition_exchange_sound = pygame.mixer.Sound(Path('./resources/superposition-control.wav'))
        self.level_up_sound = pygame.mixer.Sound(Path('./resources/next-level.mp3'))
        self.level_up_sound.set_volume(0.9)
        self.music_muted = False
        self.sound_muted = False

    def mute_unmute_music(self):
        if not self.music_muted:
            pygame.mixer.pause()
        elif self.music_muted:
            pygame.mixer.unpause()
        self.music_muted = not self.music_muted

    def mute_unmute_sound(self):
        self.sound_muted = not self.sound_muted

    def play_line_created_sound(self):
        if not self.sound_muted:
            self.line_created_sound.play()

    def play_piece_rotated_sound(self):
        if not self.sound_muted:
            self.piece_rotated_sound.play()

    def play_piece_moved_sound(self):
        if not self.sound_muted:
            self.piece_moved_sound.play()

    def play_piece_split_sound(self):
        if not self.sound_muted:
            self.piece_split_sound.play()

    def play_superposition_exchange_sound(self):
        if not self.sound_muted:
            self.superposition_exchange_sound.play()

    def play_level_up_sound(self):
        if not self.sound_muted:
            self.level_up_sound.play(1)