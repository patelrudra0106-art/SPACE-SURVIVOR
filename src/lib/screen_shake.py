import random

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.intensity = 0

    def get_offset(self):
        return self.offset_x, self.offset_y
