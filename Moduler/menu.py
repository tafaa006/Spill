import pygame

BAKGRUNN_FARGE = (30, 30, 30)
KNAPP_FARGE = (70, 130, 180)
HOVER_FARGE = (100, 170, 220)
TEKST_FARGE = (255, 255, 255)

class Knapp:
    def __init__(self, tekst, x, y, bredde, hoyde):
        self.tekst = tekst
        self.boks = pygame.Rect(x, y, bredde, hoyde)

    def tegn(self, flate, skrift):
        farge = HOVER_FARGE if self.boks.collidepoint(pygame.mouse.get_pos()) else KNAPP_FARGE
        pygame.draw.rect(flate, farge, self.boks)
        pygame.draw.rect(flate, (0, 0, 0), self.boks, 2)
        tekst_flate = skrift.render(self.tekst, True, TEKST_FARGE)
        tekst_boks = tekst_flate.get_rect(center=self.boks.center)
        flate.blit(tekst_flate, tekst_boks)

    def klikket(self, hendelse):
        return (
            hendelse.type == pygame.MOUSEBUTTONDOWN
            and hendelse.button == 1
            and self.boks.collidepoint(hendelse.pos)
        )


class Meny:
    def __init__(self, skjerm_bredde, skjerm_hoyde):
        self.skjerm_bredde = skjerm_bredde
        self.skjerm_hoyde = skjerm_hoyde
        self.skrift = pygame.font.SysFont(None, 36)

        self.knapper = [
            Knapp("Spill", skjerm_bredde // 2 - 100, 200, 200, 50),
            Knapp("Avslutt", skjerm_bredde // 2 - 100, 270, 200, 50),
        ]

        self.tittel_bilde = None
        try:
            self.tittel_bilde = pygame.image.load("Bilder/grafyx.png").convert_alpha()
        except:
            pass

        self.musikk_spilles = False
        try:
            pygame.mixer.music.load("LydEffekter/MenuLyd.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
            self.musikk_spilles = True
        except:
            pass

    def oppdater_storrelse(self, skjerm_bredde, skjerm_hoyde):
        self.skjerm_bredde = skjerm_bredde
        self.skjerm_hoyde = skjerm_hoyde
        self.knapper[0].boks = pygame.Rect(skjerm_bredde // 2 - 100, 200, 200, 50)
        self.knapper[1].boks = pygame.Rect(skjerm_bredde // 2 - 100, 270, 200, 50)

    def les_hendelse(self, hendelse):
        for knapp in self.knapper:
            if knapp.klikket(hendelse):
                if knapp.tekst == "Spill":
                    if self.musikk_spilles:
                        pygame.mixer.music.stop()
                        self.musikk_spilles = False
                    return "spill"
                if knapp.tekst == "Avslutt":
                    return "avslutt"
        return None

    def oppdater(self):
        pass

    def tegn(self, skjerm):
        skjerm.fill(BAKGRUNN_FARGE)

        if self.tittel_bilde:
            bilde = pygame.transform.scale(self.tittel_bilde, (300, 100))
            skjerm.blit(bilde, (self.skjerm_bredde // 2 - 150, 80))
        else:
            tittel = self.skrift.render("Gravity Square", True, (255, 255, 255))
            skjerm.blit(tittel, (self.skjerm_bredde // 2 - tittel.get_width() // 2, 120))

        for knapp in self.knapper:
            knapp.tegn(skjerm, self.skrift)

    def nullstill(self):
        if not self.musikk_spilles:
            try:
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                self.musikk_spilles = True
            except:
                pass
