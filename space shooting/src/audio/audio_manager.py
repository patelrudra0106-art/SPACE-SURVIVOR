import pygame

from src.lib.game_utility import get_path
from src.config.config import BULLET_SFX_VOLUME, POWER_UP_SFX_VOLUME, GAME_OVER_SFX_VOLUME


class AudioManager:
    def __init__(self):
        pygame.mixer.init()

        # ── Music paths (streamed via pygame.mixer.music) ────────────────────
        self.menu_music_path = get_path("menu.mp3", "audio")
        self.game_music_tracks = [
            get_path("game.mp3", "audio"),
            get_path("melodyayresgriffiths-cosmos-space-game-action-shooter-astronauts-scifi-aliens-142978.mp3", "audio")
        ]

        # ── Sound effects (concurrent via pygame.mixer.Sound) ────────────────
        self.game_over_sfx = pygame.mixer.Sound(get_path("game_over.mp3", "audio"))
        self.power_up_sfx = pygame.mixer.Sound(get_path("power_up.mp3", "audio"))
        self.bullet_sfx = pygame.mixer.Sound(get_path("bullet.mp3", "audio"))
        self.destroy_sfx = pygame.mixer.Sound(get_path("destroy.mp3", "audio"))

        # Volume from config
        self.bullet_sfx.set_volume(BULLET_SFX_VOLUME)
        self.game_over_sfx.set_volume(GAME_OVER_SFX_VOLUME)
        self.power_up_sfx.set_volume(POWER_UP_SFX_VOLUME)
        self.destroy_sfx.set_volume(0.3)

    # ── Music controls ───────────────────────────────────────────────────────

    def play_menu_music(self):
        """Play the menu background music on loop."""
        pygame.mixer.music.load(self.menu_music_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)  # -1 = loop forever

    def play_game_music(self):
        """Play a random in-game background music track on loop."""
        import random
        track = random.choice(self.game_music_tracks)
        pygame.mixer.music.load(track)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)

    def stop_music(self):
        """Stop whatever music is currently playing."""
        pygame.mixer.music.stop()

    # ── SFX controls ─────────────────────────────────────────────────────────

    def play_game_over_sound(self):
        """Play the game-over sting and lower background music."""
        pygame.mixer.music.set_volume(0.2)  # keep music at 20%
        self.game_over_sfx.play()

    def play_power_up_sound(self):
        """Play the power-up pickup sound."""
        self.power_up_sfx.play()

    def play_bullet_sound(self):
        """Play the bullet fire sound."""
        self.bullet_sfx.play()

    def play_destroy_sound(self):
        """Play the enemy destroyed sound."""
        self.destroy_sfx.play()

    def play_hurt_sound(self):
        """Play the player hurt sound."""
        # Fallback to destroy sound if a specific hurt sound isn't available
        self.destroy_sfx.play()
