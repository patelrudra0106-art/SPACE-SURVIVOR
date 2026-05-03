import pygame
import math
from src.lib.game_utility import get_path

class HomingMissile:
    def __init__(self, x, y, game, speed=300, dmg=50):
        self.game = game
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = dmg
        self.radius = 6
        self.color = (255, 100, 0)
        self.angle = 0
        self.target = None
        self.turn_speed = 0.1 # Radians per frame-ish

        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        info = pygame.display.Info()
        self.screen_w = info.current_w
        self.screen_h = info.current_h

    def find_target(self):
        if not self.game.enemies:
            self.target = None
            return

        # Find closest enemy
        closest_dist = float('inf')
        for enemy in self.game.enemies:
            dist = math.hypot(enemy.cx - self.x, enemy.cy - self.y)
            if dist < closest_dist:
                closest_dist = dist
                self.target = enemy

    def update(self, dt):
        if self.target not in self.game.enemies:
            self.find_target()

        if self.target:
            target_angle = math.atan2(self.target.cy - self.y, self.target.cx - self.x)
            # Smoothly rotate towards target
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * self.turn_speed

        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self.rect.center = (self.x, self.y)

        # Particle trail
        self.game.particle_manager.create_trail(self.x, self.y, self.angle + math.pi/2)

    def draw(self, screen):
        # Draw a triangle pointing in the angle direction
        points = [
            (self.x + math.cos(self.angle) * 15, self.y + math.sin(self.angle) * 15),
            (self.x + math.cos(self.angle + 2.5) * 10, self.y + math.sin(self.angle + 2.5) * 10),
            (self.x + math.cos(self.angle - 2.5) * 10, self.y + math.sin(self.angle - 2.5) * 10),
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.circle(screen, (255, 200, 50), (int(self.x), int(self.y)), 3)

    def is_off_canvas(self):
        return self.x < -100 or self.x > self.screen_w + 100 or self.y < -100 or self.y > self.screen_h + 100

    def check_collision(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.game.particle_manager.create_explosion(self.x, self.y, color=(255, 100, 0), count=20)
                return True
        return False
