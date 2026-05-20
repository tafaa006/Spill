import pygame

class Player:
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False

        self.gravity = 0.6
        self.jump_strength = -12
        self.jumps_remaining = 2
        self.max_jumps = 2

        self.walk_speed = 5
        self.run_max_speed = 8
        self.acceleration = 0.8
        self.friction = 0.85
        self.is_running = False

        self.last_tap_time_left = 0
        self.last_tap_time_right = 0
        self.double_tap_window = 15

        self.dash_speed = 15
        self.dash_cooldown = 0
        self.dash_cooldown_time = 60
        self.can_dash_in_air = True
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 10

        self.last_direction = "right"

        self.color_normal = (0, 150, 255)
        self.color_running = (255, 150, 0)
        self.color_dashing = (255, 0, 255)

    def get_shoot_direction(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            return "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return "down"
        return self.last_direction

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            t = pygame.time.get_ticks() / (1000 / 60)

            if event.key in (pygame.K_LEFT, pygame.K_a):
                if t - self.last_tap_time_left < self.double_tap_window:
                    self.is_running = True
                self.last_tap_time_left = t
                self.last_direction = "left"
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if t - self.last_tap_time_right < self.double_tap_window:
                    self.is_running = True
                self.last_tap_time_right = t
                self.last_direction = "right"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.last_direction = "up"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.last_direction = "down"

            if event.key in (pygame.K_UP, pygame.K_w) and self.jumps_remaining > 0:
                self.y_velocity = self.jump_strength
                self.jumps_remaining -= 1
                self.on_ground = False

            if event.key == pygame.K_q and self.dash_cooldown == 0 and (self.on_ground or self.can_dash_in_air):
                self.dash()

    def dash(self):
        self.is_dashing = True
        self.dash_timer = self.dash_duration
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            d = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            d = "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            d = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            d = "down"
        else:
            d = self.last_direction

        if d == "left":
            self.x_velocity, self.y_velocity = -self.dash_speed, 0
        elif d == "right":
            self.x_velocity, self.y_velocity = self.dash_speed, 0
        elif d == "up":
            self.x_velocity, self.y_velocity = 0, -self.dash_speed
        elif d == "down":
            self.x_velocity, self.y_velocity = 0, self.dash_speed

        self.dash_cooldown = self.dash_cooldown_time
        if not self.on_ground:
            self.can_dash_in_air = False

    def update(self, world_width):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            self.is_dashing = False

        if not self.is_dashing:
            keys = pygame.key.get_pressed()
            moving = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]

            if self.is_running:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.x_velocity -= self.acceleration
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.x_velocity += self.acceleration
                else:
                    self.x_velocity *= self.friction
                    if abs(self.x_velocity) < 0.1:
                        self.x_velocity = 0
                self.x_velocity = max(-self.run_max_speed, min(self.run_max_speed, self.x_velocity))
                if not moving and abs(self.x_velocity) < 0.1:
                    self.is_running = False
            else:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.x_velocity = -self.walk_speed
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.x_velocity = self.walk_speed
                else:
                    self.x_velocity = 0

        self.x += self.x_velocity
        self.x = max(0, min(world_width - self.size, self.x))
        if self.x == 0 or self.x == world_width - self.size:
            self.x_velocity = 0

        if not (self.is_dashing and self.last_direction in ("left", "right")):
            self.y_velocity += self.gravity
        self.y += self.y_velocity
        if self.y < 0:
            self.y = 0
            self.y_velocity = 0

    def check_platform_collision(self, platforms):
        self.on_ground = False
        for rect, tile_type in platforms:
            player_rect = pygame.Rect(self.x, self.y, self.size, self.size)
            if not player_rect.colliderect(rect):
                continue
            overlap_left = (self.x + self.size) - rect.left
            overlap_right = rect.right - self.x
            overlap_top = (self.y + self.size) - rect.top
            overlap_bottom = rect.bottom - self.y
            min_o = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_o == overlap_top and self.y_velocity >= 0:
                self.y = rect.top - self.size
                self.y_velocity = 0
                self.on_ground = True
                self.jumps_remaining = self.max_jumps
                self.can_dash_in_air = True
            elif min_o == overlap_bottom and self.y_velocity < 0:
                self.y = rect.bottom
                self.y_velocity = 0
            elif min_o == overlap_left and self.x_velocity > 0:
                self.x = rect.left - self.size
                self.x_velocity = 0
            elif min_o == overlap_right and self.x_velocity < 0:
                self.x = rect.right
                self.x_velocity = 0

    def draw(self, screen, camera):
        sx, sy = camera.apply(self.x, self.y)
        size = self.size * camera.zoom
        if self.is_dashing:
            color = self.color_dashing
        elif self.is_running:
            color = self.color_running
        else:
            color = self.color_normal
        pygame.draw.rect(screen, color, (sx, sy, size, size))

    def reset(self, x, y):
        self.x, self.y = x, y
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False
        self.jumps_remaining = self.max_jumps
        self.dash_cooldown = 0
        self.can_dash_in_air = True
        self.last_direction = "right"
        self.is_running = False
        self.is_dashing = False
        self.dash_timer = 0
        self.last_tap_time_left = 0
        self.last_tap_time_right = 0
