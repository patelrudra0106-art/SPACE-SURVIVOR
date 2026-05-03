import pygame
import math

class XPGem:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.value = value
        self.radius = 6 if value == 1 else 10
        self.color = (50, 200, 255) if value == 1 else (255, 50, 200)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        
        # Magnetism
        self.magnet_radius = 150
        self.speed = 0

    def update(self, dt, player):
        # Calculate distance to player
        dx = player.cx - self.x
        dy = player.cy - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.magnet_radius:
            # Move towards player
            self.speed += 500 * dt
            if dist > 0:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt
        else:
            # Drift down slowly
            self.speed = 0
            self.y += 20 * dt
            
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Outer glow
        glow_radius = self.radius + 3
        glow_color = (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_radius)
        
        # Inner core
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Highlight
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 2), int(self.y - 2)), self.radius // 2)
