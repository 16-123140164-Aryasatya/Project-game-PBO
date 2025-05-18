import pygame
import sys
import random
import json
import os

pygame.init()

# Constants
WIDTH, HEIGHT = 620, 360
SAVE_FILE = "save_data.json"
MENU, GAMEPLAY, SHOP, SETTING = 0, 1, 2, 3      
DEBUG_HITBOX = True

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Runner Saga")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.game_state = MENU
        self.running = True
        
        # Initialize sound system
        pygame.mixer.init()
        self.sounds = {}
        
        # Settings
        self.settings = {
            "music_enabled": True,
            "sound_effects_enabled": True,
            "hitbox_visible": DEBUG_HITBOX
        }

        # Load assets
        self.load_assets()
        self.load_sounds()

        # Play menu music initially
        self.play_menu_music()
        
        # Initialize game components
        self.save_data = {"high_score": 0, "total_coin": 0}
        self.shop_items = {
            "shield": {"level": 1, "price": 100, "max_level": 5},
            "double_jump": {"level": 1, "price": 150, "max_level": 3},
            "multiplier": {"level": 1, "price": 200, "max_level": 3}
        }
        
        # Button positions
        self.start_button_rect = self.start_img.get_rect(center=(WIDTH // 2, 140))
        self.shop_rect = self.shop_img.get_rect(center=(WIDTH // 2, 180))
        self.setting_rect = self.setting_img.get_rect(center=(WIDTH // 2, 220))
        self.reset_rect = self.reset_img.get_rect(center=(WIDTH // 2, 270))
        
        # Load saved data
        self.load_save()
        
        # Initialize player and game objects
        self.player = Player(self)
        self.obstacle_manager = ObstacleManager(self)
        self.coin_manager = CoinManager(self)
        self.powerup_manager = PowerupManager(self)
    
    def load_sounds(self):
        try:
            # Background music
            self.sounds['menu_music'] = pygame.mixer.Sound("assets/sound_menu.wav")
            self.sounds['gameplay_music'] = pygame.mixer.Sound("assets/sound_gameplay.wav")
            
            # Sound effects
            self.sounds['collectible'] = pygame.mixer.Sound("assets/sound_collectible.wav")
            
        
            # Set volume levels
            self.sounds['menu_music'].set_volume(0.5)
            self.sounds['gameplay_music'].set_volume(0.5)
            self.sounds['collectible'].set_volume(0.7)
            
        except Exception as e:
            print(f"Failed to load sounds: {e}")

    def play_menu_music(self):
        pygame.mixer.stop()
        self.sounds['menu_music'].play(-1)  # -1 means loop indefinitely
    
    def play_gameplay_music(self):
        pygame.mixer.stop()
        self.sounds['gameplay_music'].play(-1)
    
    def play_collectible_sound(self):
        self.sounds['collectible'].play()

    def load_assets(self):
        try:
            self.bg_img = pygame.image.load("assets/menu_start.png").convert()
            self.start_img = pygame.image.load("assets/start.png").convert_alpha()
            self.shop_img = pygame.image.load("assets/shop.png").convert_alpha()
            self.setting_img = pygame.image.load("assets/setting.png").convert_alpha()
            self.reset_img = pygame.image.load("assets/reset.png").convert_alpha()
            
            # Player sprites
            player_spritesheet = pygame.image.load("assets/player.png").convert_alpha()
            self.player_frames = self.load_frames(player_spritesheet, 768, 64, 8)
            self.player_roll_frames = self.load_frames(
                pygame.image.load("assets/player_roll.png").convert_alpha(), 
                768, 32, 8
            )
            self.player_attack_frames = self.load_frames(
                pygame.image.load("assets/player_attack.png").convert_alpha(),
                768, 64, 8
            )
            
            # Obstacles
            self.obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
            self.obstacle_arrow_img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
            enemy_img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
            self.enemy_frames = self.load_frames(enemy_img, 135, 64, 4)
            
            # Powerups
            self.coin_frames = self.load_frames(
                pygame.image.load("assets/coin.png").convert_alpha(),
                240, 16, 15
            )
            self.dj_frames = self.load_frames(
                pygame.image.load("assets/double_jump.png").convert_alpha(),
                128, 32, 4
            )
            self.shield_frames = self.load_frames(
                pygame.image.load("assets/shield.png").convert_alpha(),
                128, 32, 4
            )
            self.multiplier_frames = self.load_frames(
                pygame.image.load("assets/multiplier.png").convert_alpha(),
                128, 32, 4
            )
        except Exception as e:
            print(f"Failed to load assets: {e}")
            pygame.quit()
            sys.exit()
    
    def load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        frames = []
        for i in range(frame_count):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height))
            frames.append(frame)
        return frames
    
    def load_save(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.save_data.update(data)
                if "shop_items" in data:
                    self.shop_items.update(data["shop_items"])
    
    def save_game(self):
        self.save_data["shop_items"] = self.shop_items
        with open(SAVE_FILE, "w") as f:
            json.dump(self.save_data, f)
    
    def reset_data(self):
        self.save_data = {"high_score": 0, "total_coin": 0}
        self.shop_items = {
            "shield": {"level": 1, "price": 100, "max_level": 5},
            "double_jump": {"level": 1, "price": 150, "max_level": 3},
            "multiplier": {"level": 1, "price": 200, "max_level": 3}
        }
        self.save_game()
    
    def draw_shop(self):
        self.screen.blit(self.bg_img, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Display coins
        coins_text = self.font.render(f"Coins: {self.save_data['total_coin']}", True, (255, 255, 0))
        self.screen.blit(coins_text, (WIDTH - 150, 20))
        
        title = self.font.render("SHOP", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        back_btn = pygame.Rect(20, 20, 80, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), back_btn)
        self.screen.blit(self.font.render("Back", True, (255, 255, 255)), (back_btn.x + 20, back_btn.y + 10))
        
        buttons = []
        y_pos = 100
        
        for item, data in self.shop_items.items():
            # Draw item icon
            if item == "shield":
                img = self.shield_frames[0]
            elif item == "double_jump":
                img = self.dj_frames[0]
            else:
                img = self.multiplier_frames[0]
            
            img = pygame.transform.scale(img, (50, 50))
            self.screen.blit(img, (50, y_pos))
            
            # Item info
            self.screen.blit(self.font.render(f"{item.replace('_', ' ').title()}", True, (255, 255, 255)), (120, y_pos))
            self.screen.blit(self.font.render(f"Lvl: {data['level']}/{data['max_level']}", True, (200, 200, 200)), (120, y_pos + 25))
            
            # Buy button
            if data['level'] < data['max_level']:
                btn_rect = pygame.Rect(WIDTH - 150, y_pos + 10, 120, 40)
                btn_color = (50, 200, 50) if self.save_data['total_coin'] >= data['price'] else (100, 100, 100)
                pygame.draw.rect(self.screen, btn_color, btn_rect)
                self.screen.blit(self.font.render(f"Buy: {data['price']}", True, (255, 255, 255)), (WIDTH - 140, y_pos + 20))
                buttons.append((item, btn_rect))
            
            y_pos += 80
        
        return back_btn, buttons
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button_rect.collidepoint(mouse_pos):
                        self.game_state = GAMEPLAY
                        self.play_gameplay_music()
                        self.reset_game()
                    elif self.shop_rect.collidepoint(mouse_pos):
                        self.game_state = SHOP
                    elif self.setting_rect.collidepoint(mouse_pos):
                        self.game_state = SETTING  # New state for settings
                    elif self.reset_rect.collidepoint(mouse_pos):
                        self.reset_data()
            
            elif self.game_state == GAMEPLAY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.player.start_roll()
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.player.jump()
                    elif event.key == pygame.K_s:
                        self.player.attack()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = MENU
                        self.play_menu_music()
                    elif event.key == pygame.K_q:  # Toggle hitbox with Q key
                        self.settings["hitbox_visible"] = not self.settings["hitbox_visible"]
            
            elif self.game_state == SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    back_btn, buy_buttons = self.draw_shop()
                    
                    if back_btn.collidepoint(mouse_pos):
                        self.game_state = MENU
                    else:
                        for item, btn_rect in buy_buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                self.buy_item(item)
                                self.play_collectible_sound()  # Play sound when buying
                                break

            elif self.game_state == SETTING:  # Settings menu
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    back_btn, music_btn, sfx_btn = self.draw_settings()
                    
                    if back_btn.collidepoint(mouse_pos):
                        self.game_state = MENU
                    elif music_btn.collidepoint(mouse_pos):
                        self.toggle_music()
                    elif sfx_btn.collidepoint(mouse_pos):
                        self.toggle_sound_effects()
    
    def toggle_music(self):
        self.settings["music_enabled"] = not self.settings["music_enabled"]
        if self.settings["music_enabled"]:
            if self.game_state == MENU:
                self.play_menu_music()
            elif self.game_state == GAMEPLAY:
                self.play_gameplay_music()
        else:
            pygame.mixer.stop()

    def toggle_sound_effects(self):
        self.settings["sound_effects_enabled"] = not self.settings["sound_effects_enabled"]
    
    def play_menu_music(self):
        if not self.settings["music_enabled"]:
            return
        pygame.mixer.stop()
        self.sounds['menu_music'].play(-1)

    def play_gameplay_music(self):
        if not self.settings["music_enabled"]:
            return
        pygame.mixer.stop()
        self.sounds['gameplay_music'].play(-1)
    
    def play_collectible_sound(self):
        if not self.settings["sound_effects_enabled"]:
            return
        self.sounds['collectible'].play()

    def draw_settings(self):
        self.screen.blit(self.bg_img, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("SETTINGS", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Back button
        back_btn = pygame.Rect(20, 20, 90, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), back_btn)
        self.screen.blit(self.font.render("Back", True, (255, 255, 255)), (back_btn.x + 15, back_btn.y + 10))

        # Music toggle
        music_btn = pygame.Rect(WIDTH//2 - 100, 120, 260, 50)
        btn_color = (50, 200, 50) if self.settings["music_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.screen, btn_color, music_btn)
        status = "ON" if self.settings["music_enabled"] else "OFF"
        self.screen.blit(self.font.render(f"Music:            {status}", True, (255, 255, 255)), 
                        (music_btn.x + 50, music_btn.y + 15))
        
        # Sound effects toggle
        sfx_btn = pygame.Rect(WIDTH//2 - 100, 190, 260, 50)
        btn_color = (50, 200, 50) if self.settings["sound_effects_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.screen, btn_color, sfx_btn)
        status = "ON" if self.settings["sound_effects_enabled"] else "OFF"
        self.screen.blit(self.font.render(f"Sound Effects: {status}", True, (255, 255, 255)), 
                        (sfx_btn.x + 30, sfx_btn.y + 15))
        
        # Hitbox visibility info
        hitbox_text = self.font.render("Press Q in-game to toggle hitboxes", True, (255, 255, 255))
        self.screen.blit(hitbox_text, (WIDTH//2 - hitbox_text.get_width()//2, 260))
        
        return back_btn, music_btn, sfx_btn

    def buy_item(self, item):
        if self.save_data['total_coin'] >= self.shop_items[item]['price']:
            self.save_data['total_coin'] -= self.shop_items[item]['price']
            self.shop_items[item]['level'] += 1
            self.shop_items[item]['price'] = int(self.shop_items[item]['price'] * 1.5)
            self.save_game()
            
            # Visual feedback
            self.draw_shop()
            pygame.display.flip()
            pygame.time.delay(100)
    
    def reset_game(self):
        self.player.reset()
        self.obstacle_manager.reset()
        self.coin_manager.reset()
        self.powerup_manager.reset()
        self.apply_upgrades()
    
    def apply_upgrades(self):
        self.powerup_manager.max_shield_hits = 1 + self.shop_items["shield"]["level"]
        self.powerup_manager.dj_duration = 20000 + (self.shop_items["double_jump"]["level"] * 10000)
        self.powerup_manager.multiplier_value = 1 + (0.5 * self.shop_items["multiplier"]["level"])
        
        # Adjust spawn intervals based on upgrades
        self.powerup_manager.shield_spawn_interval = max(3000, 10000 - (self.shop_items["shield"]["level"] * 1500))
        self.powerup_manager.dj_spawn_interval = max(5000, 15000 - (self.shop_items["double_jump"]["level"] * 3000))
        self.powerup_manager.multiplier_spawn_interval = max(8000, 15000 - (self.shop_items["multiplier"]["level"] * 2000))
    
    def update(self, dt):
        if self.game_state == GAMEPLAY:
            self.player.update(dt)
            self.obstacle_manager.update(dt)
            self.coin_manager.update(dt)
            self.powerup_manager.update(dt)
            
            # Check collisions
            self.check_collisions()
            
            # Update score
            if self.player.score_timer >= self.player.score_interval:
                self.player.score_timer = 0
                self.player.score += self.powerup_manager.multiplier_value
    
    def check_collisions(self):
        # Check obstacle collisions
        for obstacle, o_type in self.obstacle_manager.obstacles[:]:
            if self.player.rect.inflate(-80, -30).colliderect(obstacle):
                if self.powerup_manager.shield_active:
                    self.obstacle_manager.obstacles.remove((obstacle, o_type))
                    self.powerup_manager.shield_hits += 1
                    if self.powerup_manager.shield_hits >= self.powerup_manager.max_shield_hits:
                        self.powerup_manager.shield_active = False
                    continue
                else:
                    self.game_over()
                    break
        
        # Check coin collisions
        for coin in self.coin_manager.coins[:]:
            if self.player.rect.inflate(-80, -30).colliderect(coin):
                self.coin_manager.coins.remove(coin)
                self.player.coin_score += 1
                self.play_collectible_sound()  # Play sound when collecting coin
    
    def game_over(self):
        if self.player.score > self.save_data["high_score"]:
            self.save_data["high_score"] = self.player.score
        self.save_data["total_coin"] += self.player.coin_score
        self.save_game()
        self.game_state = MENU
        self.play_menu_music()
        
    
    def render(self):
        if self.game_state == MENU:
            self.screen.blit(self.bg_img, (0, 0))
            self.screen.blit(self.start_img, self.start_button_rect)
            self.screen.blit(self.shop_img, self.shop_rect)
            self.screen.blit(self.setting_img, self.setting_rect)
            self.screen.blit(self.reset_img, self.reset_rect)
            
            self.screen.blit(
                self.font.render(f"High Score: {self.save_data['high_score']}", True, (255, 255, 255)), 
                (10, 10)
            )
            self.screen.blit(
                self.font.render(f"Total Coins: {self.save_data['total_coin']}", True, (255, 255, 0)), 
                (10, 40)
            )
        
        elif self.game_state == SHOP:
            self.draw_shop()

        elif self.game_state == SETTING:  # Settings menu
            self.draw_settings()
        
        elif self.game_state == GAMEPLAY:
            # Draw background
            self.screen.blit(self.bg_img, (self.player.bg_scroll_x - WIDTH, 0))
            self.screen.blit(self.bg_img, (self.player.bg_scroll_x, 0))
            
            # Draw game objects
            self.obstacle_manager.draw(self.screen)
            self.coin_manager.draw(self.screen)
            self.powerup_manager.draw(self.screen)
            self.player.draw(self.screen)
            
            # Draw UI
            self.screen.blit(
                self.font.render(f"Score: {self.player.score}", True, (255, 255, 255)), 
                (10, 10)
            )
            self.screen.blit(
                self.font.render(f"Coins: {self.player.coin_score}", True, (255, 255, 0)), 
                (10, 40)
            )
            
            # Draw powerup status
            if self.powerup_manager.dj_active:
                elapsed = pygame.time.get_ticks() - self.powerup_manager.dj_timer
                self.screen.blit(
                    self.font.render(f"Double Jump: {(self.powerup_manager.dj_duration - elapsed)//1000}s", True, (0, 255, 0)), 
                    (WIDTH - 220, 10)
                )
            
            if self.powerup_manager.shield_active:
                self.screen.blit(
                    self.font.render(f"Shield: {self.powerup_manager.max_shield_hits - self.powerup_manager.shield_hits} hits", True, (128, 128, 255)), 
                    (WIDTH - 220, 40)
                )
            
            if self.powerup_manager.multiplier_active:
                elapsed = pygame.time.get_ticks() - self.powerup_manager.multiplier_timer
                self.screen.blit(
                    self.font.render(f"Multiplier: {(self.powerup_manager.multiplier_duration - elapsed)//1000}s", True, (255, 215, 0)), 
                    (WIDTH - 220, 70)
                )
            
            # Debug hitboxes
            if self.settings["hitbox_visible"]:
                pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect.inflate(-80, -30), 2)
                for c in self.coin_manager.coins:
                    pygame.draw.rect(self.screen, (255, 255, 0), c, 2)
                for o, o_type in self.obstacle_manager.obstacles:
                    color = (255, 255, 255) if o_type == "arrow" else (0, 0, 255)
                    pygame.draw.rect(self.screen, color, o, 2)
                for dj in self.powerup_manager.double_jumps:
                    pygame.draw.rect(self.screen, (0, 255, 0), dj, 2)
                for s in self.powerup_manager.shields:
                    pygame.draw.rect(self.screen, (0, 0, 255), s, 2)
                for m in self.powerup_manager.multipliers:
                    pygame.draw.rect(self.screen, (255, 165, 0), m, 2)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()

class Player:
    def __init__(self, game):
        self.game = game
        self.reset()
        # Hitbox offset untuk animasi yang berbeda
        self.normal_hitbox = pygame.Rect(0, 0, 768//8, 64)
        self.roll_hitbox = pygame.Rect(0, 0, 768//8, 32)
        self.attack_hitbox_rect = pygame.Rect(0, 0, 768//8, 64)
    
    def reset(self):
        self.rect = pygame.Rect(100, HEIGHT - 64 - 50, 768//8, 64)
        self.speed_y = 0
        self.gravity = 0.5
        self.jump_power = -10
        self.ground_level = HEIGHT - 50
        self.bg_scroll_x = 0
        self.bg_speed = 2
        
        # Animation
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
        
        # Rolling
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_duration = 1000
        
        # Attacking
        self.is_attacking = False
        self.attack_frame_index = 0
        self.attack_animation_timer = 0
        self.attack_animation_speed = 80
        self.attack_timer = 0
        self.attack_duration = 1000
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.attack_hitbox = None
        
        # Game stats
        self.score = 0
        self.coin_score = 0
        self.score_timer = 0
        self.score_interval = 100
        
        # Jumping
        self.has_jumped_once = False
    
    def update(self, dt):
    # Apply gravity
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
        
        # Ground collision
        if self.rect.bottom >= self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0
            self.has_jumped_once = False
        
        # Check if roll should end
        if self.is_rolling and pygame.time.get_ticks() - self.roll_timer >= self.roll_duration:
            self.end_roll()
        
        # Update animations
        self.update_animations(dt)
        
        # Background scrolling
        self.bg_scroll_x = (self.bg_scroll_x - self.bg_speed) % WIDTH
        
        # Update score timer
        self.score_timer += dt
    
    def update_animations(self, dt):
        # Player animation
        if self.is_rolling:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.game.player_roll_frames)
        elif self.is_attacking:
            self.attack_animation_timer += dt
            if self.attack_animation_timer >= self.attack_animation_speed:
                self.attack_animation_timer = 0
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.game.player_attack_frames):
                    self.attack_frame_index = 0
                    self.is_attacking = False
                else:
                    # Update attack hitbox
                    self.attack_hitbox = pygame.Rect(
                        self.rect.right - 20, 
                        self.rect.top + 20, 
                        60, 
                        self.rect.height - 40)
        else:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.game.player_frames)
    
    def start_roll(self):
        # Bisa roll baik di tanah maupun di udara
        if not self.is_rolling and not self.is_attacking:
            self.is_rolling = True
            self.is_attacking = False  # Pastikan tidak dalam keadaan attack
            self.roll_timer = pygame.time.get_ticks()
            # Simpan posisi bawah sebelum mengubah ukuran
            bottom = self.rect.bottom
            self.rect.height = 32
            self.rect.bottom = bottom  # Pertahankan posisi bawah
    
    def end_roll(self):
        self.is_rolling = False
        self.rect.height = 64  # Kembalikan ke tinggi normal
        # Hitung posisi bawah yang baru berdasarkan posisi saat ini
        new_bottom = self.rect.bottom
        self.rect.bottom = new_bottom  # Pertahankan posisi bawah saat ini
        
        # Jika posisi bawah melebihi ground level, set ke ground level
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0

    def jump(self):
        if self.rect.bottom >= self.ground_level:
            self.speed_y = self.jump_power
            self.has_jumped_once = False
        elif self.game.powerup_manager.dj_active and not self.has_jumped_once:
            self.speed_y = self.jump_power
            self.has_jumped_once = True
    
    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            # Jika sedang roll, batalkan roll
            if self.is_rolling:
                self.end_roll()
            
            self.is_attacking = True
            self.is_rolling = False  # Pastikan tidak dalam keadaan roll
            self.attack_frame_index = 0
            self.last_attack_time = current_time
            self.attack_hitbox = pygame.Rect(
                self.rect.right - 20, 
                self.rect.top + 20, 
                60, 
                self.rect.height - 40
            )
    
    def draw(self, screen):
        if self.is_attacking:
            screen.blit(self.game.player_attack_frames[self.attack_frame_index], self.rect)
        elif self.is_rolling:
            screen.blit(self.game.player_roll_frames[self.frame_index], self.rect)
        else:
            screen.blit(self.game.player_frames[self.frame_index], self.rect)

class ObstacleManager:
    def __init__(self, game):
        self.game = game
        self.obstacles = []
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_interval = 1500
        self.obstacle_speed = 4
    
    def reset(self):
        self.obstacles.clear()
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_interval = 1500
    
    def update(self, dt):
        self.obstacle_spawn_timer += dt
        
        # Spawn new obstacles
        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            if random.random() < 0.5:
                # Normal ground obstacle
                rect = self.game.obstacle_img.get_rect(bottom=self.game.player.ground_level, left=WIDTH + random.randint(0, 100))
                self.obstacles.append((rect, "normal"))
            elif random.random() < 0.3:
                # Arrow obstacle in air
                arrow_y = self.game.player.ground_level - random.choice([60, 80])
                rect = self.game.obstacle_arrow_img.get_rect(left=WIDTH + random.randint(0, 100), top=arrow_y)
                self.obstacles.append((rect, "arrow"))
            elif random.random() < 0.2:
                # Enemy obstacle
                rect = pygame.Rect(
                    WIDTH + random.randint(0, 100), 
                    self.game.player.ground_level - 64, 
                    self.game.enemy_frames[0].get_width(), 
                    self.game.enemy_frames[0].get_height()
                )
                self.obstacles.append((rect, "enemy"))
            
            self.obstacle_spawn_timer = 0
            self.obstacle_spawn_interval = max(800, self.obstacle_spawn_interval - 10)
        
        # Update obstacles
        for obstacle, o_type in self.obstacles[:]:
            obstacle.x -= self.obstacle_speed
            
            # Remove off-screen obstacles
            if obstacle.right < 0:
                self.obstacles.remove((obstacle, o_type))
                continue
            
            # Check attack collisions with enemies
            if self.game.player.is_attacking and self.game.player.attack_hitbox and o_type == "enemy":
                if self.game.player.attack_hitbox.colliderect(obstacle):
                    self.obstacles.remove((obstacle, o_type))
                    self.game.player.score += 50
    
    def draw(self, screen):
        for obstacle, o_type in self.obstacles:
            if o_type == "normal":
                screen.blit(self.game.obstacle_img, obstacle)
            elif o_type == "arrow":
                screen.blit(self.game.obstacle_arrow_img, obstacle)
            elif o_type == "enemy":
                screen.blit(self.game.enemy_frames[self.game.powerup_manager.enemy_frame_index], obstacle)

class CoinManager:
    def __init__(self, game):
        self.game = game
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_spawn_interval = 1500
        self.coin_frame_index = 0
        self.coin_animation_timer = 0
        self.coin_animation_speed = 100
        self.coin_size = 16  # Ukuran coin yang ditampilkan di game
    
    def reset(self):
        self.coins.clear()
        self.coin_spawn_timer = 0
    
    def update(self, dt):
        self.coin_spawn_timer += dt
        self.coin_animation_timer += dt
        
        # Spawn new coins
        if self.coin_spawn_timer >= self.coin_spawn_interval:
            rect = pygame.Rect(
                WIDTH + random.randint(0, 100),
                self.game.player.ground_level - random.randint(40, 80),
                16,  # Lebar coin
                16   # Tinggi coin
            )
            self.coins.append(rect)
            self.coin_spawn_timer = 0
        
        # Update coin animation
        if self.coin_animation_timer >= self.coin_animation_speed:
            self.coin_animation_timer = 0
            self.coin_frame_index = (self.coin_frame_index + 1) % len(self.game.coin_frames)
        
        # Update coin positions
        for coin in self.coins[:]:
            coin.x -= self.game.obstacle_manager.obstacle_speed
            
            # Remove off-screen coins
            if coin.right < 0:
                self.coins.remove(coin)
                continue
    
    def draw(self, screen):
        for coin in self.coins:
            # Scale frame ke ukuran yang diinginkan
            frame = pygame.transform.scale(
                self.game.coin_frames[self.coin_frame_index],
                (coin.width, coin.height)
            )
            screen.blit(frame, coin)

class PowerupManager:
    def __init__(self, game):
        self.game = game
        self.reset()
        
        # Animation
        self.animation_speed = 100  # Kecepatan animasi yang sama untuk semua powerup
        self.dj_frame_index = 0
        self.dj_animation_timer = 0
        self.dj_animation_speed = 100
        
        self.shield_frame_index = 0
        self.shield_animation_timer = 0
        self.shield_animation_speed = 100
        
        self.multiplier_frame_index = 0
        self.multiplier_animation_timer = 0
        self.multiplier_animation_speed = 100
        
        self.enemy_frame_index = 0
        self.enemy_animation_timer = 0
        self.enemy_animation_speed = 150
    
    def reset(self):
        # Powerups
        self.double_jumps = []
        self.shields = []
        self.multipliers = []
        
        # Spawn timers
        self.dj_spawn_timer = 0
        self.dj_spawn_interval = 7000
        self.shield_spawn_timer = 0
        self.shield_spawn_interval = 10000
        self.multiplier_spawn_timer = 0
        self.multiplier_spawn_interval = 12000
        
        # Active powerups
        self.dj_active = False
        self.dj_timer = 0
        self.dj_duration = 30000
        
        self.shield_active = False
        self.shield_hits = 0
        self.max_shield_hits = 2
        
        self.multiplier_active = False
        self.multiplier_timer = 0
        self.multiplier_duration = 10000
        self.multiplier_value = 1
    
    def update(self, dt):
        # Update animations
        self.update_animations(dt)
        
        # Spawn powerups
        self.spawn_powerups(dt)
        
        # Update active powerups
        self.update_active_powerups()
    
    def update_animations(self, dt):

        # Double jump animation
        self.dj_animation_timer += dt
        if self.dj_animation_timer >= self.dj_animation_speed:
            self.dj_animation_timer = 0
            self.dj_frame_index = (self.dj_frame_index + 1) % len(self.game.dj_frames)
        
        # Shield animation
        self.shield_animation_timer += dt
        if self.shield_animation_timer >= self.shield_animation_speed:
            self.shield_animation_timer = 0
            self.shield_frame_index = (self.shield_frame_index + 1) % len(self.game.shield_frames)
        
        # Multiplier animation
        self.multiplier_animation_timer += dt
        if self.multiplier_animation_timer >= self.multiplier_animation_speed:
            self.multiplier_animation_timer = 0
            self.multiplier_frame_index = (self.multiplier_frame_index + 1) % len(self.game.multiplier_frames)
        
        # Enemy animation
        self.enemy_animation_timer += dt
        if self.enemy_animation_timer >= self.enemy_animation_speed:
            self.enemy_animation_timer = 0
            self.enemy_frame_index = (self.enemy_frame_index + 1) % len(self.game.enemy_frames)
    
    def spawn_powerups(self, dt):
        # Spawn double jump
        if not self.dj_active:
            self.dj_spawn_timer += dt
            if self.dj_spawn_timer >= self.dj_spawn_interval:
                rect = pygame.Rect(
                    WIDTH + random.randint(0, 100), 
                    self.game.player.ground_level - random.randint(40, 80), 
                    self.game.dj_frames[0].get_width(), 
                    self.game.dj_frames[0].get_height()
                )
                self.double_jumps.append(rect)
                self.dj_spawn_timer = 0
        
        # Spawn shield
        if not self.shield_active:
            self.shield_spawn_timer += dt
            if self.shield_spawn_timer >= self.shield_spawn_interval:
                rect = pygame.Rect(
                    WIDTH + random.randint(0, 100), 
                    self.game.player.ground_level - random.randint(40, 80), 
                    self.game.shield_frames[0].get_width(), 
                    self.game.shield_frames[0].get_height()
                )
                self.shields.append(rect)
                self.shield_spawn_timer = 0
        
        # Spawn multiplier
        if not self.multiplier_active:
            self.multiplier_spawn_timer += dt
            if self.multiplier_spawn_timer >= self.multiplier_spawn_interval:
                rect = pygame.Rect(
                    WIDTH + random.randint(0, 100), 
                    self.game.player.ground_level - random.randint(40, 80), 
                    self.game.multiplier_frames[0].get_width(), 
                    self.game.multiplier_frames[0].get_height()
                )
                self.multipliers.append(rect)
                self.multiplier_spawn_timer = 0
        
        # Update powerup positions and check collisions
        self.update_powerups()
    
    def update_powerups(self):
        # Double jumps
        for dj in self.double_jumps[:]:
            dj.x -= self.game.obstacle_manager.obstacle_speed
            
            if dj.right < 0:
                self.double_jumps.remove(dj)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(dj):
                self.double_jumps.remove(dj)
                self.dj_active = True
                self.dj_timer = pygame.time.get_ticks()
                self.game.play_collectible_sound()  # Play sound when collecting double jump
        
        # Shields
        for shield in self.shields[:]:
            shield.x -= self.game.obstacle_manager.obstacle_speed
            
            if shield.right < 0:
                self.shields.remove(shield)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(shield):
                self.shields.remove(shield)
                self.shield_active = True
                self.shield_hits = 0
                self.game.play_collectible_sound()  # Play sound when collecting double jump
        
        # Multipliers
        for multiplier in self.multipliers[:]:
            multiplier.x -= self.game.obstacle_manager.obstacle_speed
            
            if multiplier.right < 0:
                self.multipliers.remove(multiplier)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(multiplier):
                self.multipliers.remove(multiplier)
                self.multiplier_active = True
                self.multiplier_timer = pygame.time.get_ticks()
                self.multiplier_value = 2
                self.game.play_collectible_sound()  # Play sound when collecting double jump
    
    def update_active_powerups(self):
        # Double jump
        if self.dj_active:
            elapsed = pygame.time.get_ticks() - self.dj_timer
            if elapsed >= self.dj_duration:
                self.dj_active = False
        
        # Multiplier
        if self.multiplier_active:
            elapsed = pygame.time.get_ticks() - self.multiplier_timer
            if elapsed >= self.multiplier_duration:
                self.multiplier_active = False
                self.multiplier_value = 1
    
    def draw(self, screen):
        # Draw double jumps
        for dj in self.double_jumps:
            frame = pygame.transform.scale(
                self.game.dj_frames[self.dj_frame_index],
                (32, 32)  # Ukuran konsisten
            )
            screen.blit(frame, dj)
        
        # Draw shields
        for shield in self.shields:
            frame = pygame.transform.scale(
                self.game.shield_frames[self.shield_frame_index],
                (32, 32)
            )
            screen.blit(frame, shield)
        
        # Draw multipliers
        for multiplier in self.multipliers:
            frame = pygame.transform.scale(
                self.game.multiplier_frames[self.multiplier_frame_index],
                (32, 32)
            )
            screen.blit(frame, multiplier)

if __name__ == "__main__":
    game = Game()
    game.run()
