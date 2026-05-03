from src.powers.power_up_base import PowerUpBase


class TripleShotPowerUp(PowerUpBase):
    sprite_sheet_name = "stronger_bullets.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.is_permanent = False
        self.duration = 10.0

    def collected(self, player):
        self.player = player
        player.triple_shot_active = True

    def expire(self, player):
        player.triple_shot_active = False

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "🔫 TRIPLE SHOT", "color": (255, 100, 0)}
