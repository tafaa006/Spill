import pygame
import sys
from Moduler.player import Player
from Moduler.camera import Camera
from Moduler.world import World
from Moduler.menu import Menu
from Moduler.shooting import Gun
from Moduler.pickups import PickupManager
from Moduler.enemies import EnemyManager

pygame.init()

WIDTH, HEIGHT = 800, 600 
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

def get_scaled_font(base_size):
    """Get font scaled to current screen size"""
    scale = min(WIDTH / 600, HEIGHT / 400)
    return pygame.font.SysFont(None, int(base_size * scale))

COOLDOWN_COLOR = (100, 100, 100)
READY_COLOR = (0, 255, 0)
WHITE = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)

game_state = "menu"

menu = Menu(WIDTH, HEIGHT)
world = World(2000, 800, HEIGHT - 50)
camera = Camera(WIDTH, HEIGHT)
player = Player(WIDTH // 2 - 20, HEIGHT - 90)
gun = Gun()
pickup_manager = PickupManager()
enemy_manager = EnemyManager()

player_health = 100
player_max_health = 100

def setup_level():
    """Setup pickups and enemies for the level"""
    pickup_manager.reset()
    enemy_manager.reset()
    
    pickup_manager.add_pickup(200, world.ground_y - 50, "gun")
    pickup_manager.add_pickup(400, world.ground_y - 50, "ammo")
    pickup_manager.add_pickup(600, world.ground_y - 50, "health")
    #pickup_manager.add_pickup(800, world.ground_y - 50, "ammo")#
    #pickup_manager.add_pickup(1000, world.ground_y - 50, "ammo")#
    #pickup_manager.add_pickup(1200, world.ground_y - 50, "health")#
    
    enemy_manager.add_enemy(500, world.ground_y - 40, "static")
    enemy_manager.add_enemy(900, world.ground_y - 40, "moving")
    enemy_manager.add_enemy(1300, world.ground_y - 40, "static")
    enemy_manager.add_enemy(1600, world.ground_y - 40, "moving")

def draw_ui(screen, player, gun):
    """Draw UI elements with scaling"""
    small_font = get_scaled_font(24)
    
    ui_scale = min(WIDTH / 600, HEIGHT / 400)


    health_bar_width = int(200 * ui_scale)
    health_bar_height = int(20 * ui_scale)
    health_x = WIDTH // 2 - health_bar_width // 2
    health_y = int(10 * ui_scale)
    
    health_percentage = player_health / player_max_health
    
    pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, health_bar_width * health_percentage, health_bar_height))
    pygame.draw.rect(screen, WHITE, (health_x, health_y, health_bar_width, health_bar_height), 2)
    
    health_text = small_font.render(f"HP: {player_health}/{player_max_health}", True, WHITE)
    text_rect = health_text.get_rect(center=(health_x + health_bar_width // 2, health_y + health_bar_height // 2))
    screen.blit(health_text, text_rect)
    
    right_x = WIDTH - int(100 * ui_scale)

    if gun.has_gun:
        gun_text = small_font.render("GUN: YES", True, (255, 100, 100))
        screen.blit(gun_text, (right_x, int(90 * ui_scale)))
        
        shoot_dir_text = small_font.render(f"AIM: {player.get_shoot_direction().upper()}", True, (200, 200, 200))
        screen.blit(shoot_dir_text, (right_x, int(110 * ui_scale)))
        
        if gun.unlimited_ammo:
            ammo_text = small_font.render("AMMO: ∞", True, WHITE)
        else:
            ammo_color = WHITE if gun.ammo > 5 else (255, 0, 0)
            ammo_text = small_font.render(f"AMMO: {gun.ammo}", True, ammo_color)
        screen.blit(ammo_text, (right_x, int(130 * ui_scale)))
    
    zoom_text = small_font.render(f"ZOOM: {camera.zoom:.1f}x", True, WHITE)
    screen.blit(zoom_text, (int(10 * ui_scale), HEIGHT - int(30 * ui_scale)))

running = True
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            menu.update_resolution(WIDTH, HEIGHT)
            camera.screen_width = WIDTH
            camera.screen_height = HEIGHT
        
        if game_state == "menu":
            action = menu.handle_event(event)
            if action == "quit":
                running = False
            elif action == "play":
                game_state = "game"
                player.reset(WIDTH // 2 - 20, HEIGHT - 90)
                camera.reset()
                gun.reset()
                player_health = player_max_health
                setup_level()
            elif action == "options":
                print("Options not implemented yet")
        
        elif game_state == "game":
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.zoom_in()
                elif event.y < 0:
                    camera.zoom_out()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shoot_direction = player.get_shoot_direction()
                gun.shoot(player.x, player.y, player.size, shoot_direction)
            
            player.handle_input(event)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "menu"
                menu.reset_animations()
    
    if game_state == "menu":
        menu.update()
        menu.draw(screen)
    
    elif game_state == "game":
        player.update(world.width)
        player.check_ground_collision(world.ground_y)
        camera.update(player.x + player.size // 2, player.y + player.size // 2)
        gun.update(world.width, world.height, world.ground_y)
        pickup_manager.update(player.x, player.y, player.size, gun)
        enemy_manager.update(player.x, player.y, gun.bullets, world.width, world.ground_y)
        
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        if enemy_manager.check_player_hit(player_rect):
            player_health -= 10
            print(f"Hit! Health: {player_health}")
            
            if player_health <= 0:
                print("Game Over!")
                game_state = "menu"
                menu.reset_animations()
        
        world.draw(screen, camera)
        pickup_manager.draw(screen, camera)
        enemy_manager.draw(screen, camera)
        player.draw(screen, camera)
        gun.draw(screen, camera)
        draw_ui(screen, player, gun)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()