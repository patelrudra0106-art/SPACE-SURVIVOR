"""
powers/power_up_base.py  –  Animated sprite-sheet base class for all power-ups.

Sprite sheets are 480×32 with 15 frames (each ~32×32).
Subclasses just set `sprite_sheet_name` and override `collected()` / `display_info()`.
"""

import pygame

from src.lib.game_utility import get_path


class PowerUpBase:
    """Base class for all power-ups with animated sprite sheet rendering."""

    # Subclasses set this to their sprite sheet filename (e.g. "health_sprite_sheet.png")
    sprite_sheet_name: str = ""

    # Sprite sheet layout
    SHEET_COLS = 15       # number of frames in the sheet
    FRAME_W    = 32       # width of each frame in the sheet
    FRAME_H    = 32       # height of each frame in the sheet

    def __init__(self, x: int, y: int, width: int = 50, height: int = 50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.player = None
        self.is_permanent = True
        self.active_time = 0

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # ── Animation ────────────────────────────────────────────────────
        self.frames: list[pygame.Surface] = []
        self.current_frame = 0
        self.animation_speed = 0.1  # seconds per frame
        self.animation_timer = 0.0

        if self.sprite_sheet_name:
            self._load_sprite_sheet()

    # ── Sprite sheet loading ─────────────────────────────────────────────

    def _load_sprite_sheet(self):
        """Slice a horizontal sprite sheet into individual frames, or handle single images."""
        sheet = pygame.image.load(
            get_path(self.sprite_sheet_name, "images", "powers")
        ).convert_alpha()

        sheet_w = sheet.get_width()
        sheet_h = sheet.get_height()
        
        # Determine if it's a sprite sheet (typically much wider than tall) or a single icon
        # We assume if the width is close to the height (square), it's a single icon.
        if sheet_w <= sheet_h * 1.5:
            frame = pygame.transform.scale(sheet, (self.width, self.height))
            self.frames.append(frame)
        else:
            # It's likely a horizontal sprite sheet
            frame_w = sheet_w // self.SHEET_COLS
            frame_h = sheet_h

            for i in range(self.SHEET_COLS):
                frame_rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                frame = sheet.subsurface(frame_rect).copy()
                # Scale to the power-up's display size
                frame = pygame.transform.scale(frame, (self.width, self.height))
                self.frames.append(frame)

    # ── Update / Draw ────────────────────────────────────────────────────

    def update(self):
        """Advance the animation frame."""
        if not self.frames:
            return
        self.animation_timer += 1 / 60  # approximate dt at 60fps
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen: pygame.Surface):
        """Draw the current animation frame, drifting downward."""
        self.y += 1
        self.rect.y = self.y

        if self.frames:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))
        else:
            # Fallback: plain colored square
            pygame.draw.rect(screen, (200, 200, 200), self.rect)

    # ── Override in subclasses ───────────────────────────────────────────

    def collected(self, player):
        """Called when the player picks up this power-up. Override in subclass."""
        raise NotImplementedError

    def display_info(self) -> dict[str, str | tuple[int, int, int]]:
        """Return {"label": "...", "color": (...)} for HUD display. Override in subclass."""
        return {"label": "UNKNOWN", "color": (200, 200, 200)}
