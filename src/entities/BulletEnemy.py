import pygame
from src.entities.Enemy import Enemy
from src.entities.Bullet import Bullet
from src.config.config import BULLET_ENEMY_BULLET_DMG, BULLET_ENEMY_BULLET_SPD , GOD_MODE
from src.lib.game_utility import get_path

class BulletEnemy(Enemy):
    shoot_delay = 0.5
    time_since_last_shot = 0

    def __init__(self, game):
        super().__init__(game, width=50, height=50, health=100)
        self.bullet_speed = BULLET_ENEMY_BULLET_SPD
        self.bullet_damage = 2
        self.bullet_color = (255, 255, 0)
        self.dt = game.dt
        self.screen = game.screen
        import random
        self.strafe_dir = random.choice([-1, 1])

    def load_enemy_image(self):
        img = pygame.image.load(
            get_path("shooting_enemy.png", "images", "enemies")
        ).convert_alpha()
        return img

    def update(self, dt):
        import math
        player_x, player_y = self.game.player.cx, self.game.player.cy
        dist = math.hypot(player_x - self.cx, player_y - self.cy)
        
        if self.state != "IDLE":
            if dist < 150:
                self.state = "RETREAT"
            elif dist < 300:
                self.state = "STRAFE"
            else:
                self.state = "CHASE"
                
        super().update(dt)
        self.dt = dt
        self.shoot()

        # update bullet damage based on game difficulty
        self.bullet_damage = self.game.game_difficulty * 2

    def draw(self, screen):
        super().draw(screen)

    def take_damage(self, damage):
        super().take_damage(damage)

    def shoot(self):
        self.time_since_last_shot += self.game.dt

        is_in_screen: bool = False
        if (
            self.cx < self.game.game_width
            or self.cx > 0
            and self.cy < self.game.game_height
            or self.cy > 0
        ):
            is_in_screen = True

        if self.time_since_last_shot >= self.shoot_delay and is_in_screen:
            self.time_since_last_shot = 0
            self.game.enemy_bullet_pool.get(
                self.cx,
                self.cy,
                self.game.player.cx,
                self.game.player.cy,
                (255, 255, 0),
                BULLET_ENEMY_BULLET_SPD,
                BULLET_ENEMY_BULLET_DMG,
            )
