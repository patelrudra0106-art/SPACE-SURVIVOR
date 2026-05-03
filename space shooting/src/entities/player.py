import pygame
import math
import random

from src.entities.Bullet import Bullet
from src.entities.HomingMissile import HomingMissile
from src.lib.game_utility import get_path
from src.screens.ui.health_bar import HealthBar
from src.abilities.dash_ability import DashAbility
from src.abilities.ultimate_ability import UltimateAbility
from src.config.config import (
    PLAYER_SPEED,
    PLAYER_HEALTH,
    PLAYER_SHOOT_DELAY,
    PLAYER_BULLET_DMG,
    PLAYER_BULLET_SPD,
    GOD_MODE,
)


class Player:

    player_x = 100
    player_y = 100
    player_width = 50
    player_height = 50
    player_speed = PLAYER_SPEED

    max_health = PLAYER_HEALTH
    health = max_health

    shoot_delay = PLAYER_SHOOT_DELAY
    time_since_last_shot = 0

    bullets: list[Bullet] = []

    images = []

    x1 = player_x
    y1 = player_y
    x2 = player_x + player_width
    y2 = player_y
    x3 = player_x + player_width / 2
    y3 = player_y + player_height

    is_invincible = False
    is_shooting = False

    has_shield = False
    triple_shot_active = False
    homing_active = False

    # Advanced mechanics
    super_meter = 0.0 # 0 to 100
    max_super = 100.0
    
    is_dashing = False
    
    is_ulting = False

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.invincible_timer = 0.0
        self.invincible_duration = 0.6
        # player_box hitbox
        self.player_box = pygame.Rect(
            self.player_x, self.player_y, self.player_width, self.player_height
        )

        self.health_regen = False

        # Bullet stats (instance vars so power-ups can modify them)
        self._base_bullet_speed = PLAYER_BULLET_SPD
        self._base_bullet_damage = PLAYER_BULLET_DMG
        self.bullet_speed = PLAYER_BULLET_SPD
        self.bullet_damage = PLAYER_BULLET_DMG

        # Run-based Progression (Roguelike)
        self.xp = 0
        self.run_level = 1
        self.xp_to_next_level = 10

        self.load_images()

        # player_box center for rotation
        self.cx = self.player_x + self.player_width / 2  # center x
        self.cy = self.player_y + self.player_height / 2  # center y
        self.angle = 0

        self.vx = 0.0
        self.vy = 0.0

        # Initialize base stats from meta
        self.apply_meta_upgrades()

        # Health bar
        self.health_bar = HealthBar(self.max_health, self.health, 10, 10)
        
        # Abilities
        self.abilities = {}
        unlocked = self.game.meta.data["unlocked_abilities"]
        if "dash" in unlocked:
            self.abilities["dash"] = DashAbility(self.game)
        if "ultimate" in unlocked:
            self.abilities["ultimate"] = UltimateAbility(self.game)

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.run_level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            self.game.events.emit("player_level_up")
    def apply_meta_upgrades(self):
        hp_lvl = self.game.meta.data["hp_level"]
        self.max_health = PLAYER_HEALTH + (hp_lvl - 1) * 20
        self.health = self.max_health

        fr_lvl = self.game.meta.data["fire_rate_level"]
        self.shoot_delay = PLAYER_SHOOT_DELAY * (0.9 ** (fr_lvl - 1))

    def rotate_point(self, x, y, angle):
        """Rotate a point around the player_box center"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        # Translate to origin
        dx = x - self.cx
        dy = y - self.cy
        # Rotate then translate back
        return (self.cx + dx * cos_a - dy * sin_a, self.cy + dx * sin_a + dy * cos_a)

    def update(self):
        mx, my = pygame.mouse.get_pos()
        # Angle from center to mouse (-pi to pi), offset by 90° so tip points up by default
        self.angle = math.atan2(my - self.cy, mx - self.cx) + math.pi / 2

        # Update health
        self.update_health()

        # Engine trails
        self.game.particle_manager.create_trail(self.cx, self.cy, self.angle)

        if self.invincible_timer > 0:
            self.invincible_timer -= self.game.dt

        # Update abilities
        for ability in self.abilities.values():
            ability.update(self.game.dt)

    def draw(self, surface=None):
        if surface is None:
            surface = self.screen

        # Define triangle pointing upward at origin (before rotation)
        tip = (self.cx, self.cy - self.player_height / 2)
        left = (self.cx - self.player_width / 2, self.cy + self.player_height / 2)
        right = (self.cx + self.player_width / 2, self.cy + self.player_height / 2)

        # Rotate all three points around center toward mouse
        points = [
            self.rotate_point(*tip, self.angle),
            self.rotate_point(*left, self.angle),
            self.rotate_point(*right, self.angle),
        ]

        # hitbox
        # pygame.draw.polygon(surface, (255, 255, 255), points)

        # Blink if invincible
        if self.invincible_timer > 0:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return

        scaled_image = pygame.transform.scale(
            self.get_image(), (int(self.player_width * 2), int(self.player_height * 2))
        )
        rotated_image = pygame.transform.rotate(scaled_image, math.degrees(-self.angle))
        surface.blit(rotated_image, rotated_image.get_rect(center=(self.cx, self.cy)))

        # Draw shield if active
        if self.has_shield:
            shield_color = (100, 255, 255, 120)
            pygame.draw.circle(surface, shield_color, (int(self.cx), int(self.cy)), int(self.player_width * 1.2), 2)
            # Inner glow
            pygame.draw.circle(surface, (100, 255, 255, 40), (int(self.cx), int(self.cy)), int(self.player_width * 1.3), 1)

        # Draw Ultimate Beam
        if self.is_ulting:
            # Giant beam from ship center in angle direction
            end_x = self.cx + math.cos(self.angle - math.pi/2) * 2000
            end_y = self.cy + math.sin(self.angle - math.pi/2) * 2000
            
            # Draw several layers for glow
            for i in range(3):
                width = 40 - i * 10
                color = (255, 255, 255) if i == 2 else (255, 200, 50)
                pygame.draw.line(surface, color, (self.cx, self.cy), (end_x, end_y), width)
            
            # Particles along the beam
            for _ in range(5):
                dist = random.random() * 800
                px = self.cx + math.cos(self.angle - math.pi/2) * dist
                py = self.cy + math.sin(self.angle - math.pi/2) * dist
                self.game.particle_manager.create_explosion(px, py, color=(255, 255, 100), count=1)

            # Damage logic for beam
            self.check_beam_collision(end_x, end_y)

        # Dash effects
        if self.is_dashing:
            # Ghosting effect
            ghost_color = (255, 255, 255, 100)
            pygame.draw.circle(surface, ghost_color, (int(self.cx), int(self.cy)), self.player_width, 1)

    def move(self):
        dt = self.game.dt
        keys = pygame.key.get_pressed()
        
        dir_x, dir_y = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dir_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dir_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dir_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dir_x += 1
        
        # Virtual Joystick Input
        if hasattr(self.game, 'virtual_controls') and self.game.virtual_controls.joy_active:
            dir_x, dir_y = self.game.virtual_controls.joy_vector
        else:
            # Normalize keyboard direction
            if dir_x != 0 or dir_y != 0:
                length = math.hypot(dir_x, dir_y)
                dir_x /= length
                dir_y /= length

        # Acceleration and friction for smooth movement
        acceleration = 2500.0
        friction = 0.85
        
        self.vx += dir_x * acceleration * dt
        self.vy += dir_y * acceleration * dt
        
        # Apply friction
        self.vx *= math.pow(friction, dt * 60)
        self.vy *= math.pow(friction, dt * 60)
        
        # Cap speed
        speed = math.hypot(self.vx, self.vy)
        if speed > self.player_speed:
            self.vx = (self.vx / speed) * self.player_speed
            self.vy = (self.vy / speed) * self.player_speed
            
        self.cx += self.vx * dt
        self.cy += self.vy * dt

        # Update collision rectangle to match center position
        self.player_box.x = self.cx - self.player_width / 2
        self.player_box.y = self.cy - self.player_height / 2

    def take_damage(self, damage):
        """Handle incoming damage, checking for shield first."""
        if self.is_dashing:
            return # Invincible during dash

        if self.has_shield:
            self.has_shield = False
            self.game.events.emit("shield_break", self.cx, self.cy)
            return

        if self.invincible_timer > 0:
            return

        self.health -= damage
        self.game.damage_taken += damage
        self.invincible_timer = self.invincible_duration
        self.game.events.emit("player_hit")

    def shoot(self):
        self.time_since_last_shot += self.game.dt
        mouse: tuple[bool, bool, bool] = pygame.mouse.get_pressed()
        
        # Virtual Fire Button or Mouse Click
        is_firing = mouse[0]
        if hasattr(self.game, 'virtual_controls'):
            if self.game.virtual_controls.buttons["fire"]["active"]:
                is_firing = True
            # Prevent shooting when clicking other UI buttons
            elif self.game.virtual_controls.joy_active or \
                 self.game.virtual_controls.buttons["dash"]["active"] or \
                 self.game.virtual_controls.buttons["ult"]["active"]:
                is_firing = False

        if is_firing and self.time_since_last_shot >= self.shoot_delay:
            self.time_since_last_shot = 0
            mx, my = pygame.mouse.get_pos()
            
            # Scaled damage: 10% increase per level
            level_multiplier = 1.0 + (self.game.game_level - 1) * 0.1
            scaled_damage = self.bullet_damage * level_multiplier

            def spawn_bullet(offset_angle=0):
                angle = math.atan2(my - self.cy, mx - self.cx) + offset_angle
                tx = self.cx + math.cos(angle) * 1000
                ty = self.cy + math.sin(angle) * 1000
                self.game.player_bullet_pool.get(self.cx, self.cy, tx, ty, (255, 155, 0), self.bullet_speed, scaled_damage)

            spawn_bullet(0) # Main bullet
            self.game.shots_fired += 1
            if self.triple_shot_active:
                spawn_bullet(-0.2) # Left
                spawn_bullet(0.2)  # Right
                self.game.shots_fired += 2

            if self.homing_active:
                # Spawn a homing missile occasionally
                if random.random() < 0.3:
                    # Homing missile doesn't use the pool right now, just append to enemies or handle separately.
                    # We can keep a local list or just skip it for now.
                    pass

            self.game.events.emit("player_shoot", self.cx, self.cy, self.angle)

    def check_beam_collision(self, end_x, end_y):
        """Destroy enemies touched by the beam."""
        for enemy in self.game.enemies[:]:
            # Simple line-to-point distance check
            # For brevity, we'll just check if the enemy is close enough to the beam line
            # or simply clear all enemies for a truly 'ultimate' feel if they are in front
            angle_to_enemy = math.atan2(enemy.cy - self.cy, enemy.cx - self.cx)
            diff = (angle_to_enemy - (self.angle - math.pi/2) + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) < 0.1: # Tight cone
                enemy.take_damage(20) # Balanced high DPS (approx 1200 per second)

    def load_images(self):
        self.images = []
        for i in range(4):
            img = pygame.image.load(
                get_path(f"player({i+1}).png", "images", "player")
            ).convert_alpha()
            self.images.append(img)

    def get_image(self):
        # 2 for no dmg
        # 3 for low dmg
        # 2 for medium dmg
        # 0 for critical dmg
        if self.health > self.max_health * 0.75:
            return self.images[2]
        elif self.health > self.max_health * 0.5:
            return self.images[3]
        elif self.health > self.max_health * 0.25:
            return self.images[1]
        else:
            return self.images[0]

    def update_health(self):
        if self.health_regen and self.health < self.max_health:
            if self.game.game_difficulty >= 8:
                self.health += 0.4
            elif self.game.game_difficulty >= 5:
                self.health += 0.2
            elif self.game.game_difficulty >= 2:
                self.health += 0.1
            else:
                self.health += 0.05
            
    def restore_health(self):
        self.health = min(self.health + 50, self.max_health)

    def reset(self):
        """Reset all player state for a new game."""
        self.apply_meta_upgrades()
        
        # Refresh abilities in case they were bought in shop
        unlocked = self.game.meta.data["unlocked_abilities"]
        if "dash" in unlocked and "dash" not in self.abilities:
            self.abilities["dash"] = DashAbility(self.game)
        if "ultimate" in unlocked and "ultimate" not in self.abilities:
            self.abilities["ultimate"] = UltimateAbility(self.game)
            
        self.health_bar.max_health = self.max_health
        self.player_speed = PLAYER_SPEED
        self.bullet_speed = self._base_bullet_speed
        self.bullet_damage = self._base_bullet_damage
        self.time_since_last_shot = 0
        self.cx = self.game.game_width // 2
        self.cy = self.game.game_height // 2
        self.player_box.center = (self.cx, self.cy)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0
        self.health_regen = False
        self.is_invincible = False
        self.has_shield = False
        self.triple_shot_active = False
        self.homing_active = False
        self.super_meter = 0
        self.is_dashing = False
        self.is_ulting = False
        for ability in self.abilities.values():
            ability.cooldown_timer = 0
            ability.duration_timer = 0
            ability.is_active = False
