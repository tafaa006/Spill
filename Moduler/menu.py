import pygame
import math
import random

class Button:
    def __init__(self, text, x_percent, y_percent, w_percent, h_percent, screen_width, screen_height):
        self.text = text
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.w_percent = w_percent
        self.h_percent = h_percent
        
        x = int(screen_width * x_percent)
        y = int(screen_height * y_percent)
        w = int(screen_width * w_percent)
        h = int(screen_height * h_percent)
        
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, y - 50, w, h)  
        self.button_color = (70, 130, 180)
        self.hover_color = (100, 170, 220)
        self.text_color = (255, 255, 255)
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        self.alpha = 0 
    
    def update_resolution(self, screen_width, screen_height):
        x = int(screen_width * self.x_percent)
        y = int(screen_height * self.y_percent)
        w = int(screen_width * self.w_percent)
        h = int(screen_height * self.h_percent)
        
        self.target_rect = pygame.Rect(x, y, w, h)
        if self.alpha >= 255: 
            self.rect = pygame.Rect(x, y, w, h)
    
    def update(self):
        self.rect.y += (self.target_rect.y - self.rect.y) * 0.1
        self.rect.x += (self.target_rect.x - self.rect.x) * 0.1
        self.rect.width += (self.target_rect.width - self.rect.width) * 0.1
        self.rect.height += (self.target_rect.height - self.rect.height) * 0.1
        
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 5)
        
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.target_hover_scale = 1.1
        else:
            self.target_hover_scale = 1.0
        
        self.hover_scale += (self.target_hover_scale - self.hover_scale) * 0.2
    
    def draw(self, surface, font_size):
        scaled_w = self.rect.width * self.hover_scale
        scaled_h = self.rect.height * self.hover_scale
        scaled_x = self.rect.centerx - scaled_w / 2
        scaled_y = self.rect.centery - scaled_h / 2
        
        button_surface = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
        
        is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.hover_color if is_hovered else self.button_color
        
        pygame.draw.rect(button_surface, (*color, self.alpha), (0, 0, scaled_w, scaled_h))
        pygame.draw.rect(button_surface, (0, 0, 0, self.alpha), (0, 0, scaled_w, scaled_h), 2)
     
        font = pygame.font.SysFont(None, font_size)
        text_surf = font.render(self.text, True, (*self.text_color, self.alpha))
        text_rect = text_surf.get_rect(center=(scaled_w / 2, scaled_h / 2))
        button_surface.blit(text_surf, text_rect)
        
        surface.blit(button_surface, (scaled_x, scaled_y))
    
    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
    
    def reset_animation(self):
        self.rect.y = self.target_rect.y - 50
        self.alpha = 0

