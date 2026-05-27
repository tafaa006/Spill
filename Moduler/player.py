import pygame

square_size = 40
speed = 5

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = square_size
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jumps_remaining = 2
        self.dash_cooldown = 0
        self.is_dashing = False
        self.dash_timer = 0
        self.last_direction = "right"

    def get_shoot_direction(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            return "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return "down"
        return self.last_direction

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.last_direction = "left"
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.last_direction = "right"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.last_direction = "up"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.last_direction = "down"

            if event.key in (pygame.K_UP, pygame.K_w) and self.jumps_remaining > 0:
                self.vel_y = -12
                self.jumps_remaining -= 1

            if event.key == pygame.K_q and self.dash_cooldown == 0:
                self.is_dashing = True
                self.dash_timer = 10
                self.dash_cooldown = 60
                if self.last_direction == "left":
                    self.vel_x = -15
                elif self.last_direction == "right":
                    self.vel_x = 15
                elif self.last_direction == "up":
                    self.vel_y = -15
                elif self.last_direction == "down":
                    self.vel_y = 15

    def update(self, world_width):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            self.is_dashing = False

        if not self.is_dashing:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -speed
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = speed
            else:
                self.vel_x = 0

        self.x += self.vel_x
        self.x = max(0, min(world_width - self.size, self.x))

        self.vel_y += 0.6
        self.y += self.vel_y
        if self.y < 0:
            self.y = 0
            self.vel_y = 0

    def check_platform_collision(self, platforms):
        self.on_ground = False
        killed = False
        for rect, tile_type in platforms:
            player_rect = pygame.Rect(self.x, self.y, self.size, self.size)
            if not player_rect.colliderect(rect):
                continue
            if tile_type == "2":
                killed = True
                continue
            overlap_left = (self.x + self.size) - rect.left
            overlap_right = rect.right - self.x
            overlap_top = (self.y + self.size) - rect.top
            overlap_bottom = rect.bottom - self.y
            min_o = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_o == overlap_top and self.vel_y >= 0:
                self.y = rect.top - self.size
                self.vel_y = 0
                self.on_ground = True
                self.jumps_remaining = 2
            elif min_o == overlap_bottom and self.vel_y < 0:
                self.y = rect.bottom
                self.vel_y = 0
            elif min_o == overlap_left:
                self.x = rect.left - self.size
            elif min_o == overlap_right:
                self.x = rect.right
        return killed

    def draw(self, screen, camera):
        sx, sy = camera.apply(self.x, self.y)
        color = (255, 0, 255) if self.is_dashing else (0, 200, 255)
        pygame.draw.rect(screen, color, (sx, sy, self.size, self.size))

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jumps_remaining = 2
        self.dash_cooldown = 0
        self.is_dashing = False
        self.dash_timer = 0
        self.last_direction = "right"
