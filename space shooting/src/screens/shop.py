from src.screens.base_overlay import (
    BaseOverlay,
    PixelButton,
    GREEN_BRITE,
    GREEN_DARK,
    RED_BRITE,
    RED_DARK,
    CYAN_GLOW,
    YELLOW,
    SCORE_COL,
)
from src.lib.game_state import GameState

class Shop(BaseOverlay):

    def __init__(self, game):
        super().__init__(game, panel_h=420)

        cx = self._W // 2
        
        self.btn_hp = PixelButton(cx, self._panel.y + 120, 260, 40, "UPGRADE HP (100 C)", GREEN_BRITE, GREEN_DARK)
        self.btn_hp._callback = self.buy_hp
        
        self.btn_fire_rate = PixelButton(cx, self._panel.y + 170, 260, 40, "UPGRADE FIRE RATE (150 C)", GREEN_BRITE, GREEN_DARK)
        self.btn_fire_rate._callback = self.buy_fire_rate

        self.btn_bomb = PixelButton(cx, self._panel.y + 240, 260, 40, "UNLOCK BOMB (300 C)", CYAN_GLOW, (0, 100, 150))
        self.btn_bomb._callback = self.buy_bomb

        self.btn_ult = PixelButton(cx, self._panel.y + 290, 260, 40, "UNLOCK ULTIMATE (500 C)", CYAN_GLOW, (0, 100, 150))
        self.btn_ult._callback = self.buy_ult

        self.btn_back = PixelButton(cx, self._panel.bottom - 40, 220, 40, "BACK", RED_BRITE, RED_DARK)
        self.btn_back._callback = self.go_back

        self._buttons = [self.btn_hp, self.btn_fire_rate, self.btn_bomb, self.btn_ult, self.btn_back]

    def draw(self, events):
        if self.game.state.name != "SHOP":
            return

        self._draw_particles()
        self._draw_panel()

        px = self._panel.x + 20
        py = self._panel.y

        self.draw_label("-- UPGRADES --", py + 22, color=CYAN_GLOW)
        
        credits = self.game.meta.data["credits"]
        hp_lvl = self.game.meta.data["hp_level"]
        fr_lvl = self.game.meta.data["fire_rate_level"]
        
        self.draw_info_line(f"CREDITS: {credits}", self._W // 2 - 40, py + 60, YELLOW)
        
        # Update button labels dynamically
        hp_cost = hp_lvl * 100
        fr_cost = fr_lvl * 150
        
        self.btn_hp.label = f"UPGRADE HP LVL {hp_lvl} ({hp_cost} C)"
        self.btn_fire_rate.label = f"FIRE RATE LVL {fr_lvl} ({fr_cost} C)"
        
        unlocked = self.game.meta.data["unlocked_abilities"]
        self.btn_bomb.label = "BOMB UNLOCKED" if "bomb" in unlocked else "UNLOCK BOMB (300 C)"
        self.btn_ult.label = "ULTIMATE UNLOCKED" if "ultimate" in unlocked else "UNLOCK ULTIMATE (500 C)"

        self._handle_buttons(events)
        self.draw_title("SPACE SURVIVOR")
        self._draw_hint("ESC to return")

    def buy_hp(self):
        cost = self.game.meta.data["hp_level"] * 100
        self.game.meta.upgrade_hp(cost)

    def buy_fire_rate(self):
        cost = self.game.meta.data["fire_rate_level"] * 150
        self.game.meta.upgrade_fire_rate(cost)

    def buy_bomb(self):
        self.game.meta.unlock_ability("bomb", 300)

    def buy_ult(self):
        self.game.meta.unlock_ability("ultimate", 500)

    def go_back(self):
        self.game.state = GameState.MENU
