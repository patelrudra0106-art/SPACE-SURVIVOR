import pygame
import math
import random

from src.screens.ui import health_bar
from src.lib.game_utility import get_path
from src.config.config import ENEMY_SPEED, ENEMY_HEALTH, ENEMY_DMG


class Enemy:
    def __init__(self, game, width: int = 50, height: int = 50, health: int = ENEMY_HEALTH):
        self.game = game
        self.cx = 0
        self.cy = 0
        self.angle = 0
        edge = random.randint(0, 3)
        self.width = width
        self.height = height

        self.give_dmg = ENEMY_DMG
        
        # Scaling enemy stats by level
        # +50% health per level, +5% speed per level
        level_scale_h = 1.0 + (game.game_level - 1) * 0.5
        level_scale_s = 1.0 + (game.game_level - 1) * 0.05
        
        self.speed = ENEMY_SPEED * level_scale_s
        self.max_health = health * level_scale_h
        self.health = self.max_health
        
        # damage update from game difficulty
        if self.game.game_difficulty >= 4:
            self.give_dmg = max(1, self.game.game_difficulty // 3) * ENEMY_DMG

        self.rect = pygame.Rect(
            self.cx - self.width / 2, self.cy - self.height / 2, self.width, self.height
        )

        self.health_bar = health_bar.HealthBar(self.health, self.max_health, self.cx, self.cy - 10, 50, 5)

        if edge == 0:  # top
            self.cx = random.randint(0, game.game_width)
            self.cy = -self.height
        elif edge == 1:  # bottom
            self.cx = random.randint(0, game.game_width)
            self.cy = game.game_height + self.height
        elif edge == 2:  # left
            self.cx = -self.width
            self.cy = random.randint(0, game.game_height)
        else:  # right
            self.cx = game.game_width + self.width
            self.cy = random.randint(0, game.game_height)

        self.angle = 0

        self.color = (255, 0, 0)
        
        # State machine
        self.state = "IDLE"
        self.state_timer = 0.5  # brief idle upon spawn

        # Load enemy image
        self.image = self.load_enemy_image()

    def update(self, dt):
        if self.state == "IDLE":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "CHASE"
        elif self.state == "CHASE":
            self.chase_player(dt)
        elif self.state == "RETREAT":
            self.retreat_from_player(dt)
        elif self.state == "STRAFE":
            self.strafe_player(dt)

    def chase_player(self, dt):
        player_x, player_y = self.game.player.cx, self.game.player.cy
        dx = player_x - self.cx
        dy = player_y - self.cy
        dist = math.hypot(dx, dy)

        # angle calculation
        self.angle = math.atan2(dy, dx) + math.pi / 2

        if dist > 0:
            self.cx += (dx / dist) * self.speed * dt
            self.cy += (dy / dist) * self.speed * dt
            self.rect.center = (self.cx, self.cy)

    def strafe_player(self, dt):
        player_x, player_y = self.game.player.cx, self.game.player.cy
        dx = player_x - self.cx
        dy = player_y - self.cy
        dist = math.hypot(dx, dy)
        self.angle = math.atan2(dy, dx) + math.pi / 2
        
        if dist > 0:
            # Perpendicular vector
            px = -dy / dist
            py = dx / dist
            strafe_dir = getattr(self, 'strafe_dir', 1)
            self.cx += px * self.speed * strafe_dir * dt
            self.cy += py * self.speed * strafe_dir * dt
            self.rect.center = (self.cx, self.cy)
            
    def retreat_from_player(self, dt):
        player_x, player_y = self.game.player.cx, self.game.player.cy
        dx = player_x - self.cx
        dy = player_y - self.cy
        dist = math.hypot(dx, dy)
        self.angle = math.atan2(dy, dx) + math.pi / 2
        
        if dist > 0:
            self.cx -= (dx / dist) * self.speed * dt
            self.cy -= (dy / dist) * self.speed * dt
            self.rect.center = (self.cx, self.cy)


    def draw(self, screen):
        # Draw enemy image (scaled and rotated toward player)
        scaled = pygame.transform.scale(self.image, (self.width * 2, self.height * 2))
        rotated = pygame.transform.rotate(scaled, math.degrees(-self.angle))
        rotated_rect = rotated.get_rect(center=(self.cx, self.cy))
        screen.blit(rotated, rotated_rect)

        # health bar check
        if self.health > 0 and self.health < self.max_health:
            self.health_bar.draw(screen, self.health, self.rect.x, self.rect.y - 10)

    def take_damage(self, damage):
        self.health -= damage
        
        # Trigger floating damage number
        is_crit = random.random() < 0.1 # 10% chance for a "Crit" look
        final_dmg = int(damage)
        self.game.particle_manager.create_damage_number(self.cx, self.cy - 20, final_dmg, is_crit)
        
        if self.health <= 0:
            self.game.game_score += 1
            # +3 health on kill
            self.game.player.health = min(
                self.game.player.health + 3, self.game.player.max_health
            )
            # Increment super meter
            self.game.player.super_meter = min(
                self.game.player.super_meter + 5.0, self.game.player.max_super
            )
            self.game.events.emit("enemy_killed", self.cx, self.cy)
            self.game.enemies.remove(self)

    def rotate_point(self, x, y, angle):
        """Rotate a point around the player_box center"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        dx = x - self.cx
        dy = y - self.cy
        return (
            self.cx + dx * cos_a - dy * sin_a,
            self.cy + dx * sin_a + dy * cos_a
        )

    def load_enemy_image(self):
        """Load the standard enemy image. Subclasses can override."""
        img = pygame.image.load(
            get_path("enemy.png", "images", "enemies")
        ).convert_alpha()
        return img
