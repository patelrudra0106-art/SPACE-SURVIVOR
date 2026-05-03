import pygame


class HealthBar:
    def __init__(self, max_health: int, current_health: int , x: int, y: int , width: int = 200, height: int = 20):
        self.max_health = max_health
        self.current_health = current_health
        self.x = x
        self.y = y
        
        self.width = width
        self.height = height
        
        

    def draw(self, screen: pygame.Surface , health: int , x: int , y: int):
        ratio = health / self.max_health
        
        pygame.draw.rect(screen, "red", pygame.Rect(x, y, self.width, self.height))
        pygame.draw.rect(screen, "green", pygame.Rect(x, y, self.width * ratio, self.height))