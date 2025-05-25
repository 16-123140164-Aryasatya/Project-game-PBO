import pygame
import random
from abc import ABC, abstractmethod

class Collectible(ABC):
    def __init__(self, game):
        self.game = game
        self.items = []
        self.spawn_timer = 0
        self.spawn_interval = 0
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
    
    @abstractmethod
    def _load_assets(self):
        pass
    
    @abstractmethod
    def _spawn(self):
        pass
    
    def reset(self):
        self.items = []
        self.spawn_timer = 0
        self.frame_index = 0
        self.animation_timer = 0
    
    def update(self, dt):
        self.spawn_timer += dt
        self.animation_timer += dt
        
        if self.spawn_timer >= self.spawn_interval:
            self._spawn()
            self.spawn_timer = 0
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        
        self._update_items()
    
    def _update_items(self):
        for item in self.items[:]:
            item.x -= self.game.obstacle_manager.obstacle_speed
            
            if item.right < 0:
                self.items.remove(item)
                continue
    
    @abstractmethod
    def draw(self, screen):
        pass

class CoinManager(Collectible):
    def __init__(self, game):
        super().__init__(game)
        self._load_assets()
        self.reset()
    
    def _load_assets(self):
        self.coin_frames = self._load_frames(
            pygame.image.load("assets/coin.png").convert_alpha(),
            240, 16, 15
        )
        self.size = 16
        self.spawn_interval = 1500
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def _spawn(self):
        rect = pygame.Rect(
            self.game.WIDTH + random.randint(0, 100),
            self.game.player.ground_level - random.randint(40, 80),
            self.size,
            self.size
        )
        self.items.append(rect)
    
    def draw(self, screen):
        for coin in self.items:
            frame = pygame.transform.scale(
                self.coin_frames[self.frame_index],
                (coin.width, coin.height)
            )
            screen.blit(frame, coin)