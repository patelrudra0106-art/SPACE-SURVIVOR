from src.abilities.ability_base import Ability
from src.entities.BossEnemy import BossEnemy

class BombAbility(Ability):
    def __init__(self, game):
        super().__init__(game)
        self.cooldown_max = 2.0  # 2 second cooldown to prevent spamming

    def activate(self):
        if not self.is_ready():
            return
            
        if self.game.game_score >= 10:
            self.game.game_score -= 10
            self.cooldown_timer = self.cooldown_max
            
            # Create a massive explosion and shake
            self.game.screen_shake.trigger(30, 0.5)
            self.game.particle_manager.create_explosion(self.game.game_width // 2, self.game.game_height // 2, color=(255, 255, 255), count=100)
            
            # Destroy all small enemies
            for enemy in self.game.enemies[:]:
                if not isinstance(enemy, BossEnemy):
                    self.game.particle_manager.create_explosion(enemy.cx, enemy.cy)
                    self.game.enemies.remove(enemy)
            
            self.game.audio_manager.play_destroy_sound()
