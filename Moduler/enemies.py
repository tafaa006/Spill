import pygame
import math



class Fiende:
    def __init__(self, x, y, sort="stille"):
        self.x = x
        self.y = y
        self.storrelse = 40
        self.sort = sort
        self.liv = 3
        self.lever = True
        self.treff_teller = 0
        self.fart = 2
        self.retning = 1
        self.patrulje_venstre = x - 150
        self.patrulje_hoyre = x + 150

    def ta_skade(self):
        self.liv -= 1
        self.treff_teller = 10
        if self.liv <= 0:
            self.lever = False

    def oppdater(self, sx, sy, verden_bredde):
        if not self.lever:
            return
        if self.treff_teller > 0:
            self.treff_teller -= 1

        avstand = math.sqrt((sx - self.x) ** 2 + (sy - self.y) ** 2)
        if avstand < 400:
            if sx < self.x:
                self.x -= self.fart
            elif sx > self.x:
                self.x += self.fart
        elif self.sort == "bevegelig":
            self.x += self.fart * self.retning
            if self.x <= self.patrulje_venstre or self.x >= self.patrulje_hoyre:
                self.retning *= -1

    def hent_boks(self):
        return pygame.Rect(self.x, self.y, self.storrelse, self.storrelse)

    def tegn(self, skjerm, kamera):
        if not self.lever:
            return
        sx, sy = kamera.bruk(self.x, self.y)
        farge = (255, 200, 200) if self.treff_teller > 0 else (255, 0, 0)
        pygame.draw.rect(skjerm, farge, (sx, sy, self.storrelse, self.storrelse))
        pygame.draw.rect(skjerm, (0, 0, 0), (sx, sy, self.storrelse, self.storrelse), 2)
        liv_bredde = int(self.storrelse * (self.liv / 3))
        pygame.draw.rect(skjerm, (100, 0, 0), (sx, sy - 10, self.storrelse, 5))
        pygame.draw.rect(skjerm, (0, 255, 0), (sx, sy - 10, liv_bredde, 5))


class FiendeStyrer:
    def __init__(self):
        self.fiender = []

    def legg_til_fiende(self, x, y, sort="stille"):
        self.fiender.append(Fiende(x, y, sort))

    def oppdater(self, sx, sy, kuler, verden_bredde):
        for f in self.fiender[:]:
            f.oppdater(sx, sy, verden_bredde)
            if not f.lever:
                self.fiender.remove(f)

        for f in self.fiender:
            for kule in kuler[:]:
                kule_boks = pygame.Rect(kule[0], kule[1], 10, 4)
                if f.hent_boks().colliderect(kule_boks):
                    f.ta_skade()
                    kuler.remove(kule)
                    break

    def sjekk_spiller_treff(self, spiller_boks):
        for f in self.fiender:
            if f.lever and f.hent_boks().colliderect(spiller_boks):
                return True
        return False

    def tegn(self, skjerm, kamera):
        for f in self.fiender:
            f.tegn(skjerm, kamera)

    def nullstill(self):
        self.fiender = []


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.storrelse = 40
        self.lever = True
        self.fart = 2
        self.retning = 1
        self.fart_y = 0

    def oppdater(self, plattformer, verden_bredde):
        if not self.lever:
            return

        self.x += self.fart * self.retning
        self.fart_y += 0.6
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

    def sjekk_spiller_kollisjon(self, sx, sy, s_storrelse, s_fart_y):
        if not self.lever:
            return None
        if not pygame.Rect(sx, sy, s_storrelse, s_storrelse).colliderect(pygame.Rect(self.x, self.y, self.storrelse, self.storrelse)):
            return None
        if s_fart_y > 0 and sy + s_storrelse - s_fart_y <= self.y + 10:
            self.lever = False
            return "trakk"
        return "skadet"

    def tegn(self, skjerm, kamera):
        if not self.lever:
            return
        sx, sy = kamera.bruk(self.x, self.y)
        pygame.draw.rect(skjerm, (139, 90, 43), (sx, sy, self.storrelse, self.storrelse))
        pygame.draw.rect(skjerm, (0, 0, 0), (sx, sy, self.storrelse, self.storrelse), 2)


class GoombaStyrer:
    def __init__(self):
        self.goombas = []

    def legg_til_goomba(self, x, y):
        self.goombas.append(Goomba(x, y))

    def oppdater(self, plattformer, verden_bredde):
        for g in self.goombas[:]:
            g.oppdater(plattformer, verden_bredde)
            if not g.lever:
                self.goombas.remove(g)

    def sjekk_spiller_kollisjon(self, sx, sy, s_storrelse, s_fart_y):
        for g in self.goombas:
            resultat = g.sjekk_spiller_kollisjon(sx, sy, s_storrelse, s_fart_y)
            if resultat:
                return resultat
        return None

    def tegn(self, skjerm, kamera):
        for g in self.goombas:
            g.tegn(skjerm, kamera)

    def nullstill(self):
        self.goombas = []
