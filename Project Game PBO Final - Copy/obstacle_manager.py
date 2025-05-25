import pygame
import random
from abc import ABC, abstractmethod

class Obstacle(ABC):
    def __init__(self, game, rect):
        self.game = game
        self.rect = rect
        self.speed = 4
    
    def update(self):
        self.rect.x -= self.speed
        return self.rect.right < 0
    
    @abstractmethod
    def draw(self, screen):
        pass
    
    @property
    @abstractmethod
    def type(self):
        pass

class NormalObstacle(Obstacle):
    def __init__(self, game):
        img = pygame.image.load("assets/obstacle.png").convert_alpha()
        rect = img.get_rect(
            bottom=game.player.ground_level, 
            left=game.WIDTH + random.randint(0, 100))
        super().__init__(game, rect)
        self.image = img
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    @property
    def type(self):
        return "normal"

class ArrowObstacle(Obstacle):
    def __init__(self, game):
        img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
        arrow_y = game.player.ground_level - random.choice([60, 80])
        rect = img.get_rect(
            left=game.WIDTH + random.randint(0, 100), 
            top=arrow_y)
        super().__init__(game, rect)
        self.image = img
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    @property
    def type(self):
        return "arrow"

class EnemyObstacle(Obstacle):
    def __init__(self, game):
        img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
        frames = self._load_frames(img, 135, 64, 4)
        rect = pygame.Rect(
            game.WIDTH + random.randint(0, 100), 
            game.player.ground_level - 64, 
            frames[0].get_width(), 
            frames[0].get_height()
        )
        super().__init__(game, rect)
        self.frames = frames
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def draw(self, screen):
        screen.blit(self.frames[self.game.powerup_manager.enemy_frame_index], self.rect)
    
    @property
    def type(self):
        return "enemy"

class ObstacleManager:
    def __init__(self, game):
        self.game = game
        self.reset()
        self._load_assets()
    
    def _load_assets(self):
        self.obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
        self.obstacle_arrow_img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
        enemy_img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
        self.enemy_frames = self._load_frames(enemy_img, 135, 64, 4)
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        self.obstacles = []
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_interval = 1500
        self.obstacle_speed = 4
    
    def update(self, dt):
        self.obstacle_spawn_timer += dt
        
        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            self._spawn_obstacle()
            self.obstacle_spawn_timer = 0
            self.obstacle_spawn_interval = max(800, self.obstacle_spawn_interval - 10)
        
        self._update_obstacles()
    
    def _spawn_obstacle(self):
        rand = random.random()
        if rand < 0.5:
            self.obstacles.append(NormalObstacle(self.game))
        elif rand < 0.8:
            self.obstacles.append(ArrowObstacle(self.game))
        else:
            self.obstacles.append(EnemyObstacle(self.game))
    
    def _update_obstacles(self):
        for obstacle in self.obstacles[:]:
            should_remove = obstacle.update()
            
            if obstacle.type == "enemy" and self._check_attack_collision(obstacle):
                self.obstacles.remove(obstacle)
                self.game.player.score += 50
                continue
            
            if should_remove:
                self.obstacles.remove(obstacle)
    
    def _check_attack_collision(self, obstacle):
        return (self.game.player.is_attacking and 
                self.game.player.attack_hitbox and 
                self.game.player.attack_hitbox.colliderect(obstacle.rect))
    
    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen)