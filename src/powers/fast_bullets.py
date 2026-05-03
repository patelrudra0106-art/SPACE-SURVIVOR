from src.powers.power_up_base import PowerUpBase


class FastBullets(PowerUpBase):
    sprite_sheet_name = "fast_bullets.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.is_permanent = False
        self.bullet_speed_bonus = 300

    def collected(self, player):
        self.player = player
        player.bullet_speed += self.bullet_speed_bonus

    def expire(self, player):
        player.bullet_speed -= self.bullet_speed_bonus

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "⚡ FAST BULLETS", "color": (255, 255, 100)}
