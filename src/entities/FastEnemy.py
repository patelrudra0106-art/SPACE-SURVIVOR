import pygame
from src.entities.Enemy import Enemy
from src.config.config import ENEMY_HEALTH, ENEMY_SPEED

class FastEnemy(Enemy):
    def __init__(self, game):
        # Faster but less health and smaller
        super().__init__(game, width=35, height=35, health=ENEMY_HEALTH * 0.5)
        self.speed *= 1.8
        self.give_dmg = 5
        self.color = (255, 100, 100) # Lighter red

    def load_enemy_image(self):
        img = super().load_enemy_image()
        return img
