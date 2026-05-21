import pygame
import math


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
        self.speed = 2
        self.direction = 1
        self.patrol_left = x - 150
        self.patrol_right = x + 150

    def take_damage(self):
        self.health -= 1
        self.hit_timer = 10
        if self.health <= 0:
            self.alive = False

    def update(self, world_width):
        if not self.alive:
            return
        if self.hit_timer > 0:
            self.hit_timer -= 1
        if self.type == "moving":
            self.x += self.speed * self.direction
            if self.x <= self.patrol_left or self.x >= self.patrol_right:
                self.direction *= -1

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


class EnemyManager:
    def __init__(self):
        self.enemies = []

    def add_enemy(self, x, y, enemy_type="static"):
        self.enemies.append(Enemy(x, y, enemy_type))

    def update(self, player_bullets, world_width):
        for e in self.enemies[:]:
            e.update(world_width)
            if not e.alive:
                self.enemies.remove(e)
        for e in self.enemies:
            for b in player_bullets[:]:
                if e.get_rect().colliderect(b.get_rect()):
                    e.take_damage()
                    player_bullets.remove(b)
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
        self.enemies.clear()


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.alive = True
        self.speed = 2
        self.direction = 1
        self.y_velocity = 0
        self.gravity = 0.6

    def update(self, platforms, world_width):
        if not self.alive:
            return
        self.x += self.speed * self.direction
        self.y_velocity += self.gravity
        self.y += self.y_velocity
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
            if min_o == overlap_top and self.y_velocity >= 0:
                self.y = rect.top - self.size
                self.y_velocity = 0
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
        sz = self.size * camera.zoom
        pygame.draw.rect(screen, (139, 90, 43), (sx, sy, sz, sz))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, sz, sz), 2)


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
        self.goombas.clear()
