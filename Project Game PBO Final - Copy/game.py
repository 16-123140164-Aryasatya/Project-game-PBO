import pygame
import sys
import json
import os
from abc import ABC, abstractmethod
from player import Player
from obstacle_manager import ObstacleManager
from coin_manager import CoinManager
from powerup_manager import PowerupManager

class GameState(ABC):
    @abstractmethod
    def handle_events(self, event):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def render(self):
        pass

class MenuState(GameState):
    def __init__(self, game):
        self.game = game
        
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.game.start_button_rect.collidepoint(mouse_pos):
                self.game.change_state(GameplayState(self.game))
                self.game.play_gameplay_music()
                self.game.reset_game()
            elif self.game.shop_rect.collidepoint(mouse_pos):
                self.game.change_state(ShopState(self.game))
            elif self.game.setting_rect.collidepoint(mouse_pos):
                self.game.change_state(SettingState(self.game))
            elif self.game.reset_rect.collidepoint(mouse_pos):
                self.game.reset_data()
    
    def update(self, dt):
        pass
    
    def render(self):
        self.game.screen.blit(self.game.bg_img, (0, 0))
        self.game.screen.blit(self.game.start_img, self.game.start_button_rect)
        self.game.screen.blit(self.game.shop_img, self.game.shop_rect)
        self.game.screen.blit(self.game.setting_img, self.game.setting_rect)
        self.game.screen.blit(self.game.reset_img, self.game.reset_rect)
        
        self.game.screen.blit(
            self.game.font.render(f"High Score: {int(self.game.save_data['high_score'])}", True, (255, 255, 255)), 
            (10, 10)
        )
        self.game.screen.blit(
            self.game.font.render(f"Total Coins: {self.game.save_data['total_coin']}", True, (255, 255, 0)), 
            (10, 40)
        )

class GameplayState(GameState):
    def __init__(self, game):
        self.game = game
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.game.player.start_roll()
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                self.game.player.jump()
            elif event.key == pygame.K_s:
                self.game.player.attack()
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state(MenuState(self.game))
                self.game.play_menu_music()
            elif event.key == pygame.K_q:
                self.game.settings["hitbox_visible"] = not self.game.settings["hitbox_visible"]
    
    def update(self, dt):
        self.game.player.update(dt)
        self.game.obstacle_manager.update(dt)
        self.game.coin_manager.update(dt)
        self.game.powerup_manager.update(dt)
        self.game.check_collisions()
        
        if self.game.player.score_timer >= self.game.player.score_interval:
            self.game.player.score_timer = 0
            self.game.player.score += self.game.powerup_manager.multiplier_value
    
    def render(self):
        self.game._render_gameplay()

