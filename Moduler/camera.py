import pygame

class Kamera:
    def __init__(self, skjerm_bredde, skjerm_hoyde):
        self.x = 0
        self.y = 0
        self.zoom = 1
        self.skjerm_bredde = skjerm_bredde
        self.skjerm_hoyde = skjerm_hoyde

    def oppdater(self, maal_x, maal_y):
        self.x = maal_x - self.skjerm_bredde / 2
        self.y = maal_y - self.skjerm_hoyde / 2

    def bruk(self, x, y):
        return x - self.x, y - self.y

    def bruk_boks(self, boks):
        return pygame.Rect(boks.x - self.x, boks.y - self.y, boks.width, boks.height)

    def nullstill(self):
        self.x = 0
        self.y = 0
