import pygame
import random
from abc import ABC, abstractmethod

class Obstacle(ABC):
    def __init__(self, game, rect):
        self._game = game
        self._rect = rect
        self._speed = 4
    
    def update(self):
        """Update obstacle position and return True if it should be removed"""
        self._rect.x -= self._speed
        return self._rect.right < 0
    
    @abstractmethod
    def draw(self, screen):
        """Draw the obstacle on the screen"""
        pass
    
    @property
    @abstractmethod
    def type(self):
        """Return the type of obstacle"""
        pass
    
    @property
    def rect(self):
        """Get the obstacle's rectangle (read-only)"""
        return self._rect
    
    @property
    def speed(self):
        """Get the obstacle's speed"""
        return self._speed
    
    @speed.setter
    def speed(self, value):
        """Set the obstacle's speed"""
        if value >= 0:
            self._speed = value
        else:
            raise ValueError("Speed cannot be negative")

class NormalObstacle(Obstacle):
    def __init__(self, game):
        self._image = pygame.image.load("assets/obstacle.png").convert_alpha()
        rect = self._image.get_rect(
            bottom=game.player.ground_level, 
            left=game.WIDTH + random.randint(0, 100))
        super().__init__(game, rect)
    
    def draw(self, screen):
        screen.blit(self._image, self.rect)
    
    @property
    def type(self):
        return "normal"
    
    @property
    def image(self):
        """Get the obstacle's image (read-only)"""
        return self._image

class ArrowObstacle(Obstacle):
    def __init__(self, game):
        self._image = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
        arrow_y = game.player.ground_level - random.choice([60, 80])
        rect = self._image.get_rect(
            left=game.WIDTH + random.randint(0, 100), 
            top=arrow_y)
        super().__init__(game, rect)
    
    def draw(self, screen):
        screen.blit(self._image, self.rect)
    
    @property
    def type(self):
        return "arrow"
    
    @property
    def image(self):
        """Get the obstacle's image (read-only)"""
        return self._image

class EnemyObstacle(Obstacle):
    def __init__(self, game):
        img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
        self._frames = self._load_frames(img, 135, 64, 4)
        rect = pygame.Rect(
            game.WIDTH + random.randint(0, 100), 
            game.player.ground_level - 64, 
            self._frames[0].get_width(), 
            self._frames[0].get_height()
        )
        super().__init__(game, rect)
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        """Private method to load animation frames"""
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def draw(self, screen):
        screen.blit(self._frames[self._game.powerup_manager.enemy_frame_index], self.rect)
    
    @property
    def type(self):
        return "enemy"
    
    @property
    def frames(self):
        """Get the enemy's animation frames (read-only)"""
        return self._frames

class ObstacleManager:
    def __init__(self, game):
        self._game = game
        self._obstacles = []
        self._obstacle_spawn_timer = 0
        self._obstacle_spawn_interval = 1500
        self._obstacle_speed = 4
        self._load_assets()
    
    def _load_assets(self):
        """Private method to load obstacle assets"""
        self._obstacle_img = pygame.image.load("assets/obstacle.png").convert_alpha()
        self._obstacle_arrow_img = pygame.image.load("assets/obstacle_arrow.png").convert_alpha()
        enemy_img = pygame.image.load("assets/obstacle_enemy.png").convert_alpha()
        self._enemy_frames = self._load_frames(enemy_img, 135, 64, 4)
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        """Private method to load animation frames"""
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        """Reset the obstacle manager to initial state"""
        self._obstacles = []
        self._obstacle_spawn_timer = 0
        self._obstacle_spawn_interval = 1500
        self._obstacle_speed = 4
    
    def update(self, dt):
        """Update obstacle spawning and movement"""
        self._obstacle_spawn_timer += dt
        
        if self._obstacle_spawn_timer >= self._obstacle_spawn_interval:
            self._spawn_obstacle()
            self._obstacle_spawn_timer = 0
            self._obstacle_spawn_interval = max(800, self._obstacle_spawn_interval - 10)
        
        self._update_obstacles()
    
    def _spawn_obstacle(self):
        """Private method to spawn a new obstacle"""
        rand = random.random()
        if rand < 0.5:
            self._obstacles.append(NormalObstacle(self._game))
        elif rand < 0.8:
            self._obstacles.append(ArrowObstacle(self._game))
        else:
            self._obstacles.append(EnemyObstacle(self._game))
    
    def _update_obstacles(self):
        """Private method to update all obstacles"""
        for obstacle in self._obstacles[:]:
            should_remove = obstacle.update()
            
            if obstacle.type == "enemy" and self._check_attack_collision(obstacle):
                self._obstacles.remove(obstacle)
                self._game.player.score += 50
                continue
            
            if should_remove:
                self._obstacles.remove(obstacle)
    
    def _check_attack_collision(self, obstacle):
        """Private method to check attack collision with enemy"""
        return (self._game.player.is_attacking and 
                self._game.player.attack_hitbox and 
                self._game.player.attack_hitbox.colliderect(obstacle.rect))
    
    def draw(self, screen):
        """Draw all obstacles on the screen"""
        for obstacle in self._obstacles:
            obstacle.draw(screen)
    
    @property
    def obstacles(self):
        """Get the list of obstacles (read-only)"""
        return self._obstacles
    
    @property
    def obstacle_speed(self):
        """Get the base obstacle speed"""
        return self._obstacle_speed
    
    @obstacle_speed.setter
    def obstacle_speed(self, value):
        """Set the base obstacle speed"""
        if value >= 0:
            self._obstacle_speed = value
            for obstacle in self._obstacles:
                obstacle.speed = value
        else:
            raise ValueError("Speed cannot be negative")