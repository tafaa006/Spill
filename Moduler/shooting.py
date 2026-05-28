import pygame

kule_bredde = 10
kule_hoyde = 4
kule_fart = 12

class Pistol:
    def __init__(self):
        self.har_pistol = False
        self.kuler = []
        self.skyte_ventetid = 0
        self.patroner = 50

    def plukk_pistol(self):
        self.har_pistol = True
        self.patroner = 50

    def skyt(self, sx, sy, storrelse, retning):
        if not self.har_pistol or self.skyte_ventetid > 0 or self.patroner <= 0:
            return

        kx = sx + storrelse // 2
        ky = sy + storrelse // 2

        if retning == "venstre":
            self.kuler.append([kx, ky, -kule_fart, 0])
        elif retning == "hoyre":
            self.kuler.append([kx, ky, kule_fart, 0])
        elif retning == "opp":
            self.kuler.append([kx, ky, 0, -kule_fart])
        elif retning == "ned":
            self.kuler.append([kx, ky, 0, kule_fart])

        self.skyte_ventetid = 15
        self.patroner -= 1

    def oppdater(self, verden_bredde, verden_hoyde, bakke_y):
        if self.skyte_ventetid > 0:
            self.skyte_ventetid -= 1

        for kule in self.kuler[:]:
            kule[0] += kule[2]
            kule[1] += kule[3]
            if kule[0] < 0 or kule[0] > verden_bredde or kule[1] < 0 or kule[1] > bakke_y:
                self.kuler.remove(kule)

    def tegn(self, skjerm, kamera):
        for kule in self.kuler:
            sx, sy = kamera.bruk(kule[0], kule[1])
            pygame.draw.rect(skjerm, (255, 255, 0), (sx, sy, kule_bredde, kule_hoyde))

    def nullstill(self):
        self.har_pistol = False
        self.kuler = []
        self.skyte_ventetid = 0
        self.patroner = 50
