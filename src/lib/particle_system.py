import pygame
import random
import math

class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, duration, size):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.duration = duration
        self.initial_duration = duration
        self.size = size

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.duration -= dt
        return self.duration > 0

    def draw(self, surface):
        alpha = max(0, min(255, int((self.duration / self.initial_duration) * 255)))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class DamageNumber:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.duration = 1.0
        self.initial_duration = 1.0
        self.vel_y = -60
        self.font = pygame.font.SysFont("Impact", 28)

    def update(self, dt):
        self.y += self.vel_y * dt
        self.duration -= dt
        return self.duration > 0

    def draw(self, surface):
        alpha = max(0, min(255, int((self.duration / self.initial_duration) * 255)))
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        # Shadow
        shadow = self.font.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(alpha)
        surface.blit(shadow, (self.x - surf.get_width()//2 + 2, self.y + 2))
        surface.blit(surf, (self.x - surf.get_width()//2, self.y))

class ParticleManager:
    def __init__(self):
        self.particles = []
        self.damage_numbers = []
        self.boss_title_timer = 0.0
        self.boss_title_text = ""
        self.title_font = pygame.font.SysFont("Impact", 84)

    def create_damage_number(self, x, y, amount, is_crit=False):
        color = (255, 255, 255)
        text = str(amount)
        if is_crit:
            color = (255, 255, 0)
            text = f"{amount} CRIT!"
        self.damage_numbers.append(DamageNumber(x, y, text, color))

    def trigger_boss_title(self, name):
        self.boss_title_text = name
        self.boss_title_timer = 4.0

    def create_explosion(self, x, y, color=(255, 100, 0), count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            duration = random.uniform(0.5, 1.2)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, vel_x, vel_y, color, duration, size))

    def create_trail(self, x, y, angle, color=(255, 150, 50)):
        spread = 0.4
        p_angle = angle + math.pi + random.uniform(-spread, spread)
        speed = random.uniform(20, 80)
        vel_x = math.cos(p_angle) * speed
        vel_y = math.sin(p_angle) * speed
        duration = random.uniform(0.3, 0.6)
        size = random.randint(2, 4)
        self.particles.append(Particle(x, y, vel_x, vel_y, color, duration, size))

    def create_muzzle_flash(self, x, y, angle, color=(255, 255, 100)):
        for _ in range(5):
            spread = 0.2
            p_angle = angle + random.uniform(-spread, spread)
            speed = random.uniform(100, 300)
            vel_x = math.cos(p_angle) * speed
            vel_y = math.sin(p_angle) * speed
            duration = random.uniform(0.05, 0.15)
            size = random.randint(1, 3)
            self.particles.append(Particle(x, y, vel_x, vel_y, color, duration, size))

    def create_dash_particles(self, x, y, angle, color=(255, 255, 255)):
        for _ in range(15):
            spread = 0.8
            p_angle = angle + math.pi + random.uniform(-spread, spread)
            speed = random.uniform(200, 600)
            vel_x = math.cos(p_angle) * speed
            vel_y = math.sin(p_angle) * speed
            duration = random.uniform(0.1, 0.3)
            size = random.randint(1, 3)
            self.particles.append(Particle(x, y, vel_x, vel_y, color, duration, size))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.damage_numbers = [d for d in self.damage_numbers if d.update(dt)]
        if self.boss_title_timer > 0:
            self.boss_title_timer -= dt

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for d in self.damage_numbers:
            d.draw(surface)
            
        # Draw Boss Title Card
        if self.boss_title_timer > 0:
            alpha = min(255, int(self.boss_title_timer * 255)) if self.boss_title_timer < 1.0 else 255
            if self.boss_title_timer > 3.0:
                alpha = int((4.0 - self.boss_title_timer) * 255)
            
            # Text 1: WARNING
            warn_font = pygame.font.SysFont("Impact", 36)
            warn_surf = warn_font.render("--- WARNING ---", True, (255, 0, 0))
            warn_surf.set_alpha(alpha)
            surface.blit(warn_surf, (surface.get_width()//2 - warn_surf.get_width()//2, surface.get_height()//2 - 100))
            
            # Text 2: BOSS NAME
            title_surf = self.title_font.render(self.boss_title_text, True, (255, 255, 255))
            title_surf.set_alpha(alpha)
            surface.blit(title_surf, (surface.get_width()//2 - title_surf.get_width()//2, surface.get_height()//2 - 50))
            
            # Decoration lines
            line_y = surface.get_height() // 2 + 50
            line_w = int(600 * (min(1.0, 4.0 - self.boss_title_timer) if self.boss_title_timer > 3.0 else 1.0))
            pygame.draw.rect(surface, (255, 0, 0), (surface.get_width()//2 - line_w//2, line_y, line_w, 4))
