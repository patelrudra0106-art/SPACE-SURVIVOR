import pygame
from src.entities.Enemy import Enemy
from src.config.config import ENEMY_HEALTH, ENEMY_SPEED

class TankEnemy(Enemy):
    def __init__(self, game):
        # Slower but much more health
        super().__init__(game, width=80, height=80, health=ENEMY_HEALTH * 3)
        self.speed *= 0.5
        self.give_dmg = 20
        self.color = (150, 0, 0) # Darker red

    def load_enemy_image(self):
        # Use the same image but maybe scale it in draw
        img = super().load_enemy_image()
        return img
