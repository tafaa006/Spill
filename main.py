
import pygame
import sys
from Moduler.menu import Meny
from Moduler.enemies import Fiende, Goomba

pygame.init() # vet ikke

# spill størrelse
BREDDE = 800
HOYDE  = 600
skjerm = pygame.display.set_mode((BREDDE, HOYDE), pygame.RESIZABLE)
pygame.display.set_caption("Grafyx 777")

klokke = pygame.time.Clock()               # Holder FPS stabilt (60 fps)
skrift = pygame.font.SysFont(None, 30)     # Standard skrifttype til tekst


FLIS_STORRELSE = 80                                         # Pikselstørrelse per flis
FLIS_FARGER = {"1": (200, 200, 200), "2": (220, 60, 60)}  # Farge per flistype, bruker rgb

# mappet som er laget av 1,2 og 0. 1 er vanlig plattform, 2 er dødelig plattform, og 0 er luft.
labyrint = [
    "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "11111111111111111111111111111111111111111111111111111111111111111111111111111001",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000011",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000011",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000011",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000011",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000011",
    "10000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000011111111100000000000000000000000011",
    "10000000000000000000000000000000000000000000110000000110000000000000000000000001",
    "10000000000000000000000000000000000000000001100000000011000000000000000000000011",
    "10000000000000000000000000000000000000000011000000000000000000000000000000000001",
    "10000000000000000000000000000000000000011111000000000000110000000000000000000011",
    "10000000000000000000000000000000000001000011000000000001111000000000000000000001",
    "10000000000000000000000000000000000011100001000000000011111100000000000000000011",
    "11111111111000111111111111111111111111111111111111111111111111111111000001111111",
    "11111111111000111111111111111111111111111111111111111111111111111111000001111111",
    "11111111111222111111111111111111111111111111111111111111111111111111222221111111",
    "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
]

# Totalstørrelse på verden i piksler
verden_bredde = len(labyrint[0]) * FLIS_STORRELSE
verden_hoyde  = len(labyrint)    * FLIS_STORRELSE

# Bygg en liste med alle synlige rektangler
plattformer = []
for rad in range(len(labyrint)):
    for kol in range(len(labyrint[0])):
        flistype = labyrint[rad][kol]
        if flistype in FLIS_FARGER:
            boks = pygame.Rect(
                kol * FLIS_STORRELSE,   # x-posisjon (venstre kant)
                rad * FLIS_STORRELSE,   # y-posisjon (topp kant)
                FLIS_STORRELSE,         # bredde
                FLIS_STORRELSE          # høyde
            )
            plattformer.append((boks, flistype))

bakke_y = 0
for rad in range(len(labyrint) - 1, -1, -1):
    if labyrint[rad][1] == "0":
        bakke_y = (rad + 1) * FLIS_STORRELSE
        break

SPILLER_STORRELSE = 40   # Bredde og høyde på spilleren
SPILLER_FART      = 5    # Piksler per frame

spiller_x     = 0
spiller_y     = 0
spiller_fart_x = 0   # Horisontal hastighet
spiller_fart_y = 0   # Vertikal hastighet

pa_bakken    = False   # Er spilleren på bakken?
hopp_igjen   = 2       # Antall hopp igjen
dash_ventetid = 0      # Nedtelling til neste dash er mulig
dasher       = False   # Er spilleren midt i et dash?
dash_teller  = 0       # Frames igjen av dashbevegelsen
siste_retning = "hoyre" # Siste bevegelsesretning (brukes til skyting/dash)

kamera_x = 0
kamera_y = 0

# Kule-innstillinger
KULE_BREDDE = 10
KULE_HOYDE  = 4
KULE_FART   = 8

har_pistol    = False   # Har spilleren plukket opp pistolen?
kuler         = []      # Liste med aktive kuler
skyte_ventetid = 0      # Ventetid mellom hvert skudd (cooldown)
patroner      = 12      # Antall skudd igjen

# hvor pistolen spawner
pistol_x      = 3600
pistol_y      = bakke_y - 50
pistol_plukket = False

# liste av fiender og goombas
fiender = []
goombas = []

# Spillets tilstand og UI-data
spill_tilstand = "meny"   # starter gamet på meny
spiller_liv    = 100
drap           = 0
meny = Meny(BREDDE, HOYDE)


