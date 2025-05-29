import pygame
import random

class coinmanager:
    def __init__(self, game):
        self.game = game
        self.reset()
        self._load_assets()
    
    def _load_assets(self):
        self.coin_frames = self._load_frames(
            pygame.image.load("assets/coin.png").convert_alpha(),
            240, 16, 15
        )
        self.coin_size = 16
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_spawn_interval = 1500
        self.coin_frame_index = 0
        self.coin_animation_timer = 0
        self.coin_animation_speed = 100
    
    def update(self, dt):
        self.coin_spawn_timer += dt
        self.coin_animation_timer += dt
        
        if self.coin_spawn_timer >= self.coin_spawn_interval:
            self._spawn_coin()
            self.coin_spawn_timer = 0
        
        if self.coin_animation_timer >= self.coin_animation_speed:
            self.coin_animation_timer = 0
            self.coin_frame_index = (self.coin_frame_index + 1) % len(self.coin_frames)
        
        self._update_coins()
    
    def _spawn_coin(self):
        rect = pygame.Rect(
            self.game.WIDTH + random.randint(0, 100),
            self.game.player.ground_level - random.randint(40, 80),
            self.coin_size,
            self.coin_size
        )
        self.coins.append(rect)
    
    def _update_coins(self):
        for coin in self.coins[:]:
            coin.x -= self.game.obstacle_manager.obstacle_speed
            
            if coin.right < 0:
                self.coins.remove(coin)
                continue
    
    def draw(self, screen):
        for coin in self.coins:
            frame = pygame.transform.scale(
                self.coin_frames[self.coin_frame_index],
                (coin.width, coin.height)
            )
            screen.blit(frame, coin)