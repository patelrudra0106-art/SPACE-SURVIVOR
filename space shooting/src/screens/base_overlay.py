"""
screens/base_overlay.py  –  Shared pixel-art overlay base class.

Menu, Pause, and Restart all inherit from this to reuse:
  - panel drawing
  - floating mist particles
  - pixel buttons
  - title / label rendering
"""

import pygame
import math
import random
import os

from src.lib.game_utility import get_path

# ── Font path helper ──────────────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = get_path("Segoe_UI_Emoji.TTF", "fonts")

# ── Palette (space-themed) ────────────────────────────────────────────────────
SPACE_DARK = (5, 5, 30)
SPACE_MID = (20, 30, 80)
SPACE_LIGHT = (60, 100, 180)
CYAN_GLOW = (100, 200, 255)
GREEN_BRITE = (80, 200, 60)
GREEN_DARK = (30, 90, 30)
RED_BRITE = (180, 50, 50)
RED_DARK = (90, 20, 20)
YELLOW = (240, 210, 60)
YELLOW_DARK = (120, 100, 20)
SCORE_COL = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ── Reusable pixel button ─────────────────────────────────────────────────────


class PixelButton:
    def __init__(self, cx, cy, w, h, label, face, shadow):
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.label = label
        self.face = face
        self.shadow = shadow
        self.hovered = False
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.Font(FONT_PATH, 22)
        return self._font

    def update(self, mx, my):
        self.hovered = self.rect.collidepoint(mx, my)

    def draw(self, surf):
        depth = 3 if self.hovered else 5
        col = SPACE_LIGHT if self.hovered else self.face
        hi_col = tuple(min(c + 55, 255) for c in col)

        shd = self.rect.move(depth, depth)
        pygame.draw.rect(surf, self.shadow, shd, border_radius=5)
        pygame.draw.rect(surf, col, self.rect, border_radius=5)

        hi = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.w - 8, 5)
        pygame.draw.rect(surf, hi_col, hi, border_radius=3)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=5)
        pygame.draw.rect(surf, SPACE_MID, self.rect.inflate(-4, -4), 1, border_radius=4)

        font = self._get_font()
        ts = font.render(self.label, True, BLACK)
        tx = self.rect.centerx - ts.get_width() // 2
        ty = self.rect.centery - ts.get_height() // 2
        surf.blit(ts, (tx + 2, ty + 2))
        surf.blit(font.render(self.label, True, WHITE), (tx, ty))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ── Base overlay ──────────────────────────────────────────────────────────────


class BaseOverlay:
    """
    Inherit from this class and call super().__init__(game, panel_h).
    Provides: panel, particles, draw_label(), draw_hint(), draw_title().
    """

    def __init__(self, game, panel_h=260):
        self.game = game
        self.screen = game.screen
        self.enabled = False
        self._W = game.game_width
        self._H = game.game_height

        panel_w = 340
        self._panel = pygame.Rect(
            self._W // 2 - panel_w // 2, self._H // 2 - panel_h // 2, panel_w, panel_h
        )

        self._particles = [
            {
                "x": random.uniform(0, self._W),
                "y": random.uniform(0, self._H),
                "speed": random.uniform(0.2, 0.7),
                "phase": random.uniform(0, math.pi * 2),
                "r": random.randint(1, 3),
            }
            for _ in range(30)
        ]
        self._font_title = pygame.font.Font(FONT_PATH, 48)
        self._font_label = pygame.font.Font(FONT_PATH, 20)
        self._font_score = pygame.font.Font(FONT_PATH, 18)
        self._font_hint = pygame.font.Font(FONT_PATH, 13)
        self._font_ui = pygame.font.Font(FONT_PATH, 36)
        self._font_info = pygame.font.Font(FONT_PATH, 14)
        self._buttons = []  # subclasses append PixelButton instances here

    # ── Shared draw helpers ───────────────────────────────────────────────────

    def _draw_particles(self):
        t = pygame.time.get_ticks() / 1000.0
        for p in self._particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(t * p["speed"] + p["phase"]) * 0.4
            if p["y"] < 0:
                p["y"] = self._H
                p["x"] = random.uniform(0, self._W)

            blink = (math.sin(t * 1.5 + p["phase"]) + 1) / 2
            alpha = int(blink * 160 + 40)
            s = pygame.Surface((p["r"] * 4, p["r"] * 4), pygame.SRCALPHA)
            pygame.draw.circle(
                s, (*CYAN_GLOW, alpha), (p["r"] * 2, p["r"] * 2), p["r"] * 2
            )
            self.screen.blit(s, (int(p["x"]) - p["r"] * 2, int(p["y"]) - p["r"] * 2))

    def _draw_panel(self):
        overlay = pygame.Surface((self._panel.w, self._panel.h), pygame.SRCALPHA)
        overlay.fill((*SPACE_DARK, 210))
        self.screen.blit(overlay, self._panel.topleft)

        pygame.draw.rect(self.screen, SPACE_MID, self._panel, 3, border_radius=8)
        pygame.draw.rect(
            self.screen, CYAN_GLOW, self._panel.inflate(-6, -6), 1, border_radius=6
        )

        for cx2, cy2 in [
            self._panel.topleft,
            self._panel.topright,
            self._panel.bottomleft,
            self._panel.bottomright,
        ]:
            pygame.draw.rect(self.screen, CYAN_GLOW, (cx2 - 4, cy2 - 4, 8, 8))

    def draw_title(self, text, y_frac=0.13, y_abs=None):
        """Animated wave + 3-D extruded title. y_frac = fraction of screen height."""
        t = pygame.time.get_ticks() / 500.0
        font = self._font_title
        fsize = 48
        x_start = self._W // 2 - (len(text) * fsize * 0.29)

        for i, ch in enumerate(text):
            wy = int(math.sin(t * 2.2 + i * 0.45) * 5)
            x = int(x_start + i * fsize * 0.58)
            y = y_abs + wy if y_abs is not None else int(self._H * y_frac + wy)

            for d in range(5, 0, -1):
                self.screen.blit(font.render(ch, True, SPACE_DARK), (x + d, y + d))
            for ox2, oy2 in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                self.screen.blit(font.render(ch, True, CYAN_GLOW), (x + ox2, y + oy2))
            self.screen.blit(font.render(ch, True, WHITE), (x, y))

            gleam = font.render(ch, True, CYAN_GLOW)
            clip_h = int(gleam.get_height() * 0.35)
            clip = pygame.Surface((gleam.get_width(), clip_h), pygame.SRCALPHA)
            clip.blit(gleam, (0, 0))
            self.screen.blit(clip, (x, y))

    def draw_label(self, text, y, color=SCORE_COL):
        """Centered text label with drop shadow."""
        rendered = self._font_label.render(text, True, color)
        shad = self._font_label.render(text, True, SPACE_DARK)
        x = self._W // 2 - rendered.get_width() // 2
        self.screen.blit(shad, (x + 2, y + 2))
        self.screen.blit(rendered, (x, y))

    def draw_score_label(self, text, y):
        rendered = self._font_score.render(text, True, SCORE_COL)
        shad = self._font_score.render(text, True, SPACE_DARK)
        x = self._W // 2 - rendered.get_width() // 2
        self.screen.blit(shad, (x + 2, y + 2))
        self.screen.blit(rendered, (x, y))

    def draw_info_line(self, text, x, y, color=SCORE_COL):
        """Left-aligned small info text with shadow."""
        rendered = self._font_info.render(text, True, color)
        shad = self._font_info.render(text, True, SPACE_DARK)
        self.screen.blit(shad, (x + 1, y + 1))
        self.screen.blit(rendered, (x, y))

    def _draw_hint(self, text="click to select  |  ESC to quit"):
        hint = self._font_hint.render(text, True, SPACE_MID)
        self.screen.blit(hint, (self._W // 2 - hint.get_width() // 2, self._H - 24))

    def _handle_buttons(self, events):
        mx, my = pygame.mouse.get_pos()
        for btn in self._buttons:
            btn.update(mx, my)
            btn.draw(self.screen)
        for event in events:
            for btn in self._buttons:
                if btn.clicked(event):
                    btn._callback()
