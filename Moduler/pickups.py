import pygame

class Gjenstand:
    def __init__(self, x, y, sort):
        self.x = x
        self.y = y
        self.storrelse = 30
        self.sort = sort
        self.plukket = False
        self.farge = (255, 100, 100)

    def sjekk_kollisjon(self, sx, sy, s_storrelse):
        if self.plukket:
            return False
        if pygame.Rect(self.x, self.y, self.storrelse, self.storrelse).colliderect(pygame.Rect(sx, sy, s_storrelse, s_storrelse)):
            self.plukket = True
            return True
        return False

    def tegn(self, skjerm, kamera):
        if self.plukket:
            return
        sx, sy = kamera.bruk(self.x, self.y)
        pygame.draw.rect(skjerm, self.farge, (sx, sy, self.storrelse, self.storrelse))


class GjenstandStyrer:
    def __init__(self):
        self.gjenstander = []

    def legg_til(self, x, y, sort):
        self.gjenstander.append(Gjenstand(x, y, sort))

    def oppdater(self, sx, sy, s_storrelse, pistol):
        for gjenstand in self.gjenstander[:]:
            if gjenstand.sjekk_kollisjon(sx, sy, s_storrelse):
                if gjenstand.sort == "pistol":
                    pistol.plukk_pistol()
                self.gjenstander.remove(gjenstand)

    def tegn(self, skjerm, kamera):
        for g in self.gjenstander:
            g.tegn(skjerm, kamera)

    def nullstill(self):
        self.gjenstander = []
