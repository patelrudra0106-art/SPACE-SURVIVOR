import pygame
from .health_boost import HealthBoost
from .Speed import SpeedBoost
from .fast_bullets import FastBullets
from .stronger_bullets import StrongerBullets
from .Shield import ShieldPowerUp
from .TripleShot import TripleShotPowerUp
from .HomingPowerUp import HomingPowerUp
from .BoltPower import BoltPowerUp
import random

EFFECT_DURATION = 10.0  # seconds before non-permanent power-ups expire


class PowerUpManager:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.max_power_ups = 3
        self.power_ups = []
        self.power_up_spawn_timer = 0
        self.power_up_types = [
            "health",
            "speed",
            "fast_bullets",
            "stronger_bullets",
            "shield",
            "triple_shot",
            "homing",
            "bolt",
        ]
        self.power_up_texts = {}

        # Active timed effects: list of {power_up, timer, player}
        self.active_effects: list[dict] = []

    def _random_position(self) -> tuple[int, int]:
        x = random.randint(50, self.game.game_width - 50)
        y = random.randint(50, self.game.game_height // 2)
        return x, y

    def add_power_up(self):
        # Don't spawn until score >= 10
        if self.game.game_score < 10:
            return

        if len(self.power_ups) >= self.max_power_ups:
            return

        self.power_up_spawn_timer -= self.game.dt
        if self.power_up_spawn_timer > 0:
            return

        # After difficulty 2, fixed 5s spawn interval; otherwise random
        if self.game.game_difficulty >= 2:
            self.power_up_spawn_timer = 5.0
        else:
            self.power_up_spawn_timer = random.uniform(5.0, 10.0)

        x, y = self._random_position()
        power_up_type: str = random.choice(self.power_up_types)

        if power_up_type == "health":
            self.power_ups.append(HealthBoost(x, y))
        elif power_up_type == "speed":
            self.power_ups.append(SpeedBoost(x, y))
        elif power_up_type == "fast_bullets":
            self.power_ups.append(FastBullets(x, y))
        elif power_up_type == "stronger_bullets":
            self.power_ups.append(StrongerBullets(x, y))
        elif power_up_type == "shield":
            self.power_ups.append(ShieldPowerUp(x, y))
        elif power_up_type == "triple_shot":
            self.power_ups.append(TripleShotPowerUp(x, y))
        elif power_up_type == "homing":
            self.power_ups.append(HomingPowerUp(x, y))
        elif power_up_type == "bolt":
            self.power_ups.append(BoltPowerUp(x, y))

    def draw(self, surface=None):
        if surface is None:
            surface = self.screen
        for power_up in self.power_ups:
            power_up.draw(surface)

    def update(self):
        self.add_power_up()
        for power_up in self.power_ups[:]:
            power_up.update()
            # Remove powerups that have drifted completely off the bottom of the screen
            if getattr(power_up, 'y', 0) > self.game.game_height + 100:
                self.power_ups.remove(power_up)

        # Tick down active timed effects
        self._update_effects()

    def _update_effects(self):
        """Expire non-permanent power-up effects after their timer runs out."""
        for effect in self.active_effects[:]:
            effect["timer"] -= self.game.dt
            if effect["timer"] <= 0:
                power_up = effect["power_up"]
                # Call expire to revert the effect
                if hasattr(power_up, "expire"):
                    power_up.expire(effect["player"])
                # Remove from HUD
                name = type(power_up).__name__
                self.power_up_texts.pop(name, None)
                self.active_effects.remove(effect)

    def check_collision(self, player):
        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(player.player_box):
                power_up.collected(player)
                self.power_ups.remove(power_up)
                self.game.audio_manager.play_power_up_sound()

                # Track for HUD display
                name = type(power_up).__name__
                self.power_up_texts[name] = {
                    "info": power_up.display_info(),
                    "image": power_up.frames[0] if power_up.frames else None
                }

                # If non-permanent, track for expiry
                if not power_up.is_permanent:
                    duration = getattr(power_up, "duration", EFFECT_DURATION)
                    self.active_effects.append({
                        "power_up": power_up,
                        "timer": duration,
                        "player": player,
                    })

    def reset(self):
        """Reset all power-up state for a new game."""
        # Expire all active effects immediately
        for effect in self.active_effects:
            power_up = effect["power_up"]
            if hasattr(power_up, "expire"):
                power_up.expire(effect["player"])
        self.active_effects.clear()
        self.power_ups.clear()
        self.power_up_texts.clear()
        self.power_up_spawn_timer = 0