class ShopState(GameState):
    def __init__(self, game):
        self.game = game
        
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            back_btn, buy_buttons = self.draw_shop()
            
            if back_btn.collidepoint(mouse_pos):
                self.game.change_state(MenuState(self.game))
            else:
                for item, btn_rect in buy_buttons:
                    if btn_rect.collidepoint(mouse_pos):
                        self.game.buy_item(item)
                        self.game.play_collectible_sound()
                        break
    
    def update(self, dt):
        pass
    
    def render(self):
        self.draw_shop()
    
    def draw_shop(self):
        self.game.screen.blit(self.game.bg_img, (0, 0))
        overlay = pygame.Surface((self.game.WIDTH, self.game.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.game.screen.blit(overlay, (0, 0))
        
        coins_text = self.game.font.render(f"Coins: {self.game.save_data['total_coin']}", True, (255, 255, 0))
        self.game.screen.blit(coins_text, (self.game.WIDTH - 150, 20))
        
        title = self.game.font.render("SHOP", True, (255, 255, 255))
        self.game.screen.blit(title, (self.game.WIDTH//2 - title.get_width()//2, 50))
        
        back_btn = pygame.Rect(20, 20, 80, 40)
        pygame.draw.rect(self.game.screen, (200, 50, 50), back_btn)
        self.game.screen.blit(self.game.font.render("Back", True, (255, 255, 255)), (back_btn.x + 20, back_btn.y + 10))
        
        buttons = []
        y_pos = 100
        
        for item, data in self.game.shop_items.items():
            img = None
            if item == "shield":
                img = self.game.powerup_manager.shield_frames[0]
            elif item == "double_jump":
                img = self.game.powerup_manager.dj_frames[0]
            else:
                img = self.game.powerup_manager.multiplier_frames[0]
            
            img = pygame.transform.scale(img, (50, 50))
            self.game.screen.blit(img, (50, y_pos))
            
            self.game.screen.blit(self.game.font.render(f"{item.replace('_', ' ').title()}", True, (255, 255, 255)), (120, y_pos))
            self.game.screen.blit(self.game.font.render(f"Lvl: {data['level']}/{data['max_level']}", True, (200, 200, 200)), (120, y_pos + 25))
            
            if data['level'] < data['max_level']:
                btn_rect = pygame.Rect(self.game.WIDTH - 150, y_pos + 10, 120, 40)
                btn_color = (50, 200, 50) if self.game.save_data['total_coin'] >= data['price'] else (100, 100, 100)
                pygame.draw.rect(self.game.screen, btn_color, btn_rect)
                self.game.screen.blit(self.game.font.render(f"Buy: {data['price']}", True, (255, 255, 255)), (self.game.WIDTH - 140, y_pos + 20))
                buttons.append((item, btn_rect))
            
            y_pos += 80
        
        return back_btn, buttons

class SettingState(GameState):
    def __init__(self, game):
        self.game = game
        
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            back_btn, music_btn, sfx_btn = self.draw_settings()
            
            if back_btn.collidepoint(mouse_pos):
                self.game.change_state(MenuState(self.game))
            elif music_btn.collidepoint(mouse_pos):
                self.game.toggle_music()
            elif sfx_btn.collidepoint(mouse_pos):
                self.game.toggle_sound_effects()
    
    def update(self, dt):
        pass
    
    def render(self):
        self.draw_settings()
    
    def draw_settings(self):
        self.game.screen.blit(self.game.bg_img, (0, 0))
        overlay = pygame.Surface((self.game.WIDTH, self.game.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.game.screen.blit(overlay, (0, 0))
        
        title = self.game.font.render("SETTINGS", True, (255, 255, 255))
        self.game.screen.blit(title, (self.game.WIDTH//2 - title.get_width()//2, 50))
        
        back_btn = pygame.Rect(20, 20, 90, 40)
        pygame.draw.rect(self.game.screen, (200, 50, 50), back_btn)
        self.game.screen.blit(self.game.font.render("Back", True, (255, 255, 255)), (back_btn.x + 15, back_btn.y + 10))

        music_btn = pygame.Rect(self.game.WIDTH//2 - 100, 120, 260, 50)
        btn_color = (50, 200, 50) if self.game.settings["music_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.game.screen, btn_color, music_btn)
        status = "ON" if self.game.settings["music_enabled"] else "OFF"
        self.game.screen.blit(self.game.font.render(f"Music:            {status}", True, (255, 255, 255)), 
                        (music_btn.x + 50, music_btn.y + 15))
        
        sfx_btn = pygame.Rect(self.game.WIDTH//2 - 100, 190, 260, 50)
        btn_color = (50, 200, 50) if self.game.settings["sound_effects_enabled"] else (200, 50, 50)
        pygame.draw.rect(self.game.screen, btn_color, sfx_btn)
        status = "ON" if self.game.settings["sound_effects_enabled"] else "OFF"
        self.game.screen.blit(self.game.font.render(f"Sound Effects: {status}", True, (255, 255, 255)), 
                        (sfx_btn.x + 30, sfx_btn.y + 15))
        
        hitbox_text = self.game.font.render("Press Q in-game to toggle hitboxes", True, (255, 255, 255))
        self.game.screen.blit(hitbox_text, (self.game.WIDTH//2 - hitbox_text.get_width()//2, 260))
        
        return back_btn, music_btn, sfx_btn

class Game:
    # Class constants
    DEBUG_HITBOX = True
    WIDTH, HEIGHT = 620, 360
    SAVE_FILE = "save_data.json"

    def __init__(self):
        self._initialize_pygame()
        self._load_assets()
        self._setup_buttons()
        self._load_save_data()
        self.load_sounds()  
        self._setup_settings()
        
        # Initialize game objects
        self.player = Player(self)
        self.obstacle_manager = ObstacleManager(self)
        self.coin_manager = CoinManager(self)
        self.powerup_manager = PowerupManager(self)
        
        # Set initial state
        self.current_state = MenuState(self)
        self.running = True

    def change_state(self, new_state):
        self.current_state = new_state

    def _initialize_pygame(self):
        pygame.init()
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Runner Saga")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

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
    
    def _setup_settings(self):
        self.settings = {
            "music_enabled": True,
            "sound_effects_enabled": True,
            "hitbox_visible": self.DEBUG_HITBOX
        }

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
                    self.sounds[name] = pygame.mixer.Sound(buffer=bytearray(1000))
        except Exception as e:
            print(f"Error loading sounds: {e}")
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
        self.change_state(MenuState(self))
        self.play_menu_music()
    
    def toggle_music(self):
        self.settings["music_enabled"] = not self.settings["music_enabled"]
        if self.settings["music_enabled"]:
            if isinstance(self.current_state, MenuState):
                self.play_menu_music()
            elif isinstance(self.current_state, GameplayState):
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
    
    def buy_item(self, item):
        if self.save_data['total_coin'] >= self.shop_items[item]['price']:
            self.save_data['total_coin'] -= self.shop_items[item]['price']
            self.shop_items[item]['level'] += 1
            self.shop_items[item]['price'] = int(self.shop_items[item]['price'] * 1.5)
            self.save_game()
            self.apply_upgrades()
    
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
            for o, o_type in self.obstacle_manager.obstacles:
                color = (255, 255, 255) if o_type == "arrow" else (0, 0, 255)
                pygame.draw.rect(self.screen, color, o, 2)
            for dj in self.powerup_manager.double_jumps:
                pygame.draw.rect(self.screen, (0, 255, 0), dj, 2)
            for s in self.powerup_manager.shields:
                pygame.draw.rect(self.screen, (0, 0, 255), s, 2)
            for m in self.powerup_manager.multipliers:
                pygame.draw.rect(self.screen, (255, 165, 0), m, 2)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_state.handle_events(event)
            
            self.current_state.update(dt)
            self.current_state.render()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()