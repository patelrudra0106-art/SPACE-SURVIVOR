"""
screens/menu.py  –  Main menu overlay for SPACE SURVIVOR
"""

import os
import pygame
from src.lib.game_utility import load_game_state

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


class Menu(BaseOverlay):

    def __init__(self, game):
        panel_h = 560
        super().__init__(game, panel_h=panel_h)

        panel_w = 340
        self._panel = pygame.Rect(
            self._W // 2 - panel_w // 2, self._H // 2 - panel_h // 2, panel_w, panel_h
        )
        if self._panel.y < 80:
            self._panel.y = 80
            
        cx = self._W // 2
        
        # Check if save exists
        save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "save_game.json")
        self.has_save = os.path.exists(save_path)

        self.level_btn = PixelButton(cx, 0, 220, 42, "LEVEL MODE", GREEN_BRITE, GREEN_DARK)
        self.level_btn._callback = self.game_level_start

        self.infinite_btn = PixelButton(cx, 0, 220, 42, "ENDLESS  MODE", CYAN_GLOW, (0, 100, 150))
        self.infinite_btn._callback = self.game_infinite_start

        quit_btn = PixelButton(cx, 0, 220, 42, "QUIT", RED_BRITE, RED_DARK)
        quit_btn._callback = self.game_quit

        self._buttons = [self.level_btn, self.infinite_btn]
        
        if self.has_save:
            self.resume_btn = PixelButton(cx, 0, 220, 42, "RESUME", YELLOW, (150, 100, 0))
            self.resume_btn._callback = self.game_resume
            self._buttons.append(self.resume_btn)
            
        self._buttons.append(quit_btn)

        # Dynamically layout buttons from bottom to top for a clean UI
        curr_y = self._panel.bottom - 40
        for btn in reversed(self._buttons):
            btn.rect.centery = curr_y
            curr_y -= 55

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, events):
        if self.game.state.name != "MENU":
            return

        self._draw_particles()
        self._draw_panel()

        px = self._panel.x + 20
        py = self._panel.y

        # Subtitle
        self.draw_label("Survive the bullet hell!", py + 22)

        # ── Power-ups section ────────────────────────────────────────
        self.draw_info_line("--- POWER-UPS (spawn after 10 kills) ---", px, py + 55, CYAN_GLOW)
        self.draw_info_line("[+] Health Regen   - permanent heal over time", px + 4, py + 75, (80, 220, 60))
        self.draw_info_line("[>] Speed Boost    - faster movement (10s)", px + 4, py + 93, (100, 200, 255))
        self.draw_info_line("[!] Fast Bullets   - faster projectiles (10s)", px + 4, py + 111, (255, 200, 50))
        self.draw_info_line("[*] Strong Bullets - more damage (10s)", px + 4, py + 129, (255, 80, 80))

        # ── Controls section ─────────────────────────────────────────
        self.draw_info_line("--- CONTROLS ---", px, py + 160, CYAN_GLOW)
        self.draw_info_line("Mouse Move     - aim & move ship", px + 4, py + 180, SCORE_COL)
        self.draw_info_line("Left Click      - shoot", px + 4, py + 198, SCORE_COL)
        self.draw_info_line("ESC              - pause / quit", px + 4, py + 216, SCORE_COL)

        # ── Game info ────────────────────────────────────────────────
        self.draw_info_line("--- INFO ---", px, py + 247, CYAN_GLOW)
        self.draw_info_line("10 difficulty levels | Boss every 5 levels", px + 4, py + 267, YELLOW)
        self.draw_info_line("Each kill restores +3 health", px + 4, py + 285, (80, 220, 60))

        self._handle_buttons(events)
        self.draw_title("SPACE SURVIVOR", y_abs=self._panel.y - 70)
        self._draw_hint("click PLAY to start  |  ESC to quit")

    # ── callbacks ─────────────────────────────────────────────────────────────

    def game_level_start(self):
        self.game.game_start(resume=False, mode="level")

    def game_infinite_start(self):
        self.game.game_start(resume=False, mode="infinite")

    def game_resume(self):
        self.game.game_start(resume=True)

    def game_quit(self):
        self.game.game_quit()
