import pygame
import math

from src.lib.game_utility import get_path


class Bullet:
    def __init__(self):
        self.active = False
        self.width = 25
        self.height = 25
        self.image = None
        self.load_image()
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        info = pygame.display.Info()
        self.screen_w = info.current_w
        self.screen_h = info.current_h

    def spawn(self, x, y, target_x, target_y, color, speed, dmg):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.radius = 5
        self.color = color
        self.speed = speed
        self.damage = dmg

        self.rect.topleft = (self.x, self.y)

        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Subtle outer glow
        glow_color = (max(0, self.color[0]-100), max(0, self.color[1]-100), max(0, self.color[2]-100))
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), self.radius + 3)
        # Inner bright core
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw the actual bullet image sprite on top of the glow
        if self.image:
            screen.blit(self.image, self.rect)

    def is_off_canvas(self):
        if self.x < 0 or self.x > self.screen_w or self.y < 0 or self.y > self.screen_h:
            return True
        return False

    def check_collision(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                return True  # bullet is consumed on hit
        return False

    def load_image(self):
        self.image = pygame.image.load(
            get_path("bullet.png", "images", "bullets")
        ).convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
