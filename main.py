import pygame
import sys
from Moduler.player import Player
from Moduler.camera import Camera
from Moduler.world import World
from Moduler.menu import Menu
from Moduler.shooting import Gun
from Moduler.pickups import PickupManager
from Moduler.enemies import EnemyManager
from Moduler.kart import Map

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

def get_scaled_font(base_size):
    scale = min(WIDTH / 600, HEIGHT / 400)
    return pygame.font.SysFont(None, int(base_size * scale))

WHITE = (255, 255, 255)

game_state = "menu"

game_map = Map()
menu = Menu(WIDTH, HEIGHT)
world = World(game_map)
camera = Camera(WIDTH, HEIGHT)
player = Player(game_map.world_width // 2 - 20, game_map.ground_y - 40)
gun = Gun()
pickup_manager = PickupManager()
enemy_manager = EnemyManager()

player_health = 100
player_max_health = 100

def setup_level():
    pickup_manager.reset()
    enemy_manager.reset()

    pickup_manager.add_pickup(200, world.ground_y - 50, "gun")
    pickup_manager.add_pickup(400, world.ground_y - 50, "ammo")
    pickup_manager.add_pickup(600, world.ground_y - 50, "health")

    enemy_manager.add_enemy(500, world.ground_y - 40, "static")
    enemy_manager.add_enemy(900, world.ground_y - 40, "moving")
    enemy_manager.add_enemy(1300, world.ground_y - 40, "static")
    enemy_manager.add_enemy(1600, world.ground_y - 40, "moving")

def draw_ui(screen, player, gun):
    small_font = get_scaled_font(24)
    ui_scale = min(WIDTH / 600, HEIGHT / 400)

    health_bar_width = int(200 * ui_scale)
    health_bar_height = int(20 * ui_scale)
    health_x = WIDTH // 2 - health_bar_width // 2
    health_y = int(10 * ui_scale)
    health_percentage = player_health / player_max_health

    pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, int(health_bar_width * health_percentage), health_bar_height))
    pygame.draw.rect(screen, WHITE, (health_x, health_y, health_bar_width, health_bar_height), 2)

    health_text = small_font.render(f"HP: {player_health}/{player_max_health}", True, WHITE)
    screen.blit(health_text, health_text.get_rect(center=(health_x + health_bar_width // 2, health_y + health_bar_height // 2)))

    right_x = WIDTH - int(100 * ui_scale)
    if gun.has_gun:
        screen.blit(small_font.render("GUN: YES", True, (255, 100, 100)), (right_x, int(90 * ui_scale)))
        screen.blit(small_font.render(f"AIM: {player.get_shoot_direction().upper()}", True, (200, 200, 200)), (right_x, int(110 * ui_scale)))
        if gun.unlimited_ammo:
            ammo_text = small_font.render("AMMO: ∞", True, WHITE)
        else:
            ammo_color = WHITE if gun.ammo > 5 else (255, 0, 0)
            ammo_text = small_font.render(f"AMMO: {gun.ammo}", True, ammo_color)
        screen.blit(ammo_text, (right_x, int(130 * ui_scale)))

    screen.blit(small_font.render(f"ZOOM: {camera.zoom:.1f}x", True, WHITE), (int(10 * ui_scale), HEIGHT - int(50 * ui_scale)))
    screen.blit(small_font.render("[M] Kart", True, (180, 180, 180)), (int(10 * ui_scale), HEIGHT - int(30 * ui_scale)))

running = True
while running:
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
                player.reset(game_map.world_width // 2 - 20, game_map.ground_y - 40)
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
                gun.shoot(player.x, player.y, player.size, player.get_shoot_direction())

            player.handle_input(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    menu.reset_animations()
                elif event.key == pygame.K_m:
                    game_state = "map"

        elif game_state == "map":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_m, pygame.K_ESCAPE):
                game_state = "game"

    if game_state == "menu":
        menu.update()
        menu.draw(screen)

    elif game_state == "game":
        player.update(world.width)
        player.check_platform_collision(game_map.get_platforms())
        camera.update(player.x + player.size // 2, player.y + player.size // 2)
        gun.update(world.width, world.height, world.ground_y)
        pickup_manager.update(player.x, player.y, player.size, gun)
        enemy_manager.update(player.x, player.y, gun.bullets, world.width, world.ground_y)

        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        if enemy_manager.check_player_hit(player_rect):
            player_health -= 10
            if player_health <= 0:
                game_state = "menu"
                menu.reset_animations()

        world.draw(screen, camera)
        pickup_manager.draw(screen, camera)
        enemy_manager.draw(screen, camera)
        player.draw(screen, camera)
        gun.draw(screen, camera)
        draw_ui(screen, player, gun)

    elif game_state == "map":
        world.draw(screen, camera)
        pickup_manager.draw(screen, camera)
        enemy_manager.draw(screen, camera)
        player.draw(screen, camera)
        gun.draw(screen, camera)
        draw_ui(screen, player, gun)
        game_map.draw_overlay(screen, player.x, player.y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
