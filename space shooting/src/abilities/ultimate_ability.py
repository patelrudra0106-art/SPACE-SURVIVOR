from src.abilities.ability_base import Ability

class UltimateAbility(Ability):
    def __init__(self, game):
        super().__init__(game)
        self.duration = 2.0
        
    def is_ready(self):
        return self.game.player.super_meter >= self.game.player.max_super and not self.is_active

    def activate(self):
        if not self.is_ready():
            return
            
        player = self.game.player
        player.super_meter = 0
        self.is_active = True
        self.duration_timer = self.duration
        player.is_ulting = True
        self.game.audio_manager.play_destroy_sound()
        self.game.screen_shake.trigger(20, self.duration)

    def deactivate(self):
        super().deactivate()
        self.game.player.is_ulting = False
