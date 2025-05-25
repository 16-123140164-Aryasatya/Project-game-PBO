import pygame
import random
from abc import ABC, abstractmethod

class GameObjectManager(ABC):
    def __init__(self, game):
        self.game = game
        self.objects = []
        self.spawn_timer = 0
        self.spawn_interval = 1500
        self.speed = 4
    
    @abstractmethod
    def _load_assets(self):
        pass
    
    @abstractmethod
    def _spawn(self):
        pass
    
    def reset(self):
        self.objects = []
        self.spawn_timer = 0
        self.spawn_interval = 1500
    
    def update(self, dt):
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.spawn_interval:
            self._spawn()
            self.spawn_timer = 0
            self.spawn_interval = max(800, self.spawn_interval - 10)
        
        self._update_objects()
    
    def _update_objects(self):
        for obj in self.objects[:]:
            obj[0].x -= self.speed
            
            if obj[0].right < 0:
                self.objects.remove(obj)
                continue
    
    @abstractmethod
    def draw(self, screen):
        pass

class ObstacleManager(GameObjectManager):
    def __init__(self, game):
        super().__init__(game)
        self._load_assets()
        self.reset()
    
    def _load_assets(self):
        self.obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
        self.obstacle_arrow_img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
        enemy_img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
        self.enemy_frames = self._load_frames(enemy_img, 135, 64, 4)
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def _spawn(self):
        rand = random.random()
        if rand < 0.5:
            rect = self.obstacle_img.get_rect(
                bottom=self.game.player.ground_level, 
                left=self.game.WIDTH + random.randint(0, 100))
            self.objects.append((rect, "normal"))
        elif rand < 0.8:
            arrow_y = self.game.player.ground_level - random.choice([60, 80])
            rect = self.obstacle_arrow_img.get_rect(
                left=self.game.WIDTH + random.randint(0, 100), 
                top=arrow_y)
            self.objects.append((rect, "arrow"))
        else:
            rect = pygame.Rect(
                self.game.WIDTH + random.randint(0, 100), 
                self.game.player.ground_level - 64, 
                self.enemy_frames[0].get_width(), 
                self.enemy_frames[0].get_height()
            )
            self.objects.append((rect, "enemy"))
    
    def _update_objects(self):
        super()._update_objects()
        for obstacle, o_type in self.objects[:]:
            self._check_attack_collision(obstacle, o_type)
    
    def _check_attack_collision(self, obstacle, o_type):
        if (self.game.player.is_attacking and 
            self.game.player.attack_hitbox and 
            o_type == "enemy" and 
            self.game.player.attack_hitbox.colliderect(obstacle)):
            
            self.objects.remove((obstacle, o_type))
            self.game.player.score += 50
    
    def draw(self, screen):
        for obstacle, o_type in self.objects:
            if o_type == "normal":
                screen.blit(self.obstacle_img, obstacle)
            elif o_type == "arrow":
                screen.blit(self.obstacle_arrow_img, obstacle)
            elif o_type == "enemy":
                screen.blit(self.enemy_frames[self.game.powerup_manager.enemy_frame_index], obstacle)