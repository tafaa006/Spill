import pygame

firkant_storrelse = 40
fart = 5

class Spiller:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.storrelse = firkant_storrelse
        self.fart_x = 0
        self.fart_y = 0
        self.pa_bakken = False
        self.hopp_igjen = 2
        self.dash_ventetid = 0
        self.dasher = False
        self.dash_teller = 0
        self.siste_retning = "hoyre"

    def skyte_retning(self):
        taster = pygame.key.get_pressed()
        if taster[pygame.K_LEFT] or taster[pygame.K_a]:
            return "venstre"
        if taster[pygame.K_RIGHT] or taster[pygame.K_d]:
            return "hoyre"
        if taster[pygame.K_UP] or taster[pygame.K_w]:
            return "opp"
        if taster[pygame.K_DOWN] or taster[pygame.K_s]:
            return "ned"
        return self.siste_retning

    def les_input(self, hendelse):
        if hendelse.type == pygame.KEYDOWN:
            if hendelse.key in (pygame.K_LEFT, pygame.K_a):
                self.siste_retning = "venstre"
            elif hendelse.key in (pygame.K_RIGHT, pygame.K_d):
                self.siste_retning = "hoyre"
            elif hendelse.key in (pygame.K_UP, pygame.K_w):
                self.siste_retning = "opp"
            elif hendelse.key in (pygame.K_DOWN, pygame.K_s):
                self.siste_retning = "ned"

            if hendelse.key in (pygame.K_UP, pygame.K_w) and self.hopp_igjen > 0:
                self.fart_y = -12
                self.hopp_igjen -= 1

            if hendelse.key == pygame.K_q and self.dash_ventetid == 0:
                self.dasher = True
                self.dash_teller = 10
                self.dash_ventetid = 60
                if self.siste_retning == "venstre":
                    self.fart_x = -15
                elif self.siste_retning == "hoyre":
                    self.fart_x = 15
                elif self.siste_retning == "opp":
                    self.fart_y = -15
                elif self.siste_retning == "ned":
                    self.fart_y = 15

    def oppdater(self, verden_bredde):
        if self.dash_ventetid > 0:
            self.dash_ventetid -= 1
        if self.dash_teller > 0:
            self.dash_teller -= 1
        else:
            self.dasher = False

        if not self.dasher:
            taster = pygame.key.get_pressed()
            if taster[pygame.K_LEFT] or taster[pygame.K_a]:
                self.fart_x = -fart
            elif taster[pygame.K_RIGHT] or taster[pygame.K_d]:
                self.fart_x = fart
            else:
                self.fart_x = 0

        self.x += self.fart_x
        self.x = max(0, min(verden_bredde - self.storrelse, self.x))

        self.fart_y += 0.6
        self.fart_y = min(self.fart_y, 20)
        self.y += self.fart_y
        if self.y < 0:
            self.y = 0
            self.fart_y = 0

    def sjekk_kollisjon(self, plattformer):
        self.pa_bakken = False
        drept = False

        for boks, flis_type in plattformer:
            spiller_boks = pygame.Rect(self.x, self.y, self.storrelse, self.storrelse)
            if not spiller_boks.colliderect(boks):
                continue

            if flis_type == "2":
                drept = True
                continue

            overlapp_venstre = (self.x + self.storrelse) - boks.left
            overlapp_hoyre = boks.right - self.x
            overlapp_topp = (self.y + self.storrelse) - boks.top
            overlapp_bunn = boks.bottom - self.y
            minst = min(overlapp_venstre, overlapp_hoyre, overlapp_topp, overlapp_bunn)

            if minst == overlapp_topp and self.fart_y >= 0:
                self.y = boks.top - self.storrelse
                self.fart_y = 0
                self.pa_bakken = True
                self.hopp_igjen = 2
            elif minst == overlapp_bunn and self.fart_y < 0:
                self.y = boks.bottom
                self.fart_y = 0
            elif minst == overlapp_venstre:
                self.x = boks.left - self.storrelse
            elif minst == overlapp_hoyre:
                self.x = boks.right

        return drept

    def tegn(self, skjerm, kamera_x, kamera_y):
        sx = self.x - kamera_x
        sy = self.y - kamera_y
        farge = (255, 0, 255) if self.dasher else (0, 200, 255)
        pygame.draw.rect(skjerm, farge, (sx, sy, self.storrelse, self.storrelse))

    def nullstill(self, x, y):
        self.x = x
        self.y = y
        self.fart_x = 0
        self.fart_y = 0
        self.pa_bakken = False
        self.hopp_igjen = 2
        self.dash_ventetid = 0
        self.dasher = False
        self.dash_teller = 0
        self.siste_retning = "hoyre"
