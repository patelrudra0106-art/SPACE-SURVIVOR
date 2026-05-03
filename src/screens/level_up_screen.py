"""
screens/level_up_screen.py - Roguelike upgrade selection screen
"""

import pygame
import random
from src.screens.base_overlay import BaseOverlay, PixelButton, SPACE_DARK, CYAN_GLOW, SCORE_COL, YELLOW

class LevelUpScreen(BaseOverlay):
    def __init__(self, game):
        super().__init__(game, panel_h=400)
        self.upgrades_pool = [
            {"id": "hp", "label": "+20 Max HP", "desc": "Increases max health", "color": (80, 220, 60)},
            {"id": "speed", "label": "+10% Speed", "desc": "Move faster", "color": (100, 200, 255)},
            {"id": "fire_rate", "label": "+10% Fire Rate", "desc": "Shoot faster", "color": (255, 200, 50)},
            {"id": "damage", "label": "+15% Damage", "desc": "Stronger bullets", "color": (255, 80, 80)},
            {"id": "triple_shot", "label": "Triple Shot", "desc": "Fires 3 bullets", "color": (255, 100, 0)},
            {"id": "homing", "label": "Homing Missiles", "desc": "Auto-targeting", "color": (255, 127, 0)}
        ]
        self.offered_upgrades = []

    def roll_upgrades(self):
        # Choose 3 random unique upgrades
        available = [u for u in self.upgrades_pool]
        
        # Remove unique upgrades if already active
        if self.game.player.triple_shot_active:
            available = [u for u in available if u["id"] != "triple_shot"]
        if self.game.player.homing_active:
            available = [u for u in available if u["id"] != "homing"]
            
        self.offered_upgrades = random.sample(available, min(3, len(available)))
        
        # Create buttons
        self._buttons = []
        cx = self._W // 2
        
        y_start = self._panel.y + 100
        for i, upg in enumerate(self.offered_upgrades):
            btn = PixelButton(cx, y_start + i * 80, 300, 60, upg["label"], upg["color"], (int(upg["color"][0]*0.5), int(upg["color"][1]*0.5), int(upg["color"][2]*0.5)))
            
            # Use default arguments to capture `upg` in the lambda
            btn._callback = lambda u=upg: self.apply_upgrade(u)
            self._buttons.append(btn)

    def apply_upgrade(self, upgrade):
        uid = upgrade["id"]
        player = self.game.player
        
        if uid == "hp":
            player.max_health += 20
            player.health += 20
        elif uid == "speed":
            player.player_speed *= 1.1
        elif uid == "fire_rate":
            player.shoot_delay *= 0.9
        elif uid == "damage":
            player.bullet_damage = int(player.bullet_damage * 1.15) + 1
        elif uid == "triple_shot":
            player.triple_shot_active = True
        elif uid == "homing":
            player.homing_active = True
            
        self.game.audio_manager.play_power_up_sound()
        
        from src.lib.game_state import GameState
        self.game.state = GameState.PLAYING

    def draw(self, events):
        if self.game.state.name != "LEVEL_UP":
            return

        self._draw_particles()
        self._draw_panel()

        # Title
        self.draw_title("LEVEL UP!", y_abs=self._panel.y - 70)
        
        # Choose label
        self.draw_label("Choose an upgrade:", self._panel.y + 20, YELLOW)

        self._handle_buttons(events)
        
        # Draw descriptions below buttons
        for i, btn in enumerate(self._buttons):
            desc = self.offered_upgrades[i]["desc"]
            rendered = self._font_hint.render(desc, True, SCORE_COL)
            self.screen.blit(rendered, (btn.rect.centerx - rendered.get_width()//2, btn.rect.bottom + 5))
