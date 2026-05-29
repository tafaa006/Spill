import pygame
import math


class Fiende:
    def __init__(self, x, y, sort):
        self.x = x
        self.y = y
        self.storrelse = 40
        self.sort = sort
        self.liv = 3
        self.lever = True
        self.treff_teller = 0
        self.retning = 1
        self.patrulje_venstre = x - 150
        self.patrulje_hoyre = x + 150

    def ta_skade(self):
        self.liv -= 1
        self.treff_teller = 10
        if self.liv <= 0:
            self.lever = False

    def oppdater(self, spiller_x, spiller_y, verden_bredde):
        if self.treff_teller > 0:
            self.treff_teller -= 1
        avstand = math.sqrt((spiller_x - self.x) ** 2 + (spiller_y - self.y) ** 2)
        if avstand < 400:
            if spiller_x < self.x:
                self.x -= 2
            elif spiller_x > self.x:
                self.x += 2
        elif self.sort == "bevegelig":
            self.x += 2 * self.retning
            if self.x <= self.patrulje_venstre or self.x >= self.patrulje_hoyre:
                self.retning *= -1

    def hent_boks(self):
        return pygame.Rect(self.x, self.y, self.storrelse, self.storrelse)

    def tegn(self, skjerm, kamera_x, kamera_y):
        sx = self.x - kamera_x
        sy = self.y - kamera_y
        farge = (255, 200, 200) if self.treff_teller > 0 else (255, 0, 0)
        pygame.draw.rect(skjerm, farge, (sx, sy, self.storrelse, self.storrelse))
        liv_bredde = int(self.storrelse * (self.liv / 3))
        pygame.draw.rect(skjerm, (100, 0, 0), (sx, sy - 10, self.storrelse, 5))
        pygame.draw.rect(skjerm, (0, 255, 0), (sx, sy - 10, liv_bredde, 5))


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.storrelse = 40
        self.lever = True
        self.retning = 1
        self.fart_y = 0

    def oppdater(self, plattformer, verden_bredde):
        self.x += 2 * self.retning
        self.fart_y += 0.6
        self.fart_y = min(self.fart_y, 20)
        self.y += self.fart_y

        if self.x <= 0 or self.x >= verden_bredde - self.storrelse:
            self.retning *= -1

        g_boks = pygame.Rect(self.x, self.y, self.storrelse, self.storrelse)
        for boks, flis_type in plattformer:
            if not g_boks.colliderect(boks):
                continue
            overlapp_venstre = (self.x + self.storrelse) - boks.left
            overlapp_hoyre = boks.right - self.x
            overlapp_topp = (self.y + self.storrelse) - boks.top
            overlapp_bunn = boks.bottom - self.y
            minst = min(overlapp_venstre, overlapp_hoyre, overlapp_topp, overlapp_bunn)
            if minst == overlapp_topp and self.fart_y >= 0:
                self.y = boks.top - self.storrelse
                self.fart_y = 0
            elif minst == overlapp_venstre or minst == overlapp_hoyre:
                self.retning *= -1

    def tegn(self, skjerm, kamera_x, kamera_y):
        sx = self.x - kamera_x
        sy = self.y - kamera_y
        pygame.draw.rect(skjerm, (139, 90, 43), (sx, sy, self.storrelse, self.storrelse))
        pygame.draw.rect(skjerm, (0, 0, 0), (sx, sy, self.storrelse, self.storrelse), 2)
