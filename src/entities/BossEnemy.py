import pygame
import math
import random

from src.entities.Enemy import Enemy
from src.entities.Bullet import Bullet
from src.lib.game_utility import get_path
from src.config.config import (
    BOSS_SPEED,
    BOSS_HEALTH,
    BOSS_DMG,
    BOSS_BULLET_DMG,
    BOSS_BULLET_SPD,
    BOSS_SHOOT_DELAY,
    GOD_MODE
)


class BossEnemy(Enemy):
    _last_boss_index = None  # class-level tracker to avoid reusing the same image

    def __init__(self, game):
        # Scale boss stats by level - Bosses get MUCH tougher
        # Level 5 boss = 5x base health, Level 10 = 10x base health
        level_multiplier = float(game.game_level)
        scaled_health = BOSS_HEALTH * level_multiplier
        
        super().__init__(game, width=150, height=150, health=scaled_health)
        
        # Cap boss speed so it doesn't instantly teleport to player at high levels
        raw_speed = BOSS_SPEED * (1.0 + (game.game_level - 1) * 0.15)
        self.speed = min(BOSS_SPEED * 2.0, raw_speed)
        
        # Scale collision damage so it actually hurts the player at high levels
        self.give_dmg = BOSS_DMG * (1.0 + (game.game_level - 1) * 0.5)
        
        self.bullet_speed = BOSS_BULLET_SPD
        self.bullet_damage = BOSS_BULLET_DMG * (1.0 + (game.game_level - 1) * 0.4)
        self.bullet_color = (255, 255, 20)
        self.dt = game.dt
        self.screen = game.screen
        self.shoot_delay = BOSS_SHOOT_DELAY
        self.time_since_last_shot = 0

        # Pick a random boss image, avoiding the last one used
        self.image = self.load_boss_image()
        self.original_image = self.image.copy()
        self.phase2 = False
        self.spiral_angle = 0.0

    
        

    def draw(self, screen):
        # Draw boss image (scaled and rotated toward player)
        scaled = pygame.transform.scale(self.image, (self.width * 2, self.height * 2))
        rotated = pygame.transform.rotate(scaled, math.degrees(-self.angle))
        rotated_rect = rotated.get_rect(center=(self.cx, self.cy))
        screen.blit(rotated, rotated_rect)

        # Health bar
        if self.health > 0 and self.health < self.max_health:
            self.health_bar.draw(screen, self.health, self.rect.x, self.rect.y - 10)

        self.shoot()

        self.shoot()

    def load_boss_image(self):
        """Load a random boss image (boss1.png - boss5.png), never reusing the last one."""
        choices = [i for i in range(1, 6) if i != BossEnemy._last_boss_index]
        picked = random.choice(choices)
        BossEnemy._last_boss_index = picked
        img = pygame.image.load(
            get_path(f"boss{picked}.png", "images", "bosses")
        ).convert_alpha()
        return img

    def take_damage(self, damage):
        super().take_damage(damage)
        if self.health <= 0:
            self.game.enemy_spawner.boss_alive = False
            # Automatically advance to next level on boss kill
            self.game.game_level += 1
            self.game.game_difficulty = self.game.game_level
            self.game.increase_difficulty()
            self.game.hud.trigger_level_up()
            self.game.save_game_state()
            
            self.game.enemy_spawner.max_enemies = 10
            self.game.events.emit("boss_killed", self.cx, self.cy)



    def shoot(self):
        self.time_since_last_shot += self.game.dt

        is_in_screen: bool = False
        if (
            0 <= self.cx <= self.game.game_width
            and 0 <= self.cy <= self.game.game_height
        ):
            is_in_screen = True

        # Check for phase 2 transition
        if not self.phase2 and self.health <= self.max_health * 0.5:
            self.phase2 = True
            self.shoot_delay = BOSS_SHOOT_DELAY * 0.5
            self.speed = BOSS_SPEED * 1.5
            self.game.events.emit("boss_phase2", self.cx, self.cy)

        # Pulse red in Phase 2
        if self.phase2:
            t = pygame.time.get_ticks() / 100.0
            pulse = int((math.sin(t) + 1) / 2 * 100)
            self.image = self.original_image.copy()
            self.image.fill((255, 255 - pulse, 255 - pulse), special_flags=pygame.BLEND_RGB_MULT)

        if self.time_since_last_shot >= self.shoot_delay and is_in_screen:
            self.time_since_last_shot = 0
            
            # Base angle towards player
            base_angle = math.atan2(self.game.player.cy - self.cy, self.game.player.cx - self.cx)
            
            if not self.phase2:
                # Phase 1: 3-way wave
                offsets = [-0.3, 0, 0.3]
                for offset in offsets:
                    tx = self.cx + math.cos(base_angle + offset) * 1000
                    ty = self.cy + math.sin(base_angle + offset) * 1000
                    self.game.enemy_bullet_pool.get(self.cx, self.cy, tx, ty, (255, 255, 0), BOSS_BULLET_SPD, BOSS_BULLET_DMG)
            else:
                # Phase 2: 360 Degree Burst + Targeted shot
                self.spiral_angle += 0.2
                # 12-way 360 degree burst
                for i in range(12):
                    angle = self.spiral_angle + (i * math.pi / 6)
                    tx = self.cx + math.cos(angle) * 1000
                    ty = self.cy + math.sin(angle) * 1000
                    self.game.enemy_bullet_pool.get(self.cx, self.cy, tx, ty, (255, 50, 50), BOSS_BULLET_SPD * 0.8, BOSS_BULLET_DMG)
                
                # And one targeted shot
                tx = self.cx + math.cos(base_angle) * 1000
                ty = self.cy + math.sin(base_angle) * 1000
                self.game.enemy_bullet_pool.get(self.cx, self.cy, tx, ty, (255, 255, 0), BOSS_BULLET_SPD * 1.5, BOSS_BULLET_DMG)