def lag_brett():
    global har_pistol, kuler, skyte_ventetid, patroner
    global pistol_plukket, fiender, goombas
    # verdiene for pistolen
    har_pistol     = False
    kuler          = []
    skyte_ventetid = 0
    patroner       = 12
    pistol_plukket = False

    # hvor chase fiendene skal bli plassert
    fiender = [
        Fiende(900,  bakke_y - 40, "stille"),
        Fiende(1600, bakke_y - 40, "bevegelig"),
    ]

    # hvor gombas skal bli plassert
    goombas = [
        Goomba(400,  bakke_y - 40),
        Goomba(700,  bakke_y - 40),
        Goomba(1100, bakke_y - 40),
        Goomba(1500, bakke_y - 40),
    ]


def nullstill_spiller():
    global spiller_x, spiller_y, spiller_fart_x, spiller_fart_y
    global pa_bakken, hopp_igjen, dash_ventetid, dasher, dash_teller, siste_retning
    global kamera_x, kamera_y

    # verdier for funksjonene som siste retning dashing cooldowns.
    spiller_x      = verden_bredde // 2 - 20   # Midten av verden
    spiller_y      = bakke_y - 40
    spiller_fart_x = 0
    spiller_fart_y = 0
    pa_bakken      = False
    hopp_igjen     = 2
    dash_ventetid  = 0
    dasher         = False
    dash_teller    = 0
    siste_retning  = "hoyre"
    kamera_x       = 0
    kamera_y       = 0


def skyte_retning():
    """Returnerer retningen spilleren sikter (basert på piltastene)."""
    taster = pygame.key.get_pressed()
    if taster[pygame.K_LEFT] or taster[pygame.K_a]:  return "venstre"
    if taster[pygame.K_RIGHT] or taster[pygame.K_d]: return "hoyre"
    if taster[pygame.K_UP] or taster[pygame.K_w]:    return "opp"
    if taster[pygame.K_DOWN] or taster[pygame.K_s]:  return "ned"
    return siste_retning   # returnerer siste retning, dette blir brukt for skyting og dashing.


def skyt():
    """Skyter en kule fra midten av spilleren i sikteretningen."""
    global skyte_ventetid, patroner

    if not har_pistol or skyte_ventetid > 0 or patroner <= 0:
        return   # stopper deg fra å skyte hvis du ikke har pistol, hvis du er i cooldown, eller hvis du er tom for ammo

    # så kulen sin posisjon starter på spilleren
    kx = spiller_x + SPILLER_STORRELSE // 2
    ky = spiller_y + SPILLER_STORRELSE // 2

    # hvilken retning kulen skal fly
    retning = skyte_retning()
    if retning == "venstre": kuler.append([kx, ky, -KULE_FART, 0])
    elif retning == "hoyre": kuler.append([kx, ky,  KULE_FART, 0])
    elif retning == "opp":   kuler.append([kx, ky, 0, -KULE_FART])
    elif retning == "ned":   kuler.append([kx, ky, 0,  KULE_FART])

    skyte_ventetid = 15   # Vent 15 frames før neste skudd
    patroner -= 1


def sjekk_kollisjon():
    global spiller_x, spiller_y, spiller_fart_x, spiller_fart_y, pa_bakken, hopp_igjen, dasher
    pa_bakken = False
    drept = False

    spiller_boks = pygame.Rect(spiller_x, spiller_y, SPILLER_STORRELSE, SPILLER_STORRELSE)

    for boks, flistype in plattformer:
        if not spiller_boks.colliderect(boks):
            continue 

        if flistype == "2":
            drept = True
            continue   # Dødelig flis – ikke skyv, men merk at spilleren døde

        # Beregn overlapp på alle fire sider
        overlapp_venstre = (spiller_x + SPILLER_STORRELSE) - boks.left
        overlapp_hoyre   = boks.right  - spiller_x
        overlapp_topp    = (spiller_y + SPILLER_STORRELSE) - boks.top
        overlapp_bunn    = boks.bottom - spiller_y

        # Finn den minste overlappen – det er den siden spilleren kom fra
        minst = min(overlapp_venstre, overlapp_hoyre, overlapp_topp, overlapp_bunn)

        if minst == overlapp_topp and spiller_fart_y >= 0:
            # basicly overlapping koden
            spiller_y      = boks.top - SPILLER_STORRELSE
            spiller_fart_y = 0
            pa_bakken      = True
            hopp_igjen     = 2
        elif minst == overlapp_bunn and spiller_fart_y < 0:
            spiller_y      = boks.bottom
            spiller_fart_y = 0
        elif minst == overlapp_venstre:
            spiller_x = boks.left - SPILLER_STORRELSE
        elif minst == overlapp_hoyre:
            spiller_x = boks.right

        spiller_boks = pygame.Rect(spiller_x, spiller_y, SPILLER_STORRELSE, SPILLER_STORRELSE)

    return drept


