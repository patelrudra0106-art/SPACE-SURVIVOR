from src.powers.power_up_base import PowerUpBase

class BoltPowerUp(PowerUpBase):
    sprite_sheet_name = "bolt.png"

    def __init__(self, x, y):
        # Slightly larger since it's the only power now
        super().__init__(x, y, width=60, height=60)
        self.is_permanent = False
        self.duration = 15.0
        self.speed_bonus = 200
        self.damage_bonus = 20

    def collected(self, player):
        self.player = player
        player.player_speed += self.speed_bonus
        player.bullet_damage += self.damage_bonus
        # Instantly heal a bit too
        player.health = min(player.max_health, player.health + 30)

    def expire(self, player):
        player.player_speed -= self.speed_bonus
        player.bullet_damage -= self.damage_bonus

    def display_info(self) -> dict:
        return {"label": "⚡ HYPER BOLT", "color": (255, 255, 0)}
