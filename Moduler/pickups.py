import pygame

class Pickup:
    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.size = 30
        self.type = pickup_type
        self.collected = False
        self.color = (255, 100, 100)

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
        sx, sy = camera.apply(self.x, self.y)
        pygame.draw.rect(screen, self.color, (sx, sy, self.size, self.size))


class PickupManager:
    def __init__(self):
        self.pickups = []

    def add_pickup(self, x, y, pickup_type):
        self.pickups.append(Pickup(x, y, pickup_type))

    def update(self, px, py, psize, gun):
        for pickup in self.pickups[:]:
            if pickup.check_collision(px, py, psize):
                if pickup.type == "gun":
                    gun.pickup_gun()
                self.pickups.remove(pickup)

    def draw(self, screen, camera):
        for p in self.pickups:
            p.draw(screen, camera)

    def reset(self):
        self.pickups = []
