from src.powers.power_up_base import PowerUpBase


class ShieldPowerUp(PowerUpBase):
    sprite_sheet_name = "shield.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.is_permanent = True # Permanent until hit

    def collected(self, player):
        self.player = player
        player.has_shield = True

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "🛡️ SHIELD", "color": (100, 255, 255)}
