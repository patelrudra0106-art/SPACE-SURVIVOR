"""
screens/restart.py  –  Game-over / restart overlay for SPACE SURVIVOR
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


class Restart(BaseOverlay):

    def __init__(self, game):
        super().__init__(game, panel_h=380)

        cx = self._W // 2

        restart_btn = PixelButton(
            cx, self._panel.bottom - 100, 220, 52, "RESTART", GREEN_BRITE, GREEN_DARK
        )
        restart_btn._callback = self.game.game_restart

        quit_btn = PixelButton(
            cx, self._panel.bottom - 40, 220, 52, "MAIN MENU", RED_BRITE, RED_DARK
        )
        quit_btn._callback = self.game.show_game_menu

        self._buttons = [restart_btn, quit_btn]
        self._last_score = 0
        self._last_difficulty = 1

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, events):
        if self.game.state.name != "GAME_OVER":
            return

        self._draw_particles()
        self._draw_panel()

        px = self._panel.x + 20
        py = self._panel.y

        # Heading
        self.draw_label("-- GAME OVER --", py + 22, color=RED_BRITE)

        # Stats
        self.draw_info_line(f"Enemies Killed:   {self.game.game_score}", px + 4, py + 62, SCORE_COL)
        self.draw_info_line(f"Difficulty Reached:   {self.game.game_difficulty:.1f} / 10", px + 4, py + 82, YELLOW)
        self.draw_info_line(f"Best Score:   {self.game.game_high_score}", px + 4, py + 102, CYAN_GLOW)

        # Tips
        self.draw_info_line("── TIPS ──", px, py + 135, CYAN_GLOW)
        self.draw_info_line("• Each kill restores +1 health", px + 4, py + 155, (80, 220, 60))
        self.draw_info_line("• Collect power-ups after 10 kills", px + 4, py + 173, SCORE_COL)
        self.draw_info_line("• Boss spawns every 25 kills", px + 4, py + 191, SCORE_COL)
        self.draw_info_line("• Difficulty increases every 25 kills", px + 4, py + 209, SCORE_COL)
        self.draw_info_line("• Health boost on difficulty up", px + 4, py + 227, (80, 220, 60))

        self._handle_buttons(events)
        self.draw_title("SPACE SURVIVOR")
        self._draw_hint("Restart or Main Menu")


