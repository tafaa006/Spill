import pygame

class World:
    def __init__(self, width, height, ground_y):
        self.width = width
        self.height = height
        self.ground_y = ground_y
        self.ground_color = (240, 240, 240)
        self.bg_color = (30, 30, 30)

    def draw(self, screen, camera):
        screen.fill(self.bg_color)
        ground_rect = pygame.Rect(0, self.ground_y, self.width, self.height - self.ground_y)
        pygame.draw.rect(screen, self.ground_color, camera.apply_rect(ground_rect))

        