class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.buttons = [
            Button("Play", 0.25, 0.5, 0.5, 0.125, screen_width, screen_height),
            Button("Options", 0.29, 0.675, 0.42, 0.125, screen_width, screen_height),
            Button("Quit", 0.33, 0.85, 0.34, 0.125, screen_width, screen_height)
        ]

        for i, button in enumerate(self.buttons):
            button.rect.y -= i * 20

        self.bg_color = (30, 30, 30)

        self.title_image = None
        try:
            self.title_image = pygame.image.load("Bilder/grafyx.png").convert_alpha()
        except:
            pass

        self.title_y = -100
        self.title_alpha = 0

        self.beat_bounce = 0
        self.target_beat_bounce = 0
        self.beat_scale = 1.0
        self.target_beat_scale = 1.0

        self.particles = []
        self.particle_timer = 0

        self.wave_offset = 0

        self.music_loaded = False
        self.music_playing = False
        self.beat_timer = 0
        self.beat_interval = 30

        try:
            pygame.mixer.music.load('LydEffekter/MenuLyd.mp3')
            self.music_loaded = True
        except:
            try:
                pygame.mixer.music.load('LydEffekter/MenuLyd.wav')
                self.music_loaded = True
            except:
                try:
                    pygame.mixer.music.load('LydEffekter/MenuLyd.ogg')
                    self.music_loaded = True
                except:
                    self.music_loaded = False

    def update_resolution(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        for button in self.buttons:
            button.update_resolution(screen_width, screen_height)

    def get_scaled_font_size(self, base_size):
        scale_factor = min(self.screen_width / 600, self.screen_height / 400)
        return int(base_size * scale_factor)

    def start_music(self):
        if self.music_loaded and not self.music_playing:
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
            self.music_playing = True

    def stop_music(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def trigger_beat(self):
        self.target_beat_bounce = 20 * (self.screen_height / 400)
        self.target_beat_scale = 1.15

    def update(self):
        if not self.music_playing:
            self.start_music()

        target_y = self.screen_height * 0.25
        self.title_y += (target_y - self.title_y) * 0.08

        if self.title_alpha < 255:
            self.title_alpha = min(255, self.title_alpha + 3)

        self.beat_timer += 1
        if self.beat_timer >= self.beat_interval:
            self.trigger_beat()
            self.beat_timer = 0

        self.beat_bounce += (self.target_beat_bounce - self.beat_bounce) * 0.3
        self.target_beat_bounce *= 0.8

        self.beat_scale += (self.target_beat_scale - self.beat_scale) * 0.2
        self.target_beat_scale += (1.0 - self.target_beat_scale) * 0.1

        for button in self.buttons:
            button.update()

        self.wave_offset += 0.05

        self.particle_timer += 1
        if self.particle_timer > 10:
            self.particle_timer = 0
            self.particles.append({
                'x': random.randint(0, self.screen_width),
                'y': self.screen_height,
                'speed': 1 + random.random() * 2,
                'size': 2 + random.randint(0, 2)
            })

        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                self.particles.remove(particle)

    def draw_background_waves(self, surface):
        for i in range(5):
            points = []
            for x in range(0, self.screen_width + 20, 20):
                y = self.screen_height - 100 + math.sin((x + self.wave_offset * 50 + i * 30) * 0.02) * 20 + i * 30
                points.append((x, y))

            points.append((self.screen_width, self.screen_height))
            points.append((0, self.screen_height))

            wave_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            color_intensity = 40 - i * 5
            pygame.draw.polygon(wave_surface, (color_intensity, color_intensity, color_intensity, 50), points)
            surface.blit(wave_surface, (0, 0))

    def draw_particles(self, surface):
        for particle in self.particles:
            alpha = max(0, min(255, int(255 * (particle['y'] / self.screen_height))))
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                (100, 150, 200, alpha),
                (particle['size'], particle['size']),
                particle['size']
            )
            surface.blit(particle_surface, (int(particle['x']), int(particle['y'])))

    def handle_event(self, event):
        for button in self.buttons:
            if button.clicked(event):
                if button.text == "Quit":
                    return "quit"
                elif button.text == "Options":
                    return "options"
                elif button.text == "Play":
                    self.stop_music()
                    return "play"
        return None

    def draw(self, surface):
        surface.fill(self.bg_color)
        self.draw_background_waves(surface)
        self.draw_particles(surface)

        if self.title_image:
            title_y_with_bounce = self.title_y - self.beat_bounce
            scale = self.beat_scale
            img_width = int(self.title_image.get_width() * scale)
            img_height = int(self.title_image.get_height() * scale)

            max_width = int(self.screen_width * 0.6)
            if img_width > max_width:
                scale = max_width / self.title_image.get_width()
                img_width = int(self.title_image.get_width() * scale)
                img_height = int(self.title_image.get_height() * scale)

            scaled_img = pygame.transform.smoothscale(self.title_image, (img_width, img_height))
            scaled_img.set_alpha(self.title_alpha)
            surface.blit(scaled_img, (self.screen_width // 2 - img_width // 2, int(title_y_with_bounce - img_height // 2)))

        button_font_size = self.get_scaled_font_size(36)
        for button in self.buttons:
            button.draw(surface, button_font_size)

    def reset_animations(self):
        self.title_y = -100
        self.title_alpha = 0
        self.particles.clear()
        self.beat_bounce = 0
        self.target_beat_bounce = 0
        self.beat_scale = 1.0
        self.target_beat_scale = 1.0
        self.beat_timer = 0

        for i, button in enumerate(self.buttons):
            button.reset_animation()
            button.rect.y -= i * 20

        self.start_music()
