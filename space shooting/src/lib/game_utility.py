# ── Game state management ─────────────────────────────────────────────────

import os
import json

from src.config.config import PLAYER_HEALTH
from src.lib.game_state import GameState


def get_path(image_name: str, type: str = "", subfolder: str | None = None):
    # src/lib/game_utility.py → src/lib → src → project root
    _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if subfolder is None:
        return os.path.join(_PROJECT_ROOT, "assets", type, image_name)
    return os.path.join(_PROJECT_ROOT, "assets", type, subfolder, image_name)


def increase_difficulty(self):
    """Increase difficulty based on the current level."""
    # Difficulty is now tied to level, but we can still use this function 
    # to trigger level-up effects like restoring health.
    last_level = getattr(self, "_last_level_reached", 1)
    if self.game_level > last_level:
        self.player.restore_health()
        self._last_level_reached = self.game_level


def update_level(self):
    """Update game level/difficulty based on mode, score, and DDS metrics."""
    # Calculate Dynamic Difficulty
    accuracy = 0.0
    if self.shots_fired > 0:
        accuracy = self.shots_hit / self.shots_fired

    # Base difficulty floor
    base_diff = float(self.game_level) if self.game_mode == "level" else 1.0
    
    # DDS Formula
    raw_dds = base_diff + (self.game_score * 0.1) + (self.time_alive * 0.05) + (accuracy * 2.0) - (self.damage_taken * 0.02)
    
    # Ensure difficulty never drops below base and updates dynamically
    new_difficulty = max(base_diff, raw_dds)
    
    # Update if significantly changed (prevent jitter) or just continuously assign
    self.game_difficulty = new_difficulty

    # Pause progression during boss fights
    if self.enemy_spawner.boss_alive:
        return
        
    if self.game_mode == "level":
        # Specific number of kills per level (level * 10)
        kills_needed = self.game_level * 10
        if self.game_score >= kills_needed:
            self.game_level += 1
            self.increase_difficulty()
            # Trigger level up notification on HUD
            self.hud.trigger_level_up()
            # Trigger boss warning if multiple of 5
            if self.game_level % 5 == 0:
                self.hud.trigger_boss_warning()
            # Auto-save progress on level up
            save_game_state(self)
            # Update background theme
            self.background.update_theme_by_level(self.game_level)
            # Reset score for next level
            self.game_score = 0
            
    elif self.game_mode == "infinite" or self.game_mode == "endless":
        # Sync level to integer difficulty for endless mode so bosses spawn
        current_level = int(self.game_difficulty)
        if current_level > getattr(self, "_last_endless_level", 1):
            self.game_level = current_level
            self.increase_difficulty()
            self._last_endless_level = current_level
            if self.game_level % 5 == 0:
                self.hud.trigger_boss_warning()

def game_start(self, resume=True, mode=None):
    """Start a new game or resume from saved state."""
    self.state = GameState.PLAYING
    
    if mode is not None:
        self.game_mode = mode
    
    if not resume:
        self.game_score = 0
        self.game_level = 1
        self.game_difficulty = 1
    else:
        # Load state if exists, otherwise defaults to level 1
        load_game_state(self)

    self._last_difficulty_threshold = 0

    # Reset all subsystems
    self.player.reset()
    self.enemy_spawner.reset()
    self.power_up_manager.reset()
    self.hud.reset()
    self.background.reset()

    self.audio_manager.play_game_music()


def game_quit(self):
    """Quit the game entirely."""
    save_game_state(self)
    self.running = False


def pause_game(self):
    """Toggle pause state."""
    if self.state == GameState.PAUSED:
        self.state = GameState.PLAYING
    elif self.state == GameState.PLAYING:
        self.state = GameState.PAUSED


def game_restart(self):
    """Restart the game after game over."""
    self.game_start()


def show_game_menu(self):
    """Return to main menu."""
    self.state = GameState.MENU

    # Reset difficulty
    self.game_difficulty = 1
    self._last_difficulty_threshold = 0
    self.game_level = 1

    # Reset all subsystems
    self.player.reset()
    self.enemy_spawner.reset()
    self.power_up_manager.reset()
    self.hud.reset()
    self.background.reset()

    self.audio_manager.play_menu_music()


def trigger_game_over(self):
    """Called when the player dies."""
    self.state = GameState.GAME_OVER

    # Update high score
    if self.game_score > self.game_high_score:
        self.game_high_score = self.game_score
        save_high_score(self)
    
    # Save current level progress
    save_game_state(self)

    self.audio_manager.play_game_over_sound()


def save_high_score(self):
    """Save high score to a local file."""
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "high_score.txt")
        with open(path, "w") as f:
            f.write(str(self.game_high_score))
    except Exception as e:
        print(f"Error saving high score: {e}")


def load_high_score(self):
    """Load high score from a local file."""
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "high_score.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.game_high_score = int(f.read().strip())
    except Exception as e:
        print(f"Error loading high score: {e}")
        self.game_high_score = 0


def save_game_state(self):
    """Save current level and score to a JSON file."""
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "save_game.json")
        data = {
            "level": self.game_level,
            "score": self.game_score,
            "mode": self.game_mode
        }
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving game state: {e}")


def load_game_state(self):
    """Load level and score from a JSON file."""
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "save_game.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.game_level = data.get("level", 1)
                self.game_score = data.get("score", 0)
                self.game_mode = data.get("mode", "level")
                self.game_difficulty = self.game_level
    except Exception as e:
        print(f"Error loading game state: {e}")


def trigger_bomb(self):
    """Trigger a screen-clearing bomb at the cost of some points."""
    if self.game_score >= 10:
        self.game_score -= 10
        
        # Create a massive explosion and shake
        self.screen_shake.trigger(30, 0.5)
        self.particle_manager.create_explosion(self.game_width // 2, self.game_height // 2, color=(255, 255, 255), count=100)
        
        # Destroy all small enemies
        from src.entities.BossEnemy import BossEnemy
        for enemy in self.enemies[:]:
            if not isinstance(enemy, BossEnemy):
                self.particle_manager.create_explosion(enemy.cx, enemy.cy)
                self.enemies.remove(enemy)
        
        self.audio_manager.play_destroy_sound()
