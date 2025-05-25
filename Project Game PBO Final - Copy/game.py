import pygame
import sys
import json
import os
from player import Player
from obstacle_manager import ObstacleManager
from coin_manager import coinmanager
from powerup_manager import PowerupManager

class Game:
    # Class constants
    DEBUG_HITBOX = True
    WIDTH, HEIGHT = 620, 360
    SAVE_FILE = "save_data.json"
    MENU, GAMEPLAY, SHOP, SETTING = 0, 1, 2, 3

    def __init__(self):
        self._initialize_pygame()
        self._setup_game_components()
        self._setup_constants()
        self._initialize_game_components()
        self._load_assets()
        self._setup_buttons()
        self._load_save_data()
        self.load_sounds()  
        self._setup_settings()
        self.play_menu_music()

    def _initialize_pygame(self):
        pygame.init()
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Runner Saga")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

    def _setup_game_components(self):
        """Initialize all game components"""
        self.game_state = self.MENU
        self.running = True
        
        # Initialize game objects
        self.player = Player(self)
        self.obstacle_manager = ObstacleManager(self)
        self.coin_manager = coinmanager(self)
        self.powerup_manager = PowerupManager(self)
        
        # Load sounds and settings
        self.load_sounds()
        self._setup_settings()

    def _setup_constants(self):
        self.WIDTH, self.HEIGHT = 620, 360
        self.SAVE_FILE = "save_data.json"
        self.MENU, self.GAMEPLAY, self.SHOP, self.SETTING = 0, 1, 2, 3
        self.DEBUG_HITBOX = True
        
    def _initialize_game_components(self):
        self.game_state = self.MENU
        self.running = True
        self._initialize_sound_system()
        self._setup_settings()
        
        self.player = Player(self)
        self.obstacle_manager = ObstacleManager(self)
        self.coin_manager = coinmanager(self)
        self.powerup_manager = PowerupManager(self)
        
    def _initialize_sound_system(self):
        pygame.mixer.init()
        self.sounds = {}
        
    def _setup_settings(self):
        self.settings = {
            "music_enabled": True,
            "sound_effects_enabled": True,
            "hitbox_visible": self.DEBUG_HITBOX
        }
        
    def _load_assets(self):
        try:
            self.bg_img = pygame.image.load("assets/menu_start.png").convert()
            self.start_img = pygame.image.load("assets/start.png").convert_alpha()
            self.shop_img = pygame.image.load("assets/shop.png").convert_alpha()
            self.setting_img = pygame.image.load("assets/setting.png").convert_alpha()
            self.reset_img = pygame.image.load("assets/reset.png").convert_alpha()
        except Exception as e:
            print(f"Failed to load assets: {e}")
            pygame.quit()
            sys.exit()
            
    def _setup_buttons(self):
        self.start_button_rect = self.start_img.get_rect(center=(self.WIDTH // 2, 140))
        self.shop_rect = self.shop_img.get_rect(center=(self.WIDTH // 2, 180))
        self.setting_rect = self.setting_img.get_rect(center=(self.WIDTH // 2, 220))
        self.reset_rect = self.reset_img.get_rect(center=(self.WIDTH // 2, 270))
        
    def _load_save_data(self):
        self.save_data = {"high_score": 0, "total_coin": 0}
        self.shop_items = {
            "shield": {"level": 1, "price": 100, "max_level": 5},
            "double_jump": {"level": 1, "price": 150, "max_level": 3},
            "multiplier": {"level": 1, "price": 200, "max_level": 3}
        }
        
        if os.path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r") as f:
                data = json.load(f)
                self.save_data.update(data)
                if "shop_items" in data:
                    self.shop_items.update(data["shop_items"])
    
    def load_sounds(self):
        self.sounds = {}
        try:
            sound_files = {
                'menu_music': 'assets/sound_menu.wav',
                'gameplay_music': 'assets/sound_gameplay.wav',
                'collectible': 'assets/sound_collectible.wav'
            }
            
            for name, path in sound_files.items():
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.7)
                else:
                    print(f"Warning: Sound file {path} not found!")
                    # Create silent sound as fallback
                    self.sounds[name] = pygame.mixer.Sound(buffer=bytearray(1000))
        except Exception as e:
            print(f"Critical sound error: {str(e)}")

        except Exception as e:
            print(f"Error loading sounds: {e}")
            # Fallback jika file tidak ada
            self.sounds = {
                'menu_music': None,
                'gameplay_music': None,
                'collectible': None
            }

    def save_game(self):
        self.save_data["shop_items"] = self.shop_items
        with open(self.SAVE_FILE, "w") as f:
            json.dump(self.save_data, f)
    
    def reset_data(self):
        self.save_data = {"high_score": 0, "total_coin": 0}
        self.shop_items = {
            "shield": {"level": 1, "price": 100, "max_level": 5},
            "double_jump": {"level": 1, "price": 150, "max_level": 3},
            "multiplier": {"level": 1, "price": 200, "max_level": 3}
        }
        self.save_game()
    
    def reset_audio(self):
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.load_sounds()
        if self.settings["music_enabled"]:
            self.play_menu_music()

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
        
        self.powerup_manager.shield_spawn_interval = max(3000, 10000 - (self.shop_items["shield"]["level"] * 1500))
        self.powerup_manager.dj_spawn_interval = max(5000, 15000 - (self.shop_items["double_jump"]["level"] * 3000))
        self.powerup_manager.multiplier_spawn_interval = max(8000, 15000 - (self.shop_items["multiplier"]["level"] * 2000))
    
    def check_collisions(self):
        # Update untuk obstacle berbasis class
        for obstacle in self.obstacle_manager.obstacles[:]:
            if self.player.rect.inflate(-80, -30).colliderect(obstacle.rect):
                if self.powerup_manager.shield_active:
                    self.obstacle_manager.obstacles.remove(obstacle)
                    self.powerup_manager.shield_hits += 1
                    if self.powerup_manager.shield_hits >= self.powerup_manager.max_shield_hits:
                        self.powerup_manager.shield_active = False
                    continue
                else:
                    self.game_over()
                    break
        
        # Update untuk coin collision
        for coin in self.coin_manager.coins[:]:
            if self.player.rect.inflate(-80, -30).colliderect(coin):
                self.coin_manager.coins.remove(coin)
                self.player.coin_score += 1
                self.play_collectible_sound()
    
    def game_over(self):
        if self.player.score > self.save_data["high_score"]:
            self.save_data["high_score"] = self.player.score
        self.save_data["total_coin"] += self.player.coin_score
        self.save_game()
        self.game_state = self.MENU
        self.play_menu_music()
    
    def update(self, dt):
        if self.game_state == self.GAMEPLAY:
            self.player.update(dt)
            self.obstacle_manager.update(dt)
            self.coin_manager.update(dt)
            self.powerup_manager.update(dt)
            self.check_collisions()
            
            if self.player.score_timer >= self.player.score_interval:
                self.player.score_timer = 0
                self.player.score += self.powerup_manager.multiplier_value
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.game_state == self.MENU:
                self._handle_menu_events(event)
            elif self.game_state == self.GAMEPLAY:
                self._handle_gameplay_events(event)
            elif self.game_state == self.SHOP:
                self._handle_shop_events(event)
            elif self.game_state == self.SETTING:
                self._handle_settings_events(event)
    
    def _handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.start_button_rect.collidepoint(mouse_pos):
                self.game_state = self.GAMEPLAY
                self.play_gameplay_music()
                self.reset_game()
            elif self.shop_rect.collidepoint(mouse_pos):
                self.game_state = self.SHOP
            elif self.setting_rect.collidepoint(mouse_pos):
                self.game_state = self.SETTING
            elif self.reset_rect.collidepoint(mouse_pos):
                self.reset_data()
    
    def _handle_gameplay_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.player.start_roll()
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                self.player.jump()
            elif event.key == pygame.K_s:
                self.player.attack()
            elif event.key == pygame.K_ESCAPE:
                self.game_state = self.MENU
                self.play_menu_music()
            elif event.key == pygame.K_q:
                self.settings["hitbox_visible"] = not self.settings["hitbox_visible"]
    
    def _handle_shop_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            back_btn, buy_buttons = self.draw_shop()
            
            if back_btn.collidepoint(mouse_pos):
                self.game_state = self.MENU
            else:
                for item, btn_rect in buy_buttons:
                    if btn_rect.collidepoint(mouse_pos):
                        self.buy_item(item)
                        self.play_collectible_sound()
                        break

    def _handle_settings_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            back_btn, music_btn, sfx_btn = self.draw_settings()
            
            if back_btn.collidepoint(mouse_pos):
                self.game_state = self.MENU
            elif music_btn.collidepoint(mouse_pos):
                self.toggle_music()
            elif sfx_btn.collidepoint(mouse_pos):
                self.toggle_sound_effects()
    
    def buy_item(self, item):
        if self.save_data['total_coin'] >= self.shop_items[item]['price']:
            self.save_data['total_coin'] -= self.shop_items[item]['price']
            self.shop_items[item]['level'] += 1
            self.shop_items[item]['price'] = int(self.shop_items[item]['price'] * 1.5)
            self.save_game()
            
            self.draw_shop()
            pygame.display.flip()
            pygame.time.delay(100)
    
    def toggle_music(self):
        self.settings["music_enabled"] = not self.settings["music_enabled"]

        if self.settings["music_enabled"]:
            if self.game_state == self.MENU:
                self.play_menu_music()
            elif self.game_state == self.GAMEPLAY:
                self.play_gameplay_music()
        else:
            pygame.mixer.stop()

    def toggle_sound_effects(self):
        self.settings["sound_effects_enabled"] = not self.settings["sound_effects_enabled"]
    
    def play_menu_music(self):
        if not self.settings["music_enabled"]:
            return
        
        try:
            if hasattr(self, 'sounds') and 'menu_music' in self.sounds:
                pygame.mixer.stop()
                self.sounds['menu_music'].set_volume(0.7)
                self.sounds['menu_music'].play(loops=-1, fade_ms=1500)
                print("Menu music started successfully")  # Debug
            else:
                print("Menu sound not loaded!")  # Debug
        except Exception as e:
            print(f"Error playing menu music: {str(e)}")

    def play_gameplay_music(self):
        if not self.settings["music_enabled"]:
            return
        pygame.mixer.stop()
        self.sounds['gameplay_music'].play(-1)
    
    def play_collectible_sound(self):
        if not self.settings["sound_effects_enabled"]:
            return
        self.sounds['collectible'].play()
    
    def draw_shop(self):
        self.screen.blit(self.bg_img, (0, 0))
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        coins_text = self.font.render(f"Coins: {self.save_data['total_coin']}", True, (255, 255, 0))
        self.screen.blit(coins_text, (self.WIDTH - 150, 20))
        
        title = self.font.render("SHOP", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))
        
        back_btn = pygame.Rect(20, 20, 80, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), back_btn)
        self.screen.blit(self.font.render("Back", True, (255, 255, 255)), (back_btn.x + 20, back_btn.y + 10))
        
        buttons = []
        y_pos = 100
        
        for item, data in self.shop_items.items():
            img = None
            if item == "shield":
                img = self.powerup_manager.shield_frames[0]
            elif item == "double_jump":
                img = self.powerup_manager.dj_frames[0]
            else:
                img = self.powerup_manager.multiplier_frames[0]
            
            img = pygame.transform.scale(img, (50, 50))
            self.screen.blit(img, (50, y_pos))
            
            self.screen.blit(self.font.render(f"{item.replace('_', ' ').title()}", True, (255, 255, 255)), (120, y_pos))
            self.screen.blit(self.font.render(f"Lvl: {data['level']}/{data['max_level']}", True, (200, 200, 200)), (120, y_pos + 25))
            
            if data['level'] < data['max_level']:
                btn_rect = pygame.Rect(self.WIDTH - 150, y_pos + 10, 120, 40)
                btn_color = (50, 200, 50) if self.save_data['total_coin'] >= data['price'] else (100, 100, 100)
                pygame.draw.rect(self.screen, btn_color, btn_rect)
                self.screen.blit(self.font.render(f"Buy: {data['price']}", True, (255, 255, 255)), (self.WIDTH - 140, y_pos + 20))
                buttons.append((item, btn_rect))
            
            y_pos += 80
        
        return back_btn, buttons
    
    def draw_settings(self):
        self.screen.blit(self.bg_img, (0, 0))
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("SETTINGS", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))
        
        back_btn = pygame.Rect(20, 20, 90, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), back_btn)
        self.screen.blit(self.font.render("Back", True, (255, 255, 255)), (back_btn.x + 15, back_btn.y + 10))

        music_btn = pygame.Rect(self.WIDTH//2 - 100, 120, 260, 50)
        btn_color = (50, 200, 50) if self.settings["music_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.screen, btn_color, music_btn)
        status = "ON" if self.settings["music_enabled"] else "OFF"
        self.screen.blit(self.font.render(f"Music:            {status}", True, (255, 255, 255)), 
                        (music_btn.x + 50, music_btn.y + 15))
        
        sfx_btn = pygame.Rect(self.WIDTH//2 - 100, 190, 260, 50)
        btn_color = (50, 200, 50) if self.settings["sound_effects_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.screen, btn_color, sfx_btn)
        status = "ON" if self.settings["sound_effects_enabled"] else "OFF"
        self.screen.blit(self.font.render(f"Sound Effects: {status}", True, (255, 255, 255)), 
                        (sfx_btn.x + 30, sfx_btn.y + 15))
        
        hitbox_text = self.font.render("Press Q in-game to toggle hitboxes", True, (255, 255, 255))
        self.screen.blit(hitbox_text, (self.WIDTH//2 - hitbox_text.get_width()//2, 260))
        
        return back_btn, music_btn, sfx_btn
    
    def render(self):
        if self.game_state == self.MENU:
            self._render_menu()
        elif self.game_state == self.SHOP:
            self.draw_shop()
        elif self.game_state == self.SETTING:
            self.draw_settings()
        elif self.game_state == self.GAMEPLAY:
            self._render_gameplay()
        
        pygame.display.flip()
    
    def _render_menu(self):
        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.start_img, self.start_button_rect)
        self.screen.blit(self.shop_img, self.shop_rect)
        self.screen.blit(self.setting_img, self.setting_rect)
        self.screen.blit(self.reset_img, self.reset_rect)
        
        self.screen.blit(
            self.font.render(f"High Score: {int(self.save_data['high_score'])}", True, (255, 255, 255)), 
            (10, 10)
        )
        self.screen.blit(
            self.font.render(f"Total Coins: {self.save_data['total_coin']}", True, (255, 255, 0)), 
            (10, 40)
        )
    
    def _render_gameplay(self):
        self.screen.blit(self.bg_img, (self.player.bg_scroll_x - self.WIDTH, 0))
        self.screen.blit(self.bg_img, (self.player.bg_scroll_x, 0))
        
        self.obstacle_manager.draw(self.screen)
        self.coin_manager.draw(self.screen)
        self.powerup_manager.draw(self.screen)
        self.player.draw(self.screen)
        
        self.screen.blit(
            self.font.render(f"Score: {int(self.player.score)}", True, (255, 255, 255)), 
            (10, 10)
        )
        self.screen.blit(
            self.font.render(f"Coins: {self.player.coin_score}", True, (255, 255, 0)), 
            (10, 40)
        )
        
        if self.powerup_manager.dj_active:
            elapsed = pygame.time.get_ticks() - self.powerup_manager.dj_timer
            self.screen.blit(
                self.font.render(f"Double Jump: {(self.powerup_manager.dj_duration - elapsed)//1000}s", True, (0, 255, 0)), 
                (self.WIDTH - 220, 10)
            )
        
        if self.powerup_manager.shield_active:
            self.screen.blit(
                self.font.render(f"Shield: {self.powerup_manager.max_shield_hits - self.powerup_manager.shield_hits} hits", True, (128, 128, 255)), 
                (self.WIDTH - 220, 40)
            )
        
        if self.powerup_manager.multiplier_active:
            elapsed = pygame.time.get_ticks() - self.powerup_manager.multiplier_timer
            self.screen.blit(
                self.font.render(f"Multiplier: {(self.powerup_manager.multiplier_duration - elapsed)//1000}s", True, (255, 215, 0)), 
                (self.WIDTH - 220, 70)
            )
        
        if self.settings["hitbox_visible"]:
            pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect.inflate(-80, -30), 2)
            for c in self.coin_manager.coins:
                pygame.draw.rect(self.screen, (255, 255, 0), c, 2)
            # Update untuk obstacle berbasis class
            for obstacle in self.obstacle_manager.obstacles:
                color = (255, 255, 255) if obstacle.type == "arrow" else (0, 0, 255)
            for dj in self.powerup_manager.double_jumps:
                pygame.draw.rect(self.screen, (0, 255, 0), dj, 2)
            for s in self.powerup_manager.shields:
                pygame.draw.rect(self.screen, (0, 0, 255), s, 2)
            for m in self.powerup_manager.multipliers:
                pygame.draw.rect(self.screen, (255, 165, 0), m, 2)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()