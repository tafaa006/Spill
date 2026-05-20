import pygame
import math
import random

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=8):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 5
        self.color = (255, 50, 50)
        self.active = True

        dx, dy = target_x - x, target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.vel_x = (dx / dist) * speed
            self.vel_y = (dy / dist) * speed
        else:
            self.vel_x = self.vel_y = 0

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


class Enemy:
    def __init__(self, x, y, enemy_type="static"):
        self.x = x
        self.y = y
        self.size = 40
        self.type = enemy_type
        self.health = 3
        self.max_health = 3
        self.alive = True

        self.color = (255, 0, 0)
        self.hit_color = (255, 200, 200)
        self.hit_timer = 0

        self.fire_cooldown = 0
        self.fire_rate = 60
        self.bullets = []
        self.detection_range = 400

        self.speed = 2
        self.direction = 1
        self.patrol_left = x - 150
        self.patrol_right = x + 150

    def take_damage(self):
        self.health -= 1
        self.hit_timer = 10
        if self.health <= 0:
            self.alive = False

    def can_see_player(self, px, py):
        return math.sqrt((px - self.x)**2 + (py - self.y)**2) < self.detection_range

    def shoot_at_player(self, px, py):
        if self.fire_cooldown > 0:
            return
        bx = self.x + self.size / 2
        by = self.y + self.size / 2
        self.bullets.append(Bullet(bx, by, px + 20, py + 20))
        self.fire_cooldown = self.fire_rate

    def update(self, px, py, world_width, ground_y):
        if not self.alive:
            return
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        if self.hit_timer > 0:
            self.hit_timer -= 1

        if self.type == "moving":
            self.x += self.speed * self.direction
            if self.x <= self.patrol_left or self.x >= self.patrol_right:
                self.direction *= -1

        if self.can_see_player(px, py):
            self.shoot_at_player(px, py)

        for b in self.bullets[:]:
            b.update()
            if b.check_ground_collision(ground_y) or b.is_off_screen(world_width, 800):
                self.bullets.remove(b)

    def check_bullet_collision(self, bullet_rect):
        if not self.alive:
            return False
        return pygame.Rect(self.x, self.y, self.size, self.size).colliderect(bullet_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen, camera):
        if not self.alive:
            return
        sx, sy = camera.apply(self.x, self.y)
        sz = self.size * camera.zoom

        color = self.hit_color if self.hit_timer > 0 else self.color
        pygame.draw.rect(screen, color, (sx, sy, sz, sz))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, sz, sz), 2)

        pct = self.health / self.max_health
        pygame.draw.rect(screen, (100, 0, 0), (sx, sy - 10 * camera.zoom, sz, 5))
        pygame.draw.rect(screen, (0, 255, 0), (sx, sy - 10 * camera.zoom, sz * pct, 5))

        for b in self.bullets:
            b.draw(screen, camera)


class EnemyManager:
    def __init__(self):
        self.enemies = []

    def add_enemy(self, x, y, enemy_type="static"):
        self.enemies.append(Enemy(x, y, enemy_type))

    def update(self, px, py, player_bullets, world_width, ground_y):
        for e in self.enemies[:]:
            e.update(px, py, world_width, ground_y)
            if not e.alive:
                self.enemies.remove(e)

        for e in self.enemies:
            for b in player_bullets[:]:
                if e.check_bullet_collision(b.get_rect()):
                    e.take_damage()
                    player_bullets.remove(b)
                    break

    def check_player_hit(self, player_rect):
        for e in self.enemies:
            for b in e.bullets[:]:
                if b.get_rect().colliderect(player_rect):
                    e.bullets.remove(b)
                    return True
        return False

    def draw(self, screen, camera):
        for e in self.enemies:
            e.draw(screen, camera)

    def reset(self):
        self.enemies.clear()