def tegn_ui():
    # Life-bar: rød bakgrunn, grønn forgrunn
    pygame.draw.rect(skjerm, (100, 0, 0),     (300, 10, 200, 20))             # Bakgrunn
    pygame.draw.rect(skjerm, (0, 255, 0),     (300, 10, spiller_liv * 2, 20)) # Forgrunn
    pygame.draw.rect(skjerm, (255, 255, 255), (300, 10, 200, 20), 2)          # Ramme

    skjerm.blit(skrift.render(f"Liv: {spiller_liv}", True, (255, 255, 255)), (310, 12))
    skjerm.blit(skrift.render(f"Drap: {drap}",       True, (255, 255, 255)), (10, 40))

    if har_pistol:
        skjerm.blit(skrift.render(f"Skudd: {patroner}", True, (255, 255, 255)), (10, 10)) # ammo

# gameloop
kjorer = True
while kjorer:
    for hendelse in pygame.event.get():

        if hendelse.type == pygame.QUIT:
            kjorer = False 

        if hendelse.type == pygame.VIDEORESIZE:
            BREDDE, HOYDE = hendelse.w, hendelse.h
            skjerm = pygame.display.set_mode((BREDDE, HOYDE), pygame.RESIZABLE)
            meny.oppdater_storrelse(BREDDE, HOYDE)

        if spill_tilstand == "meny": # basicly koden for menyen
            handling = meny.les_hendelse(hendelse)
            if handling == "avslutt":
                kjorer = False
            elif handling == "spill":
                spill_tilstand = "spill"
                spiller_liv    = 100
                drap           = 0
                nullstill_spiller()
                lag_brett()

        elif spill_tilstand == "spill":
            if hendelse.type == pygame.KEYDOWN:

                if hendelse.key == pygame.K_SPACE: # skyter
                    skyt()

                if hendelse.key == pygame.K_ESCAPE: # sender deg til start hvis du trykker på escape
                    spill_tilstand = "meny"
                    meny.nullstill()

                # Hopp med dobbeljump
                if hendelse.key in (pygame.K_UP, pygame.K_w) and hopp_igjen > 0:
                    spiller_fart_y = -12
                    hopp_igjen    -= 1

                # Oppdater siste retning basert på tastetrykk
                if hendelse.key in (pygame.K_LEFT,  pygame.K_a): siste_retning = "venstre"
                if hendelse.key in (pygame.K_RIGHT, pygame.K_d): siste_retning = "hoyre"
                if hendelse.key in (pygame.K_UP,    pygame.K_w): siste_retning = "opp"
                if hendelse.key in (pygame.K_DOWN,  pygame.K_s): siste_retning = "ned"

                # desher hvis du trykker på Q og deretter skrur på cooldown.
                if hendelse.key == pygame.K_q and dash_ventetid == 0:
                    dasher      = True
                    dash_teller = 10
                    dash_ventetid = 60

                    if siste_retning == "venstre": spiller_fart_x = -15
                    elif siste_retning == "hoyre": spiller_fart_x =  15
                    elif siste_retning == "opp":   spiller_fart_y = -15
                    elif siste_retning == "ned":   spiller_fart_y =  15

    if spill_tilstand == "meny":
        meny.oppdater()
        meny.tegn(skjerm)

    elif spill_tilstand == "spill":
        # dash cooldowns og sånt
        if dash_ventetid > 0: dash_ventetid -= 1
        if dash_teller   > 0: dash_teller   -= 1
        else:                 dasher = False

        if not dasher:
            taster = pygame.key.get_pressed()
            if taster[pygame.K_LEFT] or taster[pygame.K_a]:
                spiller_fart_x = -SPILLER_FART
            elif taster[pygame.K_RIGHT] or taster[pygame.K_d]:
                spiller_fart_x = SPILLER_FART
            else:
                spiller_fart_x = 0 

        spiller_x += spiller_fart_x
        spiller_x  = max(0, min(verden_bredde - SPILLER_STORRELSE, spiller_x))  # Klem innenfor kanten

        spiller_fart_y += 0.6
        spiller_fart_y  = min(spiller_fart_y, 20) 
        spiller_y      += spiller_fart_y

        if spiller_y < 0:
            spiller_y      = 0
            spiller_fart_y = 0

        # Kollisjon med plattformer
        if sjekk_kollisjon():   # Returnerer True ved dødelig platform
            spill_tilstand = "meny"
            meny.nullstill()

        # sjekker om du har plukket opp pistolen
        if not pistol_plukket:
            pistol_boks  = pygame.Rect(pistol_x, pistol_y, 30, 30)
            spiller_boks = pygame.Rect(spiller_x, spiller_y, SPILLER_STORRELSE, SPILLER_STORRELSE)
            if spiller_boks.colliderect(pistol_boks):
                pistol_plukket = True
                har_pistol     = True
                patroner       = 50

        if skyte_ventetid > 0:
            skyte_ventetid -= 1

        kuler_som_blir_igjen = []
        for kule in kuler:
            kule[0] += kule[2]  # Flytter til sidene i x-retning
            kule[1] += kule[3]  # Flytter opp og ned i y-retning
            er_utenfor = kule[0] < 0 or kule[0] > verden_bredde or kule[1] < 0 or kule[1] > bakke_y
            if not er_utenfor:
                kuler_som_blir_igjen.append(kule)
        kuler = kuler_som_blir_igjen

        # Kameraet følger spilleren og holder dem midt på skjermen
        kamera_x = spiller_x + SPILLER_STORRELSE // 2 - BREDDE // 2
        kamera_y = spiller_y + SPILLER_STORRELSE // 2 - HOYDE // 2

        for g in list(goombas):
            g.oppdater(plattformer, verden_bredde)

            if not g.lever:
                goombas.remove(g)
                continue

            spiller_boks = pygame.Rect(spiller_x, spiller_y, SPILLER_STORRELSE, SPILLER_STORRELSE)
            goomba_boks  = pygame.Rect(g.x, g.y, g.storrelse, g.storrelse)

            if spiller_boks.colliderect(goomba_boks):
                if spiller_fart_y > 0 and spiller_y + SPILLER_STORRELSE - spiller_fart_y <= g.y + 10:
                    g.lever        = False
                    spiller_fart_y = -10   # Litt rekyl-hopp
                    drap          += 1
                else:
                    # når spilleren treffer Goombaen fra siden dør dem
                    spill_tilstand = "meny"
                    meny.nullstill()

        for f in list(fiender): # går gjennom feiendene
            f.oppdater(spiller_x, spiller_y, verden_bredde)

            if not f.lever: # sjekker om fienden lever
                fiender.remove(f) # despawner fienden
                continue

            # Sjekker om en kule treffer fienden
            for kule in list(kuler):
                kule_boks = pygame.Rect(kule[0], kule[1], KULE_BREDDE, KULE_HOYDE)
                if f.hent_boks().colliderect(kule_boks): # kollisjon
                    f.ta_skade()
                    kuler.remove(kule) # fjerner kulen
                    break

            # Sjekker om fienden treffer spilleren
            spiller_boks = pygame.Rect(spiller_x, spiller_y, SPILLER_STORRELSE, SPILLER_STORRELSE)
            if f.lever and f.hent_boks().colliderect(spiller_boks):
                spiller_liv -= 10
                if spiller_liv <= 0: # når du dør
                    spill_tilstand = "meny"
                    meny.nullstill()


        skjerm.fill((30, 30, 30))   # Bakgrunnsfarge

        # tegner mappet
        for boks, flistype in plattformer:
            tegnet_boks = pygame.Rect(
                boks.x - kamera_x,
                boks.y - kamera_y,
                boks.width,
                boks.height
            )
            pygame.draw.rect(skjerm, FLIS_FARGER[flistype], tegnet_boks)

        # lager den rød boksen som gir deg pistolen
        if not pistol_plukket:
            pygame.draw.rect(skjerm, (255, 100, 100), (
                pistol_x - kamera_x,
                pistol_y - kamera_y,
                30, 30
            ))

        # tegner Goombas og fiender
        for g in goombas: g.tegn(skjerm, kamera_x, kamera_y)
        for f in fiender: f.tegn(skjerm, kamera_x, kamera_y)

        # tegner spilleren, den blir lilla hvis spilleren trykker på Q
        spiller_farge = (255, 0, 255) if dasher else (0, 200, 255)
        pygame.draw.rect(skjerm, spiller_farge, (
            spiller_x - kamera_x,
            spiller_y - kamera_y,
            SPILLER_STORRELSE,
            SPILLER_STORRELSE
        ))

        # lager kulene og sender dem en retning
        for kule in kuler:
            pygame.draw.rect(skjerm, (255, 255, 0), (
                kule[0] - kamera_x,
                kule[1] - kamera_y,
                KULE_BREDDE,
                KULE_HOYDE
            ))

        # tegner UI (liv, drap, skudd)
        tegn_ui()

    pygame.display.flip()
    klokke.tick(60)

pygame.quit()
sys.exit()