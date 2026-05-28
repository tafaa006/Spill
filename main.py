import pygame
import sys
from Moduler.player import Spiller
from Moduler.camera import Kamera
from Moduler.world import Verden
from Moduler.menu import Meny
from Moduler.shooting import Pistol
from Moduler.pickups import GjenstandStyrer
from Moduler.enemies import FiendeStyrer, GoombaStyrer
from Moduler.kart import Kart

pygame.init()

BREDDE = 800
HOYDE = 600
skjerm = pygame.display.set_mode((BREDDE, HOYDE), pygame.RESIZABLE)
pygame.display.set_caption("Gravity Square")
klokke = pygame.time.Clock()
skrift = pygame.font.SysFont(None, 30)

spill_tilstand = "meny"
spiller_liv = 100
drap = 0

kart = Kart()
verden = Verden(kart)
kamera = Kamera(BREDDE, HOYDE)
spiller = Spiller(kart.verden_bredde // 2 - 20, kart.bakke_y - 40)
pistol = Pistol()
gjenstand_styrer = GjenstandStyrer()
fiende_styrer = FiendeStyrer()
goomba_styrer = GoombaStyrer()
meny = Meny(BREDDE, HOYDE)

def lag_brett():
    gjenstand_styrer.nullstill()
    fiende_styrer.nullstill()
    goomba_styrer.nullstill()

    gjenstand_styrer.legg_til(3600, verden.bakke_y - 50, "pistol")

    goomba_styrer.legg_til_goomba(400, verden.bakke_y - 40)
    goomba_styrer.legg_til_goomba(700, verden.bakke_y - 40)
    goomba_styrer.legg_til_goomba(1100, verden.bakke_y - 40)
    goomba_styrer.legg_til_goomba(1500, verden.bakke_y - 40)

    fiende_styrer.legg_til_fiende(900, verden.bakke_y - 40, "stille")
    fiende_styrer.legg_til_fiende(1600, verden.bakke_y - 40, "bevegelig")

def tegn_ui():
    pygame.draw.rect(skjerm, (100, 0, 0), (300, 10, 200, 20))
    pygame.draw.rect(skjerm, (0, 255, 0), (300, 10, spiller_liv * 2, 20))
    pygame.draw.rect(skjerm, (255, 255, 255), (300, 10, 200, 20), 2)
    skjerm.blit(skrift.render(f"Liv: {spiller_liv}", True, (255, 255, 255)), (310, 12))
    skjerm.blit(skrift.render(f"drap: {drap}", True, (255, 255, 255)), (10, 40))
    if pistol.har_pistol:
        skjerm.blit(skrift.render(f"Patroner: {pistol.patroner}", True, (255, 255, 255)), (10, 10))

kjorer = True
while kjorer:
    for hendelse in pygame.event.get():
        if hendelse.type == pygame.QUIT:
            kjorer = False

        if hendelse.type == pygame.VIDEORESIZE:
            BREDDE, HOYDE = hendelse.w, hendelse.h
            skjerm = pygame.display.set_mode((BREDDE, HOYDE), pygame.RESIZABLE)
            meny.oppdater_storrelse(BREDDE, HOYDE)
            kamera.skjerm_bredde = BREDDE
            kamera.skjerm_hoyde = HOYDE

        if spill_tilstand == "meny":
            handling = meny.les_hendelse(hendelse)
            if handling == "avslutt":
                kjorer = False
            elif handling == "spill":
                spill_tilstand = "spill"
                spiller_liv = 100
                spiller.nullstill(kart.verden_bredde // 2 - 20, kart.bakke_y - 40)
                kamera.nullstill()
                pistol.nullstill()
                lag_brett()

        elif spill_tilstand == "spill":
            if hendelse.type == pygame.KEYDOWN and hendelse.key == pygame.K_SPACE:
                pistol.skyt(spiller.x, spiller.y, spiller.storrelse, spiller.skyte_retning())
            spiller.les_input(hendelse)
            if hendelse.type == pygame.KEYDOWN and hendelse.key == pygame.K_ESCAPE:
                spill_tilstand = "meny"
                meny.nullstill()

    if spill_tilstand == "meny":
        meny.oppdater()
        meny.tegn(skjerm)

    elif spill_tilstand == "spill":
        spiller.oppdater(verden.bredde)

        if spiller.sjekk_kollisjon(kart.hent_plattformer()):
            spill_tilstand = "meny"
            meny.nullstill()

        goomba_resultat = goomba_styrer.sjekk_spiller_kollisjon(spiller.x, spiller.y, spiller.storrelse, spiller.fart_y)
        if goomba_resultat == "trakk":
            spiller.fart_y = -10
            drap += 1
        elif goomba_resultat == "skadet":
            spill_tilstand = "meny"
            meny.nullstill()

        kamera.oppdater(spiller.x + spiller.storrelse // 2, spiller.y + spiller.storrelse // 2)
        pistol.oppdater(verden.bredde, verden.hoyde, verden.bakke_y)
        gjenstand_styrer.oppdater(spiller.x, spiller.y, spiller.storrelse, pistol)
        goomba_styrer.oppdater(kart.hent_plattformer(), verden.bredde)
        fiende_styrer.oppdater(spiller.x, spiller.y, pistol.kuler, verden.bredde)

        if fiende_styrer.sjekk_spiller_treff(pygame.Rect(spiller.x, spiller.y, spiller.storrelse, spiller.storrelse)):
            spiller_liv -= 10
            if spiller_liv <= 0:
                spill_tilstand = "meny"
                meny.nullstill()

        verden.tegn(skjerm, kamera)
        gjenstand_styrer.tegn(skjerm, kamera)
        goomba_styrer.tegn(skjerm, kamera)
        fiende_styrer.tegn(skjerm, kamera)
        spiller.tegn(skjerm, kamera)
        pistol.tegn(skjerm, kamera)
        tegn_ui()

    pygame.display.flip()
    klokke.tick(60)

pygame.quit()
sys.exit()
