"""
screens/pause.py  –  Pause overlay for SPACE SURVIVOR
"""

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


class Pause(BaseOverlay):

    def __init__(self, game):
        super().__init__(game, panel_h=320)

        cx = self._W // 2

        resume_btn = PixelButton(
            cx, self._panel.bottom - 100, 220, 52, "RESUME", GREEN_BRITE, GREEN_DARK
        )
        resume_btn._callback = self.game.pause_game

        menu_btn = PixelButton(
            cx, self._panel.bottom - 40, 220, 52, "MAIN MENU", RED_BRITE, RED_DARK
        )
        menu_btn._callback = self.game.show_game_menu

        self._buttons = [resume_btn, menu_btn]

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, events):
        if self.game.state.name != "PAUSED":
            return

        self._draw_particles()
        self._draw_panel()

        px = self._panel.x + 20
        py = self._panel.y

        # Heading
        self.draw_label("-- PAUSED --", py + 22, color=CYAN_GLOW)

        # Game stats
        self.draw_info_line(f"Kills:  {self.game.game_score}", px + 4, py + 58, SCORE_COL)
        self.draw_info_line(f"Difficulty:  {self.game.game_difficulty} / 10", px + 4, py + 78, YELLOW)

        # Active power-ups
        texts = self.game.power_up_manager.power_up_texts
        if texts:
            self.draw_info_line("── ACTIVE POWER-UPS ──", px, py + 108, CYAN_GLOW)
            for i, (key, data) in enumerate(texts.items()):
                info = data.get("info", data)
                label = info.get("label", "Power Up")
                color = info.get("color", (255, 255, 255))
                # Show timer if timed
                for eff in self.game.power_up_manager.active_effects:
                    if type(eff["power_up"]).__name__ == key:
                        label += f"  ({int(eff['timer']) + 1}s)"
                        break
                self.draw_info_line(label, px + 4, py + 128 + i * 18, color)

        self._handle_buttons(events)
        self.draw_title("SPACE SURVIVOR")
        self._draw_hint("click Resume or press ESC")


