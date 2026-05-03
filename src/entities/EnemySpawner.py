import pygame
import random

from src.entities.BulletEnemy import BulletEnemy
from src.entities.Enemy import Enemy
from src.entities.BossEnemy import BossEnemy
from src.entities.TankEnemy import TankEnemy
from src.entities.FastEnemy import FastEnemy
from src.config.config import SPAWN_INTERVAL, BOSS_SPAWN_SCORE


class EnemySpawner:

    enemy_types: list[str] = ["normal", "shooter", "tank", "fast"]
    
    max_enemies: int = 10

    def __init__(self, game):
        self.game = game
        self.enemies = game.enemies

        self.boss_alive = False

        self.spawn_timer = 0
        self.spawn_interval = SPAWN_INTERVAL
        self._last_boss_level = -1

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Less aggressive spawning: base SPAWN_INTERVAL divided by a factor of difficulty and level
        # Capped at 0.3s minimum to keep it playable
        self.spawn_interval = max(0.3, SPAWN_INTERVAL / (1 + (self.game.game_difficulty * 0.1) + (self.game.game_level * 0.1)))

        # Scale max enemies with level, cap at 12 to prevent clutter
        self.max_enemies = min(12, 5 + self.game.game_level)
        if self.boss_alive:
            self.max_enemies = 3

    def spawn_enemy(self):
        if self.game.state.name == "PLAYING":
            if len(self.enemies) >= self.max_enemies:
                return

            # Boss spawning: Every 5 levels
            if self.game.game_level % 5 == 0 and self.game.game_level != self._last_boss_level:
                # Clear all regular enemies for a 1v1 boss fight
                self.enemies.clear()
                boss = BossEnemy(self.game)
                self.enemies.append(boss)
                self.boss_alive = True
                self._last_boss_level = self.game.game_level
                self.game.events.emit("boss_spawned")
                
                # Boss Title Card
                boss_name = f"VANGUARD-LEVEL {self.game.game_level // 5}"
                if self.game.game_level == 5: boss_name = "THE IRON DREADNOUGHT"
                elif self.game.game_level == 10: boss_name = "VOID REAPER"
                elif self.game.game_level == 15: boss_name = "GALACTIC OMEGA"
                self.game.particle_manager.trigger_boss_title(boss_name)
                
                return

            # No other enemies during boss fight
            if self.boss_alive:
                return

            # Variety increases with level
            available_types = ["normal", "shooter"]
            if self.game.game_level >= 2:
                available_types.append("fast")
            if self.game.game_level >= 4:
                available_types.append("tank")

            enemy_choice: str = random.choice(available_types)
            if enemy_choice == "normal":
                self.enemies.append(Enemy(self.game))
            elif enemy_choice == "shooter":
                self.enemies.append(BulletEnemy(self.game))
            elif enemy_choice == "tank":
                self.enemies.append(TankEnemy(self.game))
            elif enemy_choice == "fast":
                self.enemies.append(FastEnemy(self.game))

    def reset(self):
        """Reset spawner state for a new game."""
        self.enemies.clear()
        self._last_boss_level = -1
        self.boss_alive = False
        self.spawn_timer = 0
        self.spawn_interval = SPAWN_INTERVAL
