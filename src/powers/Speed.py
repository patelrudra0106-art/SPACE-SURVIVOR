from src.powers.power_up_base import PowerUpBase
from src.config.config import PLAYER_SPEED


class SpeedBoost(PowerUpBase):
    sprite_sheet_name = "engine.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.speed_bonus = 100
        self.is_permanent = False

    def collected(self, player):
        self.player = player
        player.player_speed += self.speed_bonus

    def expire(self, player):
        """Called when the effect wears off."""
        player.player_speed = max(player.player_speed - self.speed_bonus, PLAYER_SPEED)

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        return {"label": "🚀 SPEED BOOST", "color": (100, 200, 255)}
