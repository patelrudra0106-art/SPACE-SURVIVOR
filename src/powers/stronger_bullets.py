from src.powers.power_up_base import PowerUpBase


class StrongerBullets(PowerUpBase):
    sprite_sheet_name = "stronger_bullets.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.is_permanent = False
        self.damage_bonus = 5

    def collected(self, player):
        self.player = player
        player.bullet_damage += self.damage_bonus

    def expire(self, player):
        player.bullet_damage -= self.damage_bonus

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "💥 STRONGER BULLETS", "color": (255, 50, 50)}
