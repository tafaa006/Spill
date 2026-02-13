import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

# Colors
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)
BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 170, 220)
TEXT_COLOR = (255, 255, 255)
COOLDOWN_COLOR = (100, 100, 100)
READY_COLOR = (0, 255, 0)

# Font
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Button class
class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
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

# Camera class
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smooth_speed = 0.1
        self.zoom_speed = 0.05
        
    def update(self, target_x, target_y):
        # Smooth zoom
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
        
        # Calculate camera position to center on player with zoom
        # The camera position keeps the player centered at the current zoom level
        target_cam_x = target_x - (WIDTH / 2) / self.zoom
        target_cam_y = target_y - (HEIGHT / 2) / self.zoom
        
        # Smooth camera follow
        self.x += (target_cam_x - self.x) * self.smooth_speed
        self.y += (target_cam_y - self.y) * self.smooth_speed
    
    def apply(self, entity_x, entity_y):
        # Apply camera offset and zoom
        screen_x = (entity_x - self.x) * self.zoom
        screen_y = (entity_y - self.y) * self.zoom
        return screen_x, screen_y
    
    def apply_rect(self, rect):
        # Apply camera to a rectangle
        new_rect = rect.copy()
        new_rect.x = (rect.x - self.x) * self.zoom
        new_rect.y = (rect.y - self.y) * self.zoom
        new_rect.width = rect.width * self.zoom
        new_rect.height = rect.height * self.zoom
        return new_rect
    
    def zoom_in(self):
        self.target_zoom = min(1.5, self.target_zoom + 0.1)
    
    def zoom_out(self):
        self.target_zoom = max(0.75, self.target_zoom - 0.1)

# Create buttons
buttons = [
    Button("Play", 150, 120, 300, 50),
    Button("Options", 175, 190, 250, 50),
    Button("Quit", 200, 260, 200, 50)
]

# Game state
game_state = "menu"  # can be "menu" or "game"

# Camera
camera = Camera()

# Square (player)
size = 40
x = WIDTH // 2 - size // 2
y = HEIGHT - size - 50

x_velocity = 0
y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False

# Double jump
jumps_remaining = 2
max_jumps = 2

# Movement settings
walk_speed = 5  # Normal walking speed
run_max_speed = 8  # Running max speed
acceleration = 0.8
friction = 0.85
is_running = False

# Double tap detection
last_tap_time_left = 0
last_tap_time_right = 0
double_tap_window = 15  # frames (0.25 seconds at 60 FPS)

# Dash settings
dash_speed = 15
dash_cooldown = 0
dash_cooldown_time = 60
can_dash_in_air = True
is_dashing = False
dash_timer = 0
dash_duration = 10  # frames the dash lasts

# Track last direction pressed
last_direction = "right"  # default direction

# Ground
ground_y = HEIGHT - 50

