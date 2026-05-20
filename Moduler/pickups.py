import pygame
import math

class Pickup:
    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.size = 30
        self.type = pickup_type
        self.collected = False
        self.float_offset = 0
        self.float_speed = 0.1

        colors = {
            "gun": ((255, 100, 100), (50, 50, 50)),
            "ammo": ((255, 255, 100), (100, 100, 0)),
            "health": ((100, 255, 100), (0, 100, 0)),
        }
        self.color, self.icon_color = colors.get(pickup_type, ((255, 255, 255), (0, 0, 0)))

    def update(self):
        self.float_offset += self.float_speed

    def check_collision(self, px, py, psize):
        if self.collected:
            return False
        if pygame.Rect(self.x, self.y, self.size, self.size).colliderect(pygame.Rect(px, py, psize, psize)):
            self.collected = True
            return True
        return False

    def draw(self, screen, camera):
        if self.collected:
            return
        fy = self.y + math.sin(self.float_offset) * 5
        sx, sy = camera.apply(self.x, fy)
        sz = self.size * camera.zoom

        glow = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 50), (sz, sz), sz)
        screen.blit(glow, (sx - sz / 2, sy - sz / 2))

        pygame.draw.circle(screen, self.color, (int(sx), int(sy)), int(sz / 2))
        pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), int(sz / 2), 2)

        if self.type == "gun":
            gw, gh = sz * 0.5, sz * 0.3
            pygame.draw.rect(screen, self.icon_color, (sx - gw / 2, sy - gh / 2, gw, gh))

        elif self.type == "ammo":
            for i in range(3):
                aw, ah = sz * 0.15, sz * 0.4
                xo = (i - 1) * sz * 0.2
                pygame.draw.rect(screen, self.icon_color, (sx + xo - aw / 2, sy - ah / 2, aw, ah))

        elif self.type == "health":
            lw, ll = int(sz * 0.15), int(sz * 0.6)
            pygame.draw.rect(screen, self.icon_color, (sx - ll / 2, sy - lw / 2, ll, lw))
            pygame.draw.rect(screen, self.icon_color, (sx - lw / 2, sy - ll / 2, lw, ll))


class PickupManager:
    def __init__(self):
        self.pickups = []

    def add_pickup(self, x, y, pickup_type):
        self.pickups.append(Pickup(x, y, pickup_type))

    def update(self, px, py, psize, gun):
        for pickup in self.pickups[:]:
            pickup.update()
            if pickup.check_collision(px, py, psize):
                if pickup.type == "gun":
                    gun.pickup_gun()
                elif pickup.type == "ammo" and gun.has_gun:
                    gun.ammo = min(gun.max_bullets, gun.ammo + 10)
                self.pickups.remove(pickup)

    def draw(self, screen, camera):
        for p in self.pickups:
            p.draw(screen, camera)

    def reset(self):
        self.pickups.clear()
