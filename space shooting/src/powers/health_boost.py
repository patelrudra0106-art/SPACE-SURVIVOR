from src.powers.power_up_base import PowerUpBase


class HealthBoost(PowerUpBase):
    sprite_sheet_name = "health_sprite_sheet.png"

    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=50)
        self.max_health_increase = 25

    def collected(self, player):
        self.player = player
        # Increase max health permanently
        player.max_health += self.max_health_increase
        # Heal to the new max
        player.health = player.max_health
        player.health_bar.max_health = player.max_health
        player.health_regen = True

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        """Return label and color for HUD display."""
        return {"label": "♥ MAX HP +25", "color": (80, 220, 60)}