# World boundaries (for extended world)
world_width = 2000
world_height = 800

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Menu state events
        if game_state == "menu":
            for button in buttons:
                if button.clicked(event):
                    print(f"{button.text} clicked!")

                    if button.text == "Quit":
                        pygame.quit()
                        sys.exit()
                    elif button.text == "Options":
                        # Add your options menu here
                        print("Options menu not implemented yet")
                    elif button.text == "Play":
                        game_state = "game"  # Switch to game state
                        # Reset player position
                        x = WIDTH // 2 - size // 2
                        y = HEIGHT - size - 50
                        x_velocity = 0
                        y_velocity = 0
                        on_ground = False
                        jumps_remaining = max_jumps
                        dash_cooldown = 0
                        can_dash_in_air = True
                        last_direction = "right"
                        is_running = False
                        is_dashing = False
                        dash_timer = 0
                        last_tap_time_left = 0
                        last_tap_time_right = 0
                        camera.x = 0
                        camera.y = 0
                        camera.zoom = 1.0
                        camera.target_zoom = 1.0

        # Game state events
        elif game_state == "game":
            # Mouse wheel zoom
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    camera.zoom_in()
                elif event.y < 0:  # Scroll down
                    camera.zoom_out()
            
            if event.type == pygame.KEYDOWN:
                # Double tap detection for running
                current_time = pygame.time.get_ticks() / (1000 / 60)  # Convert to frames
                
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if current_time - last_tap_time_left < double_tap_window:
                        is_running = True
                    last_tap_time_left = current_time
                    last_direction = "left"
                    
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if current_time - last_tap_time_right < double_tap_window:
                        is_running = True
                    last_tap_time_right = current_time
                    last_direction = "right"
                    
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    last_direction = "up"
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    last_direction = "down"
                
                # Jump with double jump
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and jumps_remaining > 0:
                    y_velocity = jump_strength
                    jumps_remaining -= 1
                    on_ground = False
                
                # Dash with Q - uses last direction pressed and resets momentum
                if event.key == pygame.K_q and dash_cooldown == 0 and (on_ground or can_dash_in_air):
                    is_dashing = True
                    dash_timer = dash_duration
                    
                    # Apply dash based on last direction
                    if last_direction == "left":
                        x_velocity = -dash_speed
                        y_velocity = 0
                    elif last_direction == "right":
                        x_velocity = dash_speed
                        y_velocity = 0
                    elif last_direction == "up":
                        x_velocity = 0
                        y_velocity = -dash_speed
                    elif last_direction == "down":
                        x_velocity = 0
                        y_velocity = dash_speed
                    
                    dash_cooldown = dash_cooldown_time
                    
                    # If dashing in air, disable air dash until landing
                    if not on_ground:
                        can_dash_in_air = False

    # Update and draw based on state
    if game_state == "menu":
        # Draw menu
        screen.fill(BG_COLOR)
        for button in buttons:
            button.draw(screen)

    elif game_state == "game":
        # Decrease dash cooldown
        if dash_cooldown > 0:
            dash_cooldown -= 1
        
        # Decrease dash timer
        if dash_timer > 0:
            dash_timer -= 1
        else:
            is_dashing = False
        
        # Only allow normal movement when not dashing
        if not is_dashing:
            # Key presses - different behavior for walking vs running
            keys = pygame.key.get_pressed()
            
            # Check if any movement key is pressed
            is_moving = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]
            
            if is_running:
                # Running mode - use acceleration and friction
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    x_velocity -= acceleration
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    x_velocity += acceleration
                else:
                    # Apply friction when no keys pressed
                    x_velocity *= friction
                    # Stop completely if very slow
                    if abs(x_velocity) < 0.1:
                        x_velocity = 0
                
                # Cap max speed for running
                if x_velocity > run_max_speed:
                    x_velocity = run_max_speed
                elif x_velocity < -run_max_speed:
                    x_velocity = -run_max_speed
                
                # Stop running only when player stops moving completely
                if not is_moving and abs(x_velocity) < 0.1:
                    is_running = False
                    
            else:
                # Walking mode - instant speed, no acceleration
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    x_velocity = -walk_speed
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    x_velocity = walk_speed
                else:
                    x_velocity = 0
        
        # Apply horizontal velocity
        x += x_velocity
        
        # Keep player on screen (expanded world)
        if x < 0:
            x = 0
            x_velocity = 0
        elif x > world_width - size:
            x = world_width - size
            x_velocity = 0
        
        # Return to menu with ESC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            game_state = "menu"

        # Apply gravity (but not during horizontal dash)
        if not (is_dashing and last_direction in ["left", "right"]):
            y_velocity += gravity
        
        y += y_velocity

        # Collision with ground
        if y + size >= ground_y:
            y = ground_y - size
            y_velocity = 0
            on_ground = True
            jumps_remaining = max_jumps  # Reset jumps when landing
            can_dash_in_air = True  # Reset air dash when landing
        
        # Keep player from going above screen
        if y < 0:
            y = 0
            y_velocity = 0

        # Update camera to follow player (pass player center)
        camera.update(x + size // 2, y + size // 2)

        # Draw game
        screen.fill(DARK)

        # Draw ground with camera
        ground_rect = pygame.Rect(0, ground_y, world_width, HEIGHT - ground_y)
        screen_ground_rect = camera.apply_rect(ground_rect)
        pygame.draw.rect(screen, WHITE, screen_ground_rect)

        # Draw player with camera
        player_screen_x, player_screen_y = camera.apply(x, y)
        player_size_scaled = size * camera.zoom
        
        # Square - change color when running or dashing
        if is_dashing:
            player_color = (255, 0, 255)  # Magenta when dashing
        elif is_running:
            player_color = (255, 150, 0)  # Orange when running
        else:
            player_color = BLUE  # Blue normally
        pygame.draw.rect(screen, player_color, (player_screen_x, player_screen_y, player_size_scaled, player_size_scaled))
        
        # UI elements (not affected by camera)
        # Dash cooldown indicator
        cooldown_bar_width = 100
        cooldown_bar_height = 10
        cooldown_x = 10
        cooldown_y = 10
        
        # Background bar
        pygame.draw.rect(screen, COOLDOWN_COLOR, (cooldown_x, cooldown_y, cooldown_bar_width, cooldown_bar_height))
        
        # Filled portion based on cooldown
        if dash_cooldown == 0 and (on_ground or can_dash_in_air):
            fill_width = cooldown_bar_width
            fill_color = READY_COLOR
        else:
            fill_width = cooldown_bar_width * (1 - dash_cooldown / dash_cooldown_time)
            fill_color = BUTTON_COLOR
        
        pygame.draw.rect(screen, fill_color, (cooldown_x, cooldown_y, fill_width, cooldown_bar_height))
        pygame.draw.rect(screen, WHITE, (cooldown_x, cooldown_y, cooldown_bar_width, cooldown_bar_height), 2)
        
        # Dash status text with direction
        if dash_cooldown == 0 and (on_ground or can_dash_in_air):
            status_text = small_font.render(f"DASH READY (Q) - {last_direction.upper()}", True, READY_COLOR)
        elif not on_ground and not can_dash_in_air:
            status_text = small_font.render("LAND TO DASH", True, COOLDOWN_COLOR)
        else:
            status_text = small_font.render("DASH COOLDOWN", True, COOLDOWN_COLOR)
        screen.blit(status_text, (cooldown_x, cooldown_y + 15))
        
        # Running indicator
        if is_running:
            run_text = small_font.render("RUNNING", True, (255, 150, 0))
            screen.blit(run_text, (WIDTH - 100, 10))
        
        # Dashing indicator
        if is_dashing:
            dash_text = small_font.render("DASHING!", True, (255, 0, 255))
            screen.blit(dash_text, (WIDTH - 100, 35))
        
        # Zoom indicator
        zoom_text = small_font.render(f"ZOOM: {camera.zoom:.1f}x", True, WHITE)
        screen.blit(zoom_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)