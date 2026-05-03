import math
import pygame
from src.abilities.ability_base import Ability

class DashAbility(Ability):
    def __init__(self, game):
        super().__init__(game)
        self.cooldown_max = 1.0
        self.duration = 0.15

    def activate(self):
        if not self.is_ready():
            return
            
        player = self.game.player
        self.is_active = True
        self.duration_timer = self.duration
        self.cooldown_timer = self.cooldown_max
        player.is_dashing = True
        
        # Instantly move forward
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - player.cy, mx - player.cx)
        player.cx += math.cos(angle) * 150
        player.cy += math.sin(angle) * 150
        
        self.game.screen_shake.trigger(10, 0.2)
        self.game.audio_manager.play_power_up_sound()
        # Use advanced dash particles
        self.game.particle_manager.create_dash_particles(player.cx, player.cy, angle)

    def deactivate(self):
        super().deactivate()
        self.game.player.is_dashing = False
