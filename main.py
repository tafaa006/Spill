import pygame
import sys
from Moduler.player import Player
from Moduler.camera import Camera
from Moduler.world import World
from Moduler.menu import Menu
from Moduler.shooting import Gun
from Moduler.pickups import PickupManager
from Moduler.enemies import EnemyManager, GoombaManager
from Moduler.kart import Map

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

game_state = "menu"
player_health = 100

game_map = Map()
world = World(game_map)
camera = Camera(WIDTH, HEIGHT)
player = Player(game_map.world_width // 2 - 20, game_map.ground_y - 40)
gun = Gun()
pickup_manager = PickupManager()
enemy_manager = EnemyManager()
goomba_manager = GoombaManager()
menu = Menu(WIDTH, HEIGHT)

def setup_level():
    pickup_manager.reset()
    enemy_manager.reset()
    goomba_manager.reset()

    pickup_manager.add_pickup(200, world.ground_y - 50, "gun")

    goomba_manager.add_goomba(400, world.ground_y - 40)
    goomba_manager.add_goomba(700, world.ground_y - 40)
    goomba_manager.add_goomba(1100, world.ground_y - 40)
    goomba_manager.add_goomba(1500, world.ground_y - 40)

    enemy_manager.add_enemy(900, world.ground_y - 40, "static")
    enemy_manager.add_enemy(1600, world.ground_y - 40, "moving")

def draw_ui():
    pygame.draw.rect(screen, (100, 0, 0), (300, 10, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (300, 10, player_health * 2, 20))
    pygame.draw.rect(screen, (255, 255, 255), (300, 10, 200, 20), 2)
    screen.blit(font.render(f"HP: {player_health}", True, (255, 255, 255)), (310, 12))
    if gun.has_gun:
        screen.blit(font.render(f"AMMO: {gun.ammo}", True, (255, 255, 255)), (10, 10))

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
                player_health = 100
                player.reset(game_map.world_width // 2 - 20, game_map.ground_y - 40)
                camera.reset()
                gun.reset()
                setup_level()

        elif game_state == "game":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                gun.shoot(player.x, player.y, player.size, player.get_shoot_direction())
            player.handle_input(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "menu"
                menu.reset_animations()

    if game_state == "menu":
        menu.update()
        menu.draw(screen)

    elif game_state == "game":
        player.update(world.width)

        if player.check_platform_collision(game_map.get_platforms()):
            game_state = "menu"
            menu.reset_animations()

        goomba_result = goomba_manager.check_player_collision(player.x, player.y, player.size, player.vel_y)
        if goomba_result == "stomp":
            player.vel_y = -10
        elif goomba_result == "hurt":
            game_state = "menu"
            menu.reset_animations()

        camera.update(player.x + player.size // 2, player.y + player.size // 2)
        gun.update(world.width, world.height, world.ground_y)
        pickup_manager.update(player.x, player.y, player.size, gun)
        goomba_manager.update(game_map.get_platforms(), world.width)
        enemy_manager.update(player.x, player.y, gun.bullets, world.width)

        if enemy_manager.check_player_hit(pygame.Rect(player.x, player.y, player.size, player.size)):
            player_health -= 10
            if player_health <= 0:
                game_state = "menu"
                menu.reset_animations()

        world.draw(screen, camera)
        pickup_manager.draw(screen, camera)
        goomba_manager.draw(screen, camera)
        enemy_manager.draw(screen, camera)
        player.draw(screen, camera)
        gun.draw(screen, camera)
        draw_ui()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
