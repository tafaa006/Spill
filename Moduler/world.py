import pygame

class Verden:
    def __init__(self, kart):
        self.kart = kart
        self.bredde = kart.verden_bredde
        self.hoyde = kart.verden_hoyde
        self.bakke_y = kart.bakke_y
        self.bakgrunn_farge = (30, 30, 30)

    def tegn(self, skjerm, kamera):
        skjerm.fill(self.bakgrunn_farge)
        self.kart.tegn_verden(skjerm, kamera)
