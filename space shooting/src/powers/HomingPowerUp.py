from src.powers.power_up_base import PowerUpBase


class HomingPowerUp(PowerUpBase):
    sprite_sheet_name = "missile.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.is_permanent = False

    def collected(self, player):
        self.player = player
        player.homing_active = True

    def expire(self, player):
        player.homing_active = False

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "🎯 HOMING SHOTS", "color": (150, 255, 150)}
