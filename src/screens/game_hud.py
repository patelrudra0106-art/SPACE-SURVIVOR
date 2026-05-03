"""
screens/game_hud.py  –  In-game HUD overlay for SPACE SURVIVOR

Renders:
  - Difficulty level (top center)
  - Kill count / score (below health bar)
  - Boss warning alert (timed popup)
  - Active power-ups list (top right)
"""

import pygame
import math

from src.lib.game_utility import get_path
from src.config.config import BOSS_SPAWN_SCORE


# ── Palette ──────────────────────────────────────────────────────────────────
CYAN_GLOW   = (100, 200, 255)
YELLOW      = (240, 210, 60)
RED_BRITE   = (255, 80, 80)
WHITE       = (255, 255, 255)
SPACE_DARK  = (5, 5, 30)
GREEN_BRITE = (80, 220, 60)
ORANGE      = (255, 165, 0)

# Font path
FONT_PATH = get_path("Segoe_UI_Emoji.TTF", "fonts")


class GameHUD:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        # Fonts
        self._font_diff    = pygame.font.Font(FONT_PATH, 20)
        self._font_score   = pygame.font.Font(FONT_PATH, 18)
        self._font_boss    = pygame.font.Font(FONT_PATH, 28)
        self._font_powerup = pygame.font.Font(FONT_PATH, 16)

        # Boss warning state
        self._boss_warn_timer = 0.0
        self._boss_warn_duration = 3.0  # seconds to show warning
        self._last_boss_score = -1      # track which score triggered the warning

        # Level up announcement state
        self._level_up_timer = 0.0
        self._level_up_duration = 3.0

    def update(self, dt):
        """Tick down warning timers."""
        if self._boss_warn_timer > 0:
            self._boss_warn_timer -= dt

        if self._level_up_timer > 0:
            self._level_up_timer -= dt

        if self._level_up_timer > 0:
            self._level_up_timer -= dt

    def draw(self, surface=None):
        """Draw all HUD elements."""
        if surface is None:
            surface = self.screen

        self._draw_difficulty(surface)
        self._draw_score(surface)
        self._draw_boss_warning(surface)
        self._draw_active_powerups(surface)
        self._draw_level_up(surface)
        self._draw_super_meter(surface)
        self._draw_dash_indicator(surface)
        self._draw_xp_bar(surface)
        
        # New "10/10" features
        self._draw_boss_health_bar(surface)
        self._draw_radar(surface)

    def _draw_boss_health_bar(self, surface):
        """Draw a dramatic large health bar at the top if a boss is active."""
        if not self.game.enemy_spawner.boss_alive:
            return
            
        # Find the boss entity
        from src.entities.BossEnemy import BossEnemy
        boss = next((e for e in self.game.enemies if isinstance(e, BossEnemy)), None)
        if not boss:
            return

        width = 400
        height = 20
        x = self.game.game_width // 2 - width // 2
        y = 50
        
        # Glow effect
        glow_rect = pygame.Rect(x-4, y-4, width+8, height+8)
        pygame.draw.rect(surface, (150, 0, 0, 100), glow_rect, 0, 8)
        
        # Background
        pygame.draw.rect(surface, (30, 0, 0), (x, y, width, height), border_radius=5)
        
        # Fill
        pct = max(0, boss.health / boss.max_health)
        fill_w = int(width * pct)
        if fill_w > 0:
            # Gradient-ish red
            pygame.draw.rect(surface, (200, 30, 30), (x, y, fill_w, height), border_radius=5)
            # Highlight
            pygame.draw.rect(surface, (255, 100, 100), (x, y, fill_w, height // 3), border_radius=5)

        # Label
        label = self._font_score.render("BOSS UNIT DETECTED", True, WHITE)
        surface.blit(label, (x + width // 2 - label.get_width() // 2, y + height + 5))

    def _draw_radar(self, surface):
        """Draw a mini-radar in the bottom right corner."""
        radius = 70
        margin = 20
        cx = self.game.game_width - radius - margin
        cy = self.game.game_height - radius - margin
        
        # Radar Base
        pygame.draw.circle(surface, (0, 30, 20, 180), (cx, cy), radius) # Transparent dark green
        pygame.draw.circle(surface, (0, 255, 100, 100), (cx, cy), radius, 2) # Outer ring
        pygame.draw.circle(surface, (0, 255, 100, 50), (cx, cy), radius // 2, 1) # Inner ring
        
        # Crosshairs
        pygame.draw.line(surface, (0, 255, 100, 50), (cx - radius, cy), (cx + radius, cy))
        pygame.draw.line(surface, (0, 255, 100, 50), (cx, cy - radius), (cx, cy + radius))
        
        # Scanning sweep (aesthetic)
        sweep_angle = (pygame.time.get_ticks() / 5.0) % 360
        sweep_x = cx + math.cos(math.radians(sweep_angle)) * radius
        sweep_y = cy + math.sin(math.radians(sweep_angle)) * radius
        pygame.draw.line(surface, (0, 255, 100, 80), (cx, cy), (sweep_x, sweep_y), 2)

        # Draw entities on radar
        # Scale: Game world to radar
        view_dist = 800 # How far the radar "sees"
        
        player = self.game.player
        
        # 1. Enemies (Red)
        for enemy in self.game.enemies:
            dx = enemy.cx - player.cx
            dy = enemy.cy - player.cy
            dist = math.hypot(dx, dy)
            if dist < view_dist:
                rx = cx + (dx / view_dist) * radius
                ry = cy + (dy / view_dist) * radius
                pygame.draw.circle(surface, RED_BRITE, (int(rx), int(ry)), 2)
        
        # 2. Powerups (Yellow)
        for pu in self.game.power_up_manager.power_ups:
            dx = pu.x - player.cx
            dy = pu.y - player.cy
            dist = math.hypot(dx, dy)
            if dist < view_dist:
                rx = cx + (dx / view_dist) * radius
                ry = cy + (dy / view_dist) * radius
                pygame.draw.circle(surface, YELLOW, (int(rx), int(ry)), 2)
                
        # 3. Player (Center green dot)
        pygame.draw.circle(surface, GREEN_BRITE, (cx, cy), 3)

    # ── Difficulty (top center) ──────────────────────────────────────────────

    def _draw_difficulty(self, surface):
        diff = self.game.game_difficulty
        level = self.game.game_level
        
        if self.game.game_mode == "level":
            text = f"LEVEL {level} / 100  |  DIFF {diff}"
        else:
            text = f"ENDLESS MODE  |  DIFF {diff}"

        # Color shifts from cyan → yellow → red as difficulty increases
        if diff <= 3:
            color = CYAN_GLOW
        elif diff <= 6:
            color = YELLOW
        elif diff <= 8:
            color = ORANGE
        else:
            color = RED_BRITE

        rendered = self._font_diff.render(text, True, color)
        shadow   = self._font_diff.render(text, True, SPACE_DARK)
        x = self.game.game_width // 2 - rendered.get_width() // 2
        y = 12
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(rendered, (x, y))

    # ── Score / Kills (top left, below health bar) ───────────────────────────

    def _draw_score(self, surface):
        if self.game.game_mode == "level":
            kills_needed = self.game.game_level * 10
            text = f"KILLS: {self.game.game_score} / {kills_needed}"
        else:
            text = f"SCORE: {self.game.game_score}"
        rendered = self._font_score.render(text, True, WHITE)
        shadow   = self._font_score.render(text, True, SPACE_DARK)
        x = 12
        y = 38
        surface.blit(shadow, (x + 1, y + 1))
        surface.blit(rendered, (x, y))

    # ── Boss Warning (center screen, timed) ──────────────────────────────────

    def _draw_boss_warning(self, surface):
        if self._boss_warn_timer <= 0:
            return

        t = pygame.time.get_ticks() / 200.0
        # Pulsing alpha effect
        alpha = int((math.sin(t) + 1) / 2 * 155 + 100)

        text = "⚠  BOSS INCOMING  ⚠"
        rendered = self._font_boss.render(text, True, RED_BRITE)
        shadow   = self._font_boss.render(text, True, SPACE_DARK)

        # Create surface with alpha
        surf = pygame.Surface(rendered.get_size(), pygame.SRCALPHA)
        surf.blit(shadow, (2, 2))
        surf.blit(rendered, (0, 0))
        surf.set_alpha(alpha)

        x = self.game.game_width // 2 - rendered.get_width() // 2
        y = self.game.game_height // 2 - 120
        surface.blit(surf, (x, y))

    # ── Active Power-ups (top right) ─────────────────────────────────────────

    def _draw_active_powerups(self, surface):
        texts = self.game.power_up_manager.power_up_texts

        if not texts:
            return

        # Build a timer lookup from active_effects
        timers = {}
        for effect in self.game.power_up_manager.active_effects:
            name = type(effect["power_up"]).__name__
            timers[name] = int(effect["timer"]) + 1  # ceiling

        # Header
        header = self._font_powerup.render("POWER-UPS", True, YELLOW)
        header_shadow = self._font_powerup.render("POWER-UPS", True, SPACE_DARK)
        x = self.game.game_width - header.get_width() - 16
        y = 12
        surface.blit(header_shadow, (x + 1, y + 1))
        surface.blit(header, (x, y))

        # List each active power-up from the manager
        for i, (key, data) in enumerate(texts.items()):
            # Fallback for old save states if needed
            if "info" in data:
                info = data["info"]
                image = data.get("image")
            else:
                info = data
                image = None
                
            timer_text = ""
            if key in timers:
                timer_text = f"{timers[key]}s"
                
            py = y + 24 + i * 36
            
            if image:
                img_w, img_h = 28, 28
                small_img = pygame.transform.scale(image, (img_w, img_h))
                px = self.game.game_width - img_w - 16
                surface.blit(small_img, (px, py))
                
                if timer_text:
                    rendered = self._font_powerup.render(timer_text, True, info["color"])
                    shadow   = self._font_powerup.render(timer_text, True, SPACE_DARK)
                    tx = px - rendered.get_width() - 8
                    ty = py + (img_h - rendered.get_height()) // 2
                    surface.blit(shadow, (tx + 1, ty + 1))
                    surface.blit(rendered, (tx, ty))
            else:
                label = info["label"]
                if timer_text:
                    label += f"  {timer_text}"
                rendered = self._font_powerup.render(label, True, info["color"])
                shadow   = self._font_powerup.render(label, True, SPACE_DARK)
                px = self.game.game_width - rendered.get_width() - 16
                surface.blit(shadow, (px + 1, py + 1))
                surface.blit(rendered, (px, py))

    def _draw_super_meter(self, surface):
        """Draw the ultimate ability meter at the bottom center."""
        player = self.game.player
        
        if "ultimate" not in player.abilities:
            return
            
        width = 200
        height = 12
        x = self.game.game_width // 2 - width // 2
        y = self.game.game_height - 30
        
        # Border
        pygame.draw.rect(surface, SPACE_DARK, (x-2, y-2, width+4, height+4), 0, 4)
        pygame.draw.rect(surface, WHITE, (x-2, y-2, width+4, height+4), 1, 4)
        
        # Fill
        fill_width = int((player.super_meter / player.max_super) * width)
        color = ORANGE if player.super_meter < player.max_super else GREEN_BRITE
        if fill_width > 0:
            pygame.draw.rect(surface, color, (x, y, fill_width, height), 0, 2)
            
        # Text
        text = "ULTIMATE [F]" if player.super_meter >= player.max_super else "SUPER METER"
        rendered = self._font_powerup.render(text, True, WHITE)
        surface.blit(rendered, (x + width // 2 - rendered.get_width() // 2, y - 20))

    def _draw_dash_indicator(self, surface):
        """Draw dash availability near the health bar."""
        player = self.game.player
        x = 12
        y = 60
        
        dash_ability = player.abilities.get("dash")
        if not dash_ability:
            return
            
        dash_cooldown = dash_ability.cooldown_timer
        
        text = "DASH [SHIFT]"
        color = CYAN_GLOW if dash_cooldown <= 0 else (100, 100, 100)
        rendered = self._font_powerup.render(text, True, color)
        surface.blit(rendered, (x, y))
        
        # Cooldown bar
        if dash_cooldown > 0:
            cd_width = 80
            pygame.draw.rect(surface, SPACE_DARK, (x, y + 20, cd_width, 4))
            fill = int((dash_cooldown / dash_ability.cooldown_max) * cd_width)
            pygame.draw.rect(surface, CYAN_GLOW, (x, y + 20, fill, 4))

    def _draw_level_up(self, surface):
        if self._level_up_timer <= 0:
            return

        t = pygame.time.get_ticks() / 150.0
        # Pulsing effect
        alpha = int((math.sin(t) + 1) / 2 * 155 + 100)
        scale = 1.0 + math.sin(t) * 0.1

        text = f"LEVEL UP: {self.game.game_level}!"
        rendered = self._font_boss.render(text, True, GREEN_BRITE)
        shadow   = self._font_boss.render(text, True, SPACE_DARK)

        # Scale for animation
        w, h = rendered.get_size()
        scaled_w, scaled_h = int(w * scale), int(h * scale)
        rendered = pygame.transform.scale(rendered, (scaled_w, scaled_h))
        shadow = pygame.transform.scale(shadow, (scaled_w, scaled_h))

        surf = pygame.Surface(rendered.get_size(), pygame.SRCALPHA)
        surf.blit(shadow, (2, 2))
        surf.blit(rendered, (0, 0))
        surf.set_alpha(alpha)

        x = self.game.game_width // 2 - scaled_w // 2
        y = self.game.game_height // 2 - 180
        surface.blit(surf, (x, y))

    def trigger_level_up(self):
        """Trigger the level-up announcement."""
        self._level_up_timer = self._level_up_duration

    def trigger_boss_warning(self):
        """Trigger the boss incoming alert."""
        self._boss_warn_timer = self._boss_warn_duration

    def reset(self):
        """Reset HUD state for a new game."""
        self._boss_warn_timer = 0.0
        self._last_boss_score = -1
        self._level_up_timer = 0.0

    def _draw_xp_bar(self, surface):
        """Draw the Roguelike XP Bar at the top edge of the screen."""
        player = self.game.player
        if not player: return
        
        w = self.game.game_width - 40
        h = 8
        x = 20
        y = 5
        
        pct = min(1.0, player.xp / max(1, player.xp_to_next_level))
        
        # Background
        pygame.draw.rect(surface, (30, 30, 40), (x, y, w, h), border_radius=3)
        
        # Fill (cyan)
        if pct > 0:
            fill_rect = pygame.Rect(x, y, int(w * pct), h)
            pygame.draw.rect(surface, (50, 200, 255), fill_rect, border_radius=3)
        
        # Outline
        pygame.draw.rect(surface, SPACE_DARK, (x, y, w, h), 1, border_radius=3)
