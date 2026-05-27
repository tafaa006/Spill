import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.zoom = 1
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target_x, target_y):
        self.x = target_x - self.screen_width / 2
        self.y = target_y - self.screen_height / 2

    def apply(self, ex, ey):
        return ex - self.x, ey - self.y

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def reset(self):
        self.x = 0
        self.y = 0
