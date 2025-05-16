import pygame
import sys
import random
import json
import os

pygame.init()

# Set ukuran layar
WIDTH, HEIGHT = 620, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Run")

# Memuat aset gambar
try:
    bg_img = pygame.image.load("assets/menu_start.png").convert()
    start_img = pygame.image.load("assets/start.png").convert_alpha()
    shop_img = pygame.image.load("assets/shop.png").convert_alpha()
    setting_img = pygame.image.load("assets/setting.png").convert_alpha()
    reset_img = pygame.image.load("assets/reset.png").convert_alpha()
    spritesheet = pygame.image.load("assets/player.png").convert_alpha()
    obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
    obstacle_arrow_img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()  # Obstacle panah
    coin_spritesheet = pygame.image.load("assets/coin.png").convert_alpha()
    double_jump_spritesheet = pygame.image.load("assets/double_jump.png").convert_alpha()
    shield_spritesheet = pygame.image.load("assets/shield.png").convert_alpha()
    multiplier_spritesheet = pygame.image.load("assets/multiplier.png").convert_alpha()
    player_roll_spritesheet = pygame.image.load("assets/player_roll.png").convert_alpha() 
    obstacle_enemy_img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
except:
    print("Gagal memuat aset.")
    pygame.quit()
    sys.exit()

# Konstanta dan variabel
SAVE_FILE = "save_data.json"
save_data = {"high_score": 0, "total_coin": 0}
MENU, GAMEPLAY = 0, 1
game_state = MENU

