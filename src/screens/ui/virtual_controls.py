import pygame
import math
import sys

class VirtualControls:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width = game.game_width
        self.height = game.game_height
        
        self.is_mobile = sys.platform in ["android", "ios"]
        
        # Joystick settings
        self.joy_base_pos = (120, self.height - 120)
        self.joy_radius = 60
        self.joy_knob_radius = 30
        self.joy_knob_pos = list(self.joy_base_pos)
        self.joy_active = False
        self.joy_vector = [0.0, 0.0]
        
        # Button settings
        btn_radius = 45
        spacing = 110
        self.buttons = {
            "fire": {"pos": (self.width - 100, self.height - 100), "radius": btn_radius + 10, "color": (255, 100, 0), "label": "FIRE", "active": False},
            "dash": {"pos": (self.width - 210, self.height - 80), "radius": btn_radius, "color": (100, 100, 255), "label": "DASH", "active": False},
            "ult": {"pos": (self.width - 160, self.height - 190), "radius": btn_radius, "color": (255, 255, 0), "label": "ULT", "active": False}
        }
        
    def update(self):
        if not self.is_mobile: return
        if self.game.state.name != "PLAYING":
            self.joy_active = False
            for btn in self.buttons.values(): btn["active"] = False
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update Joystick
        dist_to_joy = math.hypot(mouse_pos[0] - self.joy_base_pos[0], mouse_pos[1] - self.joy_base_pos[1])
        
        if mouse_pressed:
            if dist_to_joy < self.joy_radius * 1.5 or self.joy_active:
                self.joy_active = True
                # Calculate vector and clamp knob
                dx = mouse_pos[0] - self.joy_base_pos[0]
                dy = mouse_pos[1] - self.joy_base_pos[1]
                angle = math.atan2(dy, dx)
                
                clamped_dist = min(dist_to_joy, self.joy_radius)
                self.joy_knob_pos[0] = self.joy_base_pos[0] + math.cos(angle) * clamped_dist
                self.joy_knob_pos[1] = self.joy_base_pos[1] + math.sin(angle) * clamped_dist
                
                # Normalized vector for movement
                self.joy_vector = [math.cos(angle) * (clamped_dist / self.joy_radius), 
                                   math.sin(angle) * (clamped_dist / self.joy_radius)]
        else:
            self.joy_active = False
            self.joy_knob_pos = list(self.joy_base_pos)
            self.joy_vector = [0.0, 0.0]
            
        # Update Buttons
        for name, btn in self.buttons.items():
            dist = math.hypot(mouse_pos[0] - btn["pos"][0], mouse_pos[1] - btn["pos"][1])
            if mouse_pressed and dist < btn["radius"]:
                if not btn["active"]: # Initial press
                    self._trigger_button(name)
                btn["active"] = True
            else:
                btn["active"] = False

    def _trigger_button(self, name):
        if name == "dash":
            if "dash" in self.game.player.abilities:
                self.game.player.abilities["dash"].activate()
        elif name == "ult":
            if "ultimate" in self.game.player.abilities:
                self.game.player.abilities["ultimate"].activate()

    def draw(self, surface):
        if not self.is_mobile: return
        if self.game.state.name != "PLAYING":
            return
            
        # Draw Joystick Base
        pygame.draw.circle(surface, (100, 100, 100, 100), self.joy_base_pos, self.joy_radius, 2)
        # Draw Joystick Knob
        knob_color = (255, 255, 255, 150) if self.joy_active else (200, 200, 200, 100)
        pygame.draw.circle(surface, knob_color, (int(self.joy_knob_pos[0]), int(self.joy_knob_pos[1])), self.joy_knob_radius)
        
        # Draw Buttons
        font = pygame.font.SysFont("Arial", 18, bold=True)
        for name, btn in self.buttons.items():
            alpha = 200 if btn["active"] else 100
            color = (*btn["color"], alpha)
            
            # Button circle
            s = pygame.Surface((btn["radius"]*2, btn["radius"]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (btn["radius"], btn["radius"]), btn["radius"])
            surface.blit(s, (btn["pos"][0] - btn["radius"], btn["pos"][1] - btn["radius"]))
            
            # Label
            label_surf = font.render(btn["label"], True, (255, 255, 255))
            surface.blit(label_surf, label_surf.get_rect(center=btn["pos"]))
