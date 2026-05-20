import pygame

class World:
    def __init__(self, game_map):
        self.map = game_map
        self.width = game_map.world_width
        self.height = game_map.world_height
        self.ground_y = game_map.ground_y
        self.bg_color = (30, 30, 30)

    def draw(self, screen, camera):
        screen.fill(self.bg_color)
        self.map.draw_world(screen, camera)
