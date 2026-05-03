import pygame
from src.lib.game_utility import get_path

# Layers ordered back → front, with increasing parallax factor
_LAYER_FILES = [
    "parallax-space-backgound.png",   # deepest – barely moves
    "parallax-space-stars.png",
    "parallax-space-big-planet.png",
    "parallax-space-far-planets.png",
    "parallax-space-ring-planet.png",  # closest – moves most
]

# How much each layer shifts per pixel of mouse offset from center.
_PARALLAX_FACTORS = [0.010, 0.025, 0.06, 0.10, 0.16]


class ParallaxBackground:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width = game.game_width
        self.height = game.game_height

        self.current_theme = "void"
        self.themes = {
            "void": {"tint": None},
            "nebula": {"tint": (150, 100, 255)}, # Purple
            "inferno": {"tint": (255, 100, 100)}, # Red
            "abyss": {"tint": (100, 255, 255)},  # Teal/Blue
        }

        self.layers: list[pygame.Surface] = []
        self._raw_layers: list[pygame.Surface] = [] # Store original for re-tinting
        self.load_layers()

    def load_layers(self):
        self._raw_layers = []
        for filename in _LAYER_FILES:
            img = pygame.image.load(
                get_path(filename, "images", "background")
            ).convert_alpha()
            img = pygame.transform.scale(img, (self.width, self.height))
            self._raw_layers.append(img)
        self.apply_theme()

    def apply_theme(self):
        self.layers = []
        tint = self.themes[self.current_theme]["tint"]
        for img in self._raw_layers:
            if tint:
                tinted = img.copy()
                # Create a tint surface
                tint_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                
                # To make the tint subtle, we mix it with white (255, 255, 255)
                intensity = 0.5 # 50% tint strength
                r = int(255 - (255 - tint[0]) * intensity)
                g = int(255 - (255 - tint[1]) * intensity)
                b = int(255 - (255 - tint[2]) * intensity)
                
                # Alpha MUST be 255 here, otherwise BLEND_RGBA_MULT makes the whole layer transparent
                tint_surf.fill((r, g, b, 255))
                tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.layers.append(tinted)
            else:
                self.layers.append(img)

    def update_theme_by_level(self, level):
        new_theme = "void"
        if level > 30: new_theme = "abyss"
        elif level > 20: new_theme = "inferno"
        elif level > 10: new_theme = "nebula"
        
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme()

    def reset(self, mode=None):
        """Reload and update theme based on level."""
        self.update_theme_by_level(self.game.game_level)

    def draw(self, surface=None):
        """Draw all layers shifted based on current mouse position."""
        if surface is None:
            surface = self.screen

        mx, my = pygame.mouse.get_pos()
        cx, cy = self.width / 2, self.height / 2
        dx, dy = mx - cx, my - cy

        for i, layer in enumerate(self.layers):
            factor = _PARALLAX_FACTORS[i]
            # Wrap offset so it stays within one tile width/height
            ox = (-dx * factor) % self.width
            oy = (-dy * factor) % self.height

            # Draw a 2×2 grid so edges are always covered
            for tx in range(-1, 2):
                for ty in range(-1, 2):
                    bx = ox + tx * self.width - self.width
                    by = oy + ty * self.height - self.height
                    if -self.width < bx < self.width and -self.height < by < self.height:
                        surface.blit(layer, (bx, by))



