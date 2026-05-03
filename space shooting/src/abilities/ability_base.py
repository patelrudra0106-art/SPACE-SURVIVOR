class Ability:
    def __init__(self, game):
        self.game = game
        self.cooldown_timer = 0.0
        self.cooldown_max = 1.0  # Default cooldown
        self.duration_timer = 0.0
        self.is_active = False

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        if self.duration_timer > 0:
            self.duration_timer -= dt
        else:
            if self.is_active:
                self.deactivate()

    def is_ready(self):
        return self.cooldown_timer <= 0

    def activate(self):
        """Override this method to implement ability logic."""
        pass
        
    def deactivate(self):
        """Override this method to implement deactivation logic."""
        self.is_active = False
