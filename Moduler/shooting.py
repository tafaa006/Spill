import pygame

bullet_width = 10
bullet_height = 4
bullet_speed = 8


class Gun:
    def __init__(self):
        self.has_gun = False
        self.bullets = []
        self.fire_cooldown = 0
        self.ammo = 50

    def pickup_gun(self):
        self.has_gun = True
        self.ammo = 50

    def shoot(self, px, py, psize, direction):
        if not self.has_gun or self.fire_cooldown > 0 or self.ammo <= 0:
            return

        bx = px + psize // 2
        by = py + psize // 2

        if direction == "left":
            self.bullets.append([bx, by, -bullet_speed, 0])
        elif direction == "right":
            self.bullets.append([bx, by, bullet_speed, 0])
        elif direction == "up":
            self.bullets.append([bx, by, 0, -bullet_speed])
        elif direction == "down":
            self.bullets.append([bx, by, 0, bullet_speed])

        self.fire_cooldown = 15
        self.ammo -= 1

    def update(self, world_width, world_height, ground_y):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if bullet[0] < 0 or bullet[0] > world_width or bullet[1] < 0 or bullet[1] > ground_y:
                self.bullets.remove(bullet)

    def get_bullet_rects(self):
        rects = []
        for bullet in self.bullets:
            rects.append((pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height), bullet))
        return rects

    def draw(self, screen, camera):
        for bullet in self.bullets:
            sx, sy = camera.apply(bullet[0], bullet[1])
            pygame.draw.rect(screen, (255, 255, 0), (sx, sy, bullet_width, bullet_height))

    def reset(self):
        self.has_gun = False
        self.bullets = []
        self.fire_cooldown = 0
        self.ammo = 50
