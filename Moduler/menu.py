import pygame

BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 170, 220)
TEXT_COLOR = (255, 255, 255)

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, font):
        color = HOVER_COLOR if self.rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont(None, 36)

        self.buttons = [
            Button("Play",  screen_width // 2 - 100, 200, 200, 50),
            Button("Quit",  screen_width // 2 - 100, 270, 200, 50),
        ]

        self.title_image = None
        try:
            self.title_image = pygame.image.load("Bilder/grafyx.png").convert_alpha()
        except:
            pass

        self.music_playing = False
        try:
            pygame.mixer.music.load("LydEffekter/MenuLyd.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
            self.music_playing = True
        except:
            pass

    def update_resolution(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons[0].rect = pygame.Rect(screen_width // 2 - 100, 200, 200, 50)
        self.buttons[1].rect = pygame.Rect(screen_width // 2 - 100, 270, 200, 50)

    def handle_event(self, event):
        for button in self.buttons:
            if button.clicked(event):
                if button.text == "Play":
                    if self.music_playing:
                        pygame.mixer.music.stop()
                        self.music_playing = False
                    return "play"
                if button.text == "Quit":
                    return "quit"
        return None

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BG_COLOR)

        if self.title_image:
            img = pygame.transform.scale(self.title_image, (300, 100))
            screen.blit(img, (self.screen_width // 2 - 150, 80))
        else:
            title = self.font.render("Gravity Square", True, (255, 255, 255))
            screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 120))

        for button in self.buttons:
            button.draw(screen, self.font)

    def reset_animations(self):
        if not self.music_playing:
            try:
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                self.music_playing = True
            except:
                pass
