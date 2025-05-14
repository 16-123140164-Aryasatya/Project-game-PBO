import pygame
import sys
import random
import json
import os

pygame.init()

WIDTH, HEIGHT = 620, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Run")

# Load gambar
try:
    bg_img = pygame.image.load("assets/menu_start.png").convert()
    start_img = pygame.image.load("assets/start.png").convert_alpha()
    shop_img = pygame.image.load("assets/shop.png").convert_alpha()
    setting_img = pygame.image.load("assets/setting.png").convert_alpha()
    reset_img = pygame.image.load("assets/reset.png").convert_alpha()
    spritesheet = pygame.image.load("assets/player.png").convert_alpha()
    obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
    coin_spritesheet = pygame.image.load("assets/coin.png").convert_alpha()
except:
    print("Gagal load gambar! Pastikan folder assets dan file ada.")
    pygame.quit()
    sys.exit()

# Tombol
start_button_rect = start_img.get_rect(center=(WIDTH // 2, 205))
shop_rect = shop_img.get_rect(center=(WIDTH // 2, 240))
setting_rect = setting_img.get_rect(center=(WIDTH // 2, 270))
reset_rect = reset_img.get_rect(center=(WIDTH // 2, 305))

# Status game
MENU = 0
GAMEPLAY = 1
game_state = MENU

# File penyimpanan data
SAVE_FILE = "save_data.json"
save_data = {"high_score": 0, "total_coin": 0}

def load_save():
    global save_data
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            save_data = json.load(f)

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(save_data, f)

def reset_data():
    global save_data
    save_data = {"high_score": 0, "total_coin": 0}
    save_game()

load_save()

# Player setup
frame_width = 768 // 8
frame_height = 64
player_frames = [spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height)) for i in range(8)]
player_frame_index = 0
player_animation_timer = 0
player_animation_speed = 100

player_rect = pygame.Rect(100, HEIGHT - frame_height - 50, frame_width, frame_height)
player_speed_y = 0
gravity = 0.5
jump_power = -10
ground_level = HEIGHT - 50

bg_scroll_x = 0
bg_speed = 2

obstacles = []
obstacle_spawn_timer = 0
obstacle_spawn_interval = 1500
obstacle_speed = 4

# Coin setup
coin_width = 16
coin_height = 16
coin_frames = [coin_spritesheet.subsurface((i * coin_width, 0, coin_width, coin_height)) for i in range(coin_spritesheet.get_width() // coin_width)]
coin_frame_index = 0
coin_animation_timer = 0
coin_animation_speed = 100

coins = []
coin_spawn_timer = 0
coin_spawn_interval = 1000
coin_score = 0

score = 0
score_timer = 0
score_interval = 100

font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()
running = True

def reset_game():
    global player_rect, player_speed_y, obstacles, bg_scroll_x, score
    global obstacle_spawn_interval, coins, coin_score, coin_spawn_timer
    global score_timer

    player_rect = pygame.Rect(100, HEIGHT - frame_height - 50, frame_width, frame_height)
    player_speed_y = 0
    obstacles = []
    coins = []
    bg_scroll_x = 0
    score = 0
    coin_score = 0
    obstacle_spawn_interval = 1500
    coin_spawn_timer = 0
    score_timer = 0

while running:
    dt = clock.tick(60)
    obstacle_spawn_timer += dt
    coin_spawn_timer += dt
    player_animation_timer += dt
    coin_animation_timer += dt
    score_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    game_state = GAMEPLAY
                    reset_game()
                elif shop_rect.collidepoint(mouse_pos):
                    print("Open Shop")
                elif setting_rect.collidepoint(mouse_pos):
                    print("Open Settings")
                elif reset_rect.collidepoint(mouse_pos):
                    reset_data()
                    print("Data telah direset")

        elif game_state == GAMEPLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= ground_level:
                    player_speed_y = jump_power
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

    if game_state == MENU:
        screen.blit(bg_img, (0, 0))
        screen.blit(start_img, start_button_rect)
        screen.blit(shop_img, shop_rect)
        screen.blit(setting_img, setting_rect)
        screen.blit(reset_img, reset_rect)

        high_score_text = font.render(f"High Score: {save_data['high_score']}", True, (255, 255, 255))
        total_coin_text = font.render(f"Total Coins: {save_data['total_coin']}", True, (255, 255, 0))
        screen.blit(high_score_text, (10, 10))
        screen.blit(total_coin_text, (10, 40))

    elif game_state == GAMEPLAY:
        if score_timer >= score_interval:
            score_timer = 0
            score += 1

        player_speed_y += gravity
        player_rect.y += player_speed_y
        if player_rect.bottom >= ground_level:
            player_rect.bottom = ground_level
            player_speed_y = 0

        if player_animation_timer >= player_animation_speed:
            player_animation_timer = 0
            player_frame_index = (player_frame_index + 1) % len(player_frames)

        bg_scroll_x = (bg_scroll_x - bg_speed) % WIDTH
        screen.blit(bg_img, (bg_scroll_x - WIDTH, 0))
        screen.blit(bg_img, (bg_scroll_x, 0))

        if obstacle_spawn_timer >= obstacle_spawn_interval:
            obstacle_rect = obstacle_img.get_rect(bottom=ground_level, left=WIDTH + random.randint(0, 100))
            obstacles.append(obstacle_rect)
            obstacle_spawn_timer = 0
            obstacle_spawn_interval = max(800, obstacle_spawn_interval - 10)

        for obstacle in obstacles[:]:
            obstacle.x -= obstacle_speed
            if obstacle.right < 0:
                obstacles.remove(obstacle)
                continue

            screen.blit(obstacle_img, obstacle)
            obstacle_hitbox = obstacle.inflate(-10, -10)
            pygame.draw.rect(screen, (0, 0, 255), obstacle_hitbox, 1)  # Hitbox biru

            player_hitbox = player_rect.inflate(-80, -30)
            pygame.draw.rect(screen, (255, 0, 0), player_hitbox, 1)  # Hitbox merah

            if player_hitbox.colliderect(obstacle_hitbox):
                if score > save_data["high_score"]:
                    save_data["high_score"] = score
                save_data["total_coin"] += coin_score
                save_game()
                print("Game Over!")
                game_state = MENU
                break

        if coin_spawn_timer >= coin_spawn_interval:
            coin_rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - random.randint(40, 80), coin_width, coin_height)
            coins.append(coin_rect)
            coin_spawn_timer = 0

        if coin_animation_timer >= coin_animation_speed:
            coin_animation_timer = 0
            coin_frame_index = (coin_frame_index + 1) % len(coin_frames)

        for coin in coins[:]:
            coin.x -= obstacle_speed
            if coin.right < 0:
                coins.remove(coin)
                continue

            screen.blit(coin_frames[coin_frame_index], coin)

            coin_hitbox = coin.inflate(-2, -2)
            pygame.draw.rect(screen, (255, 255, 0), coin_hitbox, 1)  # Hitbox kuning
            player_hitbox = player_rect.inflate(-80, -30)

            if player_hitbox.colliderect(coin_hitbox):
                coins.remove(coin)
                coin_score += 1

        screen.blit(player_frames[player_frame_index], player_rect)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        coin_text = font.render(f"Coins: {coin_score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(coin_text, (10, 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
