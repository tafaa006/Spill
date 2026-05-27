import pygame
import math


class Enemy:
    def __init__(self, x, y, enemy_type="static"):
        self.x = x
        self.y = y
        self.size = 40
        self.type = enemy_type
        self.health = 3
        self.alive = True
        self.hit_timer = 0
        self.speed = 2
        self.direction = 1
        self.patrol_left = x - 150
        self.patrol_right = x + 150

    def take_damage(self):
        self.health -= 1
        self.hit_timer = 10
        if self.health <= 0:
            self.alive = False

    def update(self, px, py, world_width):
        if not self.alive:
            return
        if self.hit_timer > 0:
            self.hit_timer -= 1

        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        if dist < 400:
            if px < self.x:
                self.x -= self.speed
            elif px > self.x:
                self.x += self.speed
        elif self.type == "moving":
            self.x += self.speed * self.direction
            if self.x <= self.patrol_left or self.x >= self.patrol_right:
                self.direction *= -1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen, camera):
        if not self.alive:
            return
        sx, sy = camera.apply(self.x, self.y)
        color = (255, 200, 200) if self.hit_timer > 0 else (255, 0, 0)
        pygame.draw.rect(screen, color, (sx, sy, self.size, self.size))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, self.size, self.size), 2)
        bar_w = int(self.size * (self.health / 3))
        pygame.draw.rect(screen, (100, 0, 0), (sx, sy - 10, self.size, 5))
        pygame.draw.rect(screen, (0, 255, 0), (sx, sy - 10, bar_w, 5))


class EnemyManager:
    def __init__(self):
        self.enemies = []

    def add_enemy(self, x, y, enemy_type="static"):
        self.enemies.append(Enemy(x, y, enemy_type))

    def update(self, px, py, bullets, world_width):
        for e in self.enemies[:]:
            e.update(px, py, world_width)
            if not e.alive:
                self.enemies.remove(e)

        for e in self.enemies:
            for bullet in bullets[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 4)
                if e.get_rect().colliderect(bullet_rect):
                    e.take_damage()
                    bullets.remove(bullet)
                    break

    def check_player_hit(self, player_rect):
        for e in self.enemies:
            if e.alive and e.get_rect().colliderect(player_rect):
                return True
        return False

    def draw(self, screen, camera):
        for e in self.enemies:
            e.draw(screen, camera)

    def reset(self):
        self.enemies = []


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.alive = True
        self.speed = 2
        self.direction = 1
        self.vel_y = 0

    def update(self, platforms, world_width):
        if not self.alive:
            return

        self.x += self.speed * self.direction
        self.vel_y += 0.6
        self.y += self.vel_y

        if self.x <= 0 or self.x >= world_width - self.size:
            self.direction *= -1

        grect = pygame.Rect(self.x, self.y, self.size, self.size)
        for rect, tile_type in platforms:
            if not grect.colliderect(rect):
                continue
            overlap_left = (self.x + self.size) - rect.left
            overlap_right = rect.right - self.x
            overlap_top = (self.y + self.size) - rect.top
            overlap_bottom = rect.bottom - self.y
            min_o = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_o == overlap_top and self.vel_y >= 0:
                self.y = rect.top - self.size
                self.vel_y = 0
            elif min_o == overlap_left or min_o == overlap_right:
                self.direction *= -1

    def check_player_collision(self, px, py, psize, py_vel):
        if not self.alive:
            return None
        if not pygame.Rect(px, py, psize, psize).colliderect(pygame.Rect(self.x, self.y, self.size, self.size)):
            return None
        if py_vel > 0 and py + psize - py_vel <= self.y + 10:
            self.alive = False
            return "stomp"
        return "hurt"

    def draw(self, screen, camera):
        if not self.alive:
            return
        sx, sy = camera.apply(self.x, self.y)
        pygame.draw.rect(screen, (139, 90, 43), (sx, sy, self.size, self.size))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, self.size, self.size), 2)


class GoombaManager:
    def __init__(self):
        self.goombas = []

    def add_goomba(self, x, y):
        self.goombas.append(Goomba(x, y))

    def update(self, platforms, world_width):
        for g in self.goombas[:]:
            g.update(platforms, world_width)
            if not g.alive:
                self.goombas.remove(g)

    def check_player_collision(self, px, py, psize, py_vel):
        for g in self.goombas:
            result = g.check_player_collision(px, py, psize, py_vel)
            if result:
                return result
        return None

    def draw(self, screen, camera):
        for g in self.goombas:
            g.draw(screen, camera)

    def reset(self):
        self.goombas = []