# Posisi tombol
start_button_rect = start_img.get_rect(center=(WIDTH // 2, 205))
shop_rect = shop_img.get_rect(center=(WIDTH // 2, 240))
setting_rect = setting_img.get_rect(center=(WIDTH // 2, 270))
reset_rect = reset_img.get_rect(center=(WIDTH // 2, 305))

# Fungsi untuk memuat data penyimpanan
def load_save():
    global save_data
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            save_data = json.load(f)

# Fungsi untuk menyimpan data game
def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(save_data, f)

# Fungsi untuk mereset data
def reset_data():
    global save_data
    save_data = {"high_score": 0, "total_coin": 0}
    save_game()

load_save()

# Animasi pemain
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

# Konstanta roll
roll_width = 768 // 8
roll_height = 32  # Misalnya, ukuran lebih kecil untuk menggulung
roll_frames = [player_roll_spritesheet.subsurface((i * roll_width, 0, roll_width, roll_height)) for i in range(8)]
roll_frame_index = 0
roll_animation_timer = 0
roll_animation_speed = 100
is_rolling = False
roll_timer = 0
roll_duration = 1000  # Durasi roll dalam milidetik

# Animasi enemy
enemy_width, enemy_height = 135 // 4, 64  # Sesuaikan dengan ukuran frame sprite Anda
enemy_frames = [obstacle_enemy_img.subsurface((i * enemy_width, 0, enemy_width, enemy_height)) for i in range(obstacle_enemy_img.get_width() // enemy_width)]
enemy_frame_index = 0
enemy_animation_timer = 0
enemy_animation_speed = 150  # Kecepatan animasi bisa disesuaikan

# Daftar rintangan dan interval spawn
obstacles = []
obstacle_spawn_timer = 0
obstacle_spawn_interval = 1500
obstacle_speed = 4

# Animasi koin
coin_width, coin_height = 16, 16
coin_frames = [coin_spritesheet.subsurface((i * coin_width, 0, coin_width, coin_height)) for i in range(coin_spritesheet.get_width() // coin_width)]
coin_frame_index = 0
coin_animation_timer = 0
coin_animation_speed = 100
coins = []
coin_spawn_timer = 0
coin_spawn_interval = 1500
coin_score = 0

# Animasi double jump
dj_width, dj_height = 32, 32
dj_frames = [double_jump_spritesheet.subsurface((i * dj_width, 0, dj_width, dj_height)) for i in range(4)]
dj_frame_index = 0
dj_animation_timer = 0
dj_animation_speed = 100
double_jumps = []
dj_spawn_timer = 0
dj_spawn_interval = 7000
dj_duration = 30000
dj_active = False
dj_timer = 0
can_double_jump = False
has_jumped_once = False

# Animasi shield
shield_width, shield_height = 32, 32
shield_frames = [shield_spritesheet.subsurface((i * shield_width, 0, shield_width, shield_height)) for i in range(4)]
shield_frame_index = 0
shield_animation_timer = 0
shield_animation_speed = 100
shields = []
shield_spawn_timer = 0
shield_spawn_interval = 10000
shield_active = False
shield_hits = 0
max_shield_hits = 2

score = 0
score_timer = 0
score_interval = 100

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()
running = True
DEBUG_HITBOX = True

# Animasi multiplier
multiplier_width, multiplier_height = 32, 32
multiplier_frames = [multiplier_spritesheet.subsurface((i * multiplier_width, 0, multiplier_width, multiplier_height)) for i in range(4)]
multiplier_frame_index = 0
multiplier_animation_timer = 0
multiplier_animation_speed = 100
multipliers = []
multiplier_spawn_timer = 0
multiplier_spawn_interval = 12000  # Multiplier spawn interval
multiplier_active = False
multiplier_duration = 10000
multiplier_timer = 0
multiplier_value = 1

score = 0
score_timer = 0
score_interval = 100

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()
running = True
DEBUG_HITBOX = True

# Fungsi untuk mereset game
def reset_game():
    global player_rect, player_speed_y, obstacles, bg_scroll_x, score
    global obstacle_spawn_interval, coins, coin_score, coin_spawn_timer
    global score_timer, double_jumps, dj_active, dj_timer
    global can_double_jump, has_jumped_once, dj_spawn_timer
    global shields, shield_active, shield_spawn_timer, shield_hits
    global shield_frame_index, shield_animation_timer
    global multipliers, multiplier_active, multiplier_timer, multiplier_value

    player_rect = pygame.Rect(100, HEIGHT - frame_height - 50, frame_width, frame_height)
    player_speed_y = 0
    obstacles.clear()
    coins.clear()
    double_jumps.clear()
    shields.clear()
    bg_scroll_x = 0
    score = 0
    coin_score = 0
    obstacle_spawn_interval = 1500
    coin_spawn_timer = 0
    score_timer = 0
    dj_active = False
    dj_timer = 0
    can_double_jump = False
    has_jumped_once = False
    dj_spawn_timer = 0
    shield_active = False
    shield_spawn_timer = 0
    shield_hits = 0
    shield_frame_index = 0
    shield_animation_timer = 0
    multiplier_active = False
    multiplier_timer = 0
    multiplier_value = 1
    
def update_player_animation():
    global player_frame_index, player_animation_timer
    global roll_frame_index, roll_animation_timer, is_rolling

    if is_rolling:
        roll_animation_timer += dt
        if roll_animation_timer >= roll_animation_speed:
            roll_animation_timer = 0
            roll_frame_index = (roll_frame_index + 1) % len(roll_frames)
    else:
        player_animation_timer += dt
        if player_animation_timer >= player_animation_speed:
            player_animation_timer = 0
            player_frame_index = (player_frame_index + 1) % len(player_frames)


# Game loop
while running:
    dt = clock.tick(60)
    obstacle_spawn_timer += dt
    coin_spawn_timer += dt
    player_animation_timer += dt
    coin_animation_timer += dt
    score_timer += dt
    dj_animation_timer += dt
    shield_animation_timer += dt
    multiplier_animation_timer += dt
    enemy_animation_timer += dt
    if enemy_animation_timer >= enemy_animation_speed:
        enemy_animation_timer = 0
        enemy_frame_index = (enemy_frame_index + 1) % len(enemy_frames)
    if not dj_active:
        dj_spawn_timer += dt
    if not shield_active:
        shield_spawn_timer += dt
    if not multiplier_active:
        multiplier_spawn_timer += dt

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
                    print("Buka Shop")
                elif setting_rect.collidepoint(mouse_pos):
                    print("Buka Pengaturan")
                elif reset_rect.collidepoint(mouse_pos):
                    reset_data()
                    print("Data direset")
        elif game_state == GAMEPLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and not is_rolling:  # Jika tombol panah bawah ditekan
                    is_rolling = True
                    roll_timer = pygame.time.get_ticks()
                    player_speed_y = 0  # Menghentikan gerakan vertikal saat roll
                    player_rect.height = roll_height  # Mengubah tinggi hitbox untuk menggulung
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:  
                    if player_rect.bottom >= ground_level:
                        player_speed_y = jump_power
                        has_jumped_once = False
                    elif dj_active and not has_jumped_once:
                        player_speed_y = jump_power
                        has_jumped_once = True
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

    # Menu
    if game_state == MENU:
        screen.blit(bg_img, (0, 0))
        screen.blit(start_img, start_button_rect)
        screen.blit(shop_img, shop_rect)
        screen.blit(setting_img, setting_rect)
        screen.blit(reset_img, reset_rect)
        screen.blit(font.render(f"High Score: {save_data['high_score']}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Total Coins: {save_data['total_coin']}", True, (255, 255, 0)), (10, 40))

    # Gameplay
    elif game_state == GAMEPLAY:
        if score_timer >= score_interval:
            score_timer = 0
            score += multiplier_value  # Apply multiplier to score

        # Update posisi pemain
        player_speed_y += gravity
        player_rect.y += player_speed_y
        if player_rect.bottom >= ground_level:
            player_rect.bottom = ground_level
            player_speed_y = 0
            has_jumped_once = False

        if player_animation_timer >= player_animation_speed:
            player_animation_timer = 0
            player_frame_index = (player_frame_index + 1) % len(player_frames)

        update_player_animation()  # Tambahkan ini

        # Perbarui logika roll
        if is_rolling:
            elapsed_roll_time = pygame.time.get_ticks() - roll_timer
            if elapsed_roll_time >= roll_duration:  # Setelah roll selesai
                is_rolling = False
                player_rect.height = frame_height  # Kembalikan tinggi hitbox ke ukuran normal

        bg_scroll_x = (bg_scroll_x - bg_speed) % WIDTH
        screen.blit(bg_img, (bg_scroll_x - WIDTH, 0))
        screen.blit(bg_img, (bg_scroll_x, 0))

        # Rintangan
        if obstacle_spawn_timer >= obstacle_spawn_interval:
            if random.random() < 0.5:
                # Rintangan biasa di tanah
                rect = obstacle_img.get_rect(bottom=ground_level, left=WIDTH + random.randint(0, 100))
                obstacles.append((rect, "normal"))
            elif random.random() < 0.3:
                # Rintangan panah di udara dengan tinggi random (60 atau 80)
                arrow_y = ground_level - random.choice([60, 80])  # Pilih antara 60 atau 80
                rect = obstacle_arrow_img.get_rect(left=WIDTH + random.randint(0, 100), top=arrow_y)
                obstacles.append((rect, "arrow"))
            elif random.random() < 0.2:
                rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - enemy_height, enemy_width, enemy_height)
                obstacles.append((rect, "enemy"))  # Tambahkan tipe "enemy" ke tuple


            obstacle_spawn_timer = 0
            obstacle_spawn_interval = max(800, obstacle_spawn_interval - 10)

        for o, o_type in obstacles[:]:
            o.x -= obstacle_speed
            if o.right < 0:
                obstacles.remove((o, o_type))
                continue

             # Gambar obstacle sesuai tipe    
            if o_type == "normal":
                screen.blit(obstacle_img, o)
            elif o_type == "arrow":
                screen.blit(obstacle_arrow_img, o)
            elif o_type == "enemy":
                screen.blit(enemy_frames[enemy_frame_index], o)

            # Cek tabrakan
            if player_rect.inflate(-80, -30).colliderect(o):
                if shield_active:
                    obstacles.remove((o, o_type))
                    shield_hits += 1
                    if shield_hits >= max_shield_hits:
                        shield_active = False
                    continue
                else:
                    if score > save_data["high_score"]:
                        save_data["high_score"] = score
                    save_data["total_coin"] += coin_score
                    save_game()
                    game_state = MENU
                    break

        # Koin
        if coin_spawn_timer >= coin_spawn_interval:
            rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - random.randint(40, 80), coin_width, coin_height)
            coins.append(rect)
            coin_spawn_timer = 0

        if coin_animation_timer >= coin_animation_speed:
            coin_animation_timer = 0
            coin_frame_index = (coin_frame_index + 1) % len(coin_frames)

        for c in coins[:]:
            c.x -= obstacle_speed
            if c.right < 0:
                coins.remove(c)
                continue
            screen.blit(coin_frames[coin_frame_index], c)
            if player_rect.inflate(-80, -30).colliderect(c):
                coins.remove(c)
                coin_score += 1

        # Double Jump
        if not dj_active and dj_spawn_timer >= dj_spawn_interval:
            rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - random.randint(40, 80), dj_width, dj_height)
            double_jumps.append(rect)
            dj_spawn_timer = 0

        if dj_animation_timer >= dj_animation_speed:
            dj_animation_timer = 0
            dj_frame_index = (dj_frame_index + 1) % len(dj_frames)

        for dj in double_jumps[:]:
            dj.x -= obstacle_speed
            if dj.right < 0:
                double_jumps.remove(dj)
                continue
            screen.blit(dj_frames[dj_frame_index], dj)
            if player_rect.inflate(-80, -30).colliderect(dj):
                double_jumps.remove(dj)
                dj_active = True
                dj_timer = pygame.time.get_ticks()

        if dj_active:
            elapsed = pygame.time.get_ticks() - dj_timer
            if elapsed >= dj_duration:
                dj_active = False
            else:
                t = font.render(f"Double Jump: {(dj_duration - elapsed)//1000}s", True, (0, 255, 0))
                screen.blit(t, (WIDTH - 220, 10))

        # Shield
        if not shield_active and shield_spawn_timer >= shield_spawn_interval:
            rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - random.randint(40, 80), shield_width, shield_height)
            shields.append(rect)
            shield_spawn_timer = 0

        if shield_animation_timer >= shield_animation_speed:
            shield_animation_timer = 0
            shield_frame_index = (shield_frame_index + 1) % len(shield_frames)

        for s in shields[:]:
            s.x -= obstacle_speed
            if s.right < 0:
                shields.remove(s)
                continue
            screen.blit(shield_frames[shield_frame_index], s)
            if player_rect.inflate(-80, -30).colliderect(s):
                shields.remove(s)
                shield_active = True
                shield_hits = 0

        if shield_active:
            t = font.render(f"Shield: {max_shield_hits - shield_hits} hits", True, (128, 128, 255))
            screen.blit(t, (WIDTH - 220, 40))

        # Multiplier
        if not multiplier_active and multiplier_spawn_timer >= multiplier_spawn_interval:
            rect = pygame.Rect(WIDTH + random.randint(0, 100), ground_level - random.randint(40, 80), multiplier_width, multiplier_height)
            multipliers.append(rect)
            multiplier_spawn_timer = 0

        if multiplier_animation_timer >= multiplier_animation_speed:
            multiplier_animation_timer = 0
            multiplier_frame_index = (multiplier_frame_index + 1) % len(multiplier_frames)

        for m in multipliers[:]:
            m.x -= obstacle_speed
            if m.right < 0:
                multipliers.remove(m)
                continue
            screen.blit(multiplier_frames[multiplier_frame_index], m)
            if player_rect.inflate(-80, -30).colliderect(m):
                multipliers.remove(m)
                multiplier_active = True
                multiplier_timer = pygame.time.get_ticks()
                multiplier_value = 2  # Increase score multiplier value
                
        if multiplier_active:
            elapsed = pygame.time.get_ticks() - multiplier_timer
            if elapsed >= multiplier_duration:
                multiplier_active = False
                multiplier_value = 1  # Reset multiplier value
            else:
                t = font.render(f"Multiplier: {(multiplier_duration - elapsed)//1000}s", True, (255, 215, 0))
                screen.blit(t, (WIDTH - 220, 70))

        # Gambar pemain
        if is_rolling:
            screen.blit(roll_frames[roll_frame_index], player_rect)
        else:
            screen.blit(player_frames[player_frame_index], player_rect)

        # Debug
        if DEBUG_HITBOX:
            pygame.draw.rect(screen, (255, 0, 0), player_rect.inflate(-80, -30), 2)
            for c in coins:
                pygame.draw.rect(screen, (255, 255, 0), c, 2)
            for o, o_type in obstacles:
                if o_type == "arrow":
                    pygame.draw.rect(screen, (255, 255, 255), o, 2)  # Warna putih untuk obstacle panah
                else:
                    pygame.draw.rect(screen, (0, 0, 255), o, 2)
            for dj in double_jumps:
                pygame.draw.rect(screen, (0, 255, 0), dj, 2)
            for s in shields:
                pygame.draw.rect(screen, (0, 0, 255), s, 2)
            for m in multipliers:
                pygame.draw.rect(screen, (255, 165, 0), m, 2)  # Warna oranye untuk multiplier

        # Tampilkan skor
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))  # Naikkan posisi sedikit
        screen.blit(font.render(f"Coins: {coin_score}", True, (255, 255, 0)), (10, 40))  # Naikkan posisi sedikit

    pygame.display.flip()

pygame.quit()
sys.exit()
