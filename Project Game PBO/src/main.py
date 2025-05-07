import pygame
import sys
import random

# Inisialisasi pygame
pygame.init()

# Ukuran layar
WIDTH, HEIGHT = 620, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Run")

# Load gambar
try:
    bg_img = pygame.image.load("assets/menu_start.png").convert()
    start_img = pygame.image.load("assets/start.png").convert_alpha()
    shop_img = pygame.image.load("assets/shop.png").convert_alpha()
    setting_img = pygame.image.load("assets/setting.png").convert_alpha()
    spritesheet = pygame.image.load("assets/player.png").convert_alpha()
    obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
except:
    print("Gagal load gambar! Pastikan folder assets dan file ada.")
    pygame.quit()
    sys.exit()

# Tombol
start_button_rect = start_img.get_rect(center=(WIDTH // 2, 205))
shop_rect = shop_img.get_rect(center=(WIDTH // 2, 240))
setting_rect = setting_img.get_rect(center=(WIDTH // 2, 270))

# Status game
MENU = 0
GAMEPLAY = 1
game_state = MENU

# Ambil frame pertama dari player.png
total_frames = 11
frame_width = spritesheet.get_width() // total_frames
frame_height = spritesheet.get_height()
player_img = spritesheet.subsurface((0, 0, frame_width, frame_height))

# Player setup
player_rect = pygame.Rect(100, HEIGHT - frame_height - 50, frame_width, frame_height)
player_speed_y = 0
gravity = 0.5
jump_power = -10
ground_level = HEIGHT - 50

# Background scroll
bg_scroll_x = 0
bg_speed = 2

# Obstacle setup
obstacles = []
obstacle_spawn_timer = 0
obstacle_spawn_interval = 1500  # ms
obstacle_speed = 4
score = 0

# Font
font = pygame.font.SysFont(None, 36)

# Clock
clock = pygame.time.Clock()
running = True

def reset_game():
    global player_rect, player_speed_y, obstacles, bg_scroll_x, score, obstacle_spawn_interval
    player_rect = pygame.Rect(100, HEIGHT - frame_height - 50, frame_width, frame_height)
    player_speed_y = 0
    obstacles = []
    bg_scroll_x = 0
    score = 0
    obstacle_spawn_interval = 1500

# Loop utama
while running:
    dt = clock.tick(60)
    obstacle_spawn_timer += dt

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

        elif game_state == GAMEPLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= ground_level:
                    player_speed_y = jump_power
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

    # Update dan render
    if game_state == MENU:
        screen.blit(bg_img, (0, 0))
        screen.blit(start_img, start_button_rect)
        screen.blit(shop_img, shop_rect)
        screen.blit(setting_img, setting_rect)

    elif game_state == GAMEPLAY:
        # Update player jump
        player_speed_y += gravity
        player_rect.y += player_speed_y
        if player_rect.bottom >= ground_level:
            player_rect.bottom = ground_level
            player_speed_y = 0

        # Geser background
        bg_scroll_x = (bg_scroll_x - bg_speed) % WIDTH
        screen.blit(bg_img, (bg_scroll_x - WIDTH, 0))
        screen.blit(bg_img, (bg_scroll_x, 0))

        # Spawn obstacle
        if obstacle_spawn_timer >= obstacle_spawn_interval:
            obstacle_rect = obstacle_img.get_rect(
                bottom=ground_level,
                left=WIDTH + random.randint(0, 100)
            )
            obstacles.append(obstacle_rect)
            obstacle_spawn_timer = 0
            obstacle_spawn_interval = max(800, obstacle_spawn_interval - 10)
            score += 1

        # Update dan gambar obstacles
        for obstacle in obstacles[:]:
            obstacle.x -= obstacle_speed
            if obstacle.right < 0:
                obstacles.remove(obstacle)
            screen.blit(obstacle_img, obstacle)

            # Hitbox obstacle diperkecil
            shrink_margin = 10  # Semakin besar, hitbox semakin kecil
            obstacle_hitbox = obstacle.inflate(-shrink_margin, -shrink_margin)

            if player_rect.colliderect(obstacle_hitbox):
                print("Game Over!")
                game_state = MENU
                break

        # Gambar player
        screen.blit(player_img, player_rect)

        # Tampilkan skor
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
