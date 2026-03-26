import pygame

class Bullet:
    def __init__(self, x, y, direction, speed=15, is_enemy_bullet=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 5
        self.is_enemy_bullet = is_enemy_bullet
        self.color = (255, 50, 50) if is_enemy_bullet else (255, 255, 0)
        self.active = True

        dirs = {"left": (-speed, 0), "right": (speed, 0), "up": (0, -speed), "down": (0, speed)}
        self.vel_x, self.vel_y = dirs.get(direction, (speed, 0))

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def check_ground_collision(self, ground_y):
        return self.y >= ground_y

    def is_off_screen(self, world_width, world_height):
        return self.x < 0 or self.x > world_width or self.y < 0 or self.y > world_height

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def draw(self, screen, camera):
        sx, sy = camera.apply(self.x, self.y)
        pygame.draw.circle(screen, self.color, (int(sx), int(sy)), int(self.size * camera.zoom))


class Gun:
    def __init__(self):
        self.has_gun = False
        self.bullets = []
        self.fire_cooldown = 0
        self.fire_rate = 15
        self.max_bullets = 50
        self.ammo = self.max_bullets
        self.unlimited_ammo = False

    def pickup_gun(self):
        self.has_gun = True
        self.ammo = self.max_bullets

    def shoot(self, px, py, psize, direction):
        if not self.has_gun or self.fire_cooldown > 0:
            return False
        if self.ammo <= 0 and not self.unlimited_ammo:
            return False
        self.bullets.append(Bullet(px + psize / 2, py + psize / 2, direction))
        self.fire_cooldown = self.fire_rate
        if not self.unlimited_ammo:
            self.ammo -= 1
        return True

    def update(self, world_width, world_height, ground_y):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        for b in self.bullets[:]:
            b.update()
            if b.check_ground_collision(ground_y) or b.is_off_screen(world_width, world_height):
                self.bullets.remove(b)

    def draw(self, screen, camera):
        for b in self.bullets:
            b.draw(screen, camera)

    def reset(self):
        self.has_gun = False
        self.bullets.clear()
        self.fire_cooldown = 0
        self.ammo = self.max_bullets