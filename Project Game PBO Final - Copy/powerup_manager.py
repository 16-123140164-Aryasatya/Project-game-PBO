import pygame
import random
from abc import ABC, abstractmethod

class Powerup(ABC):
    def __init__(self, game):
        self.game = game
        self.items = []
        self.spawn_timer = 0
        self.spawn_interval = 0
        self.active = False
        self.timer = 0
        self.duration = 0
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
    
    @abstractmethod
    def _load_frames(self):
        pass
    
    @abstractmethod
    def _spawn(self):
        pass
    
    @abstractmethod
    def activate(self):
        pass
    
    def reset(self):
        self.items = []
        self.spawn_timer = 0
        self.active = False
        self.timer = 0
        self.frame_index = 0
        self.animation_timer = 0
    
    def update(self, dt):
        if not self.active:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self._spawn()
                self.spawn_timer = 0
        
        self._update_animation(dt)
        self._update_items()
        self._update_active()
    
    def _update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    def _update_items(self):
        for item in self.items[:]:
            item.x -= self.game.obstacle_manager.obstacle_speed
            
            if item.right < 0:
                self.items.remove(item)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(item):
                self.items.remove(item)
                self.activate()
                self.game.play_collectible_sound()
    
    def _update_active(self):
        if self.active:
            elapsed = pygame.time.get_ticks() - self.timer
            if elapsed >= self.duration:
                self.active = False
    
    @abstractmethod
    def draw(self, screen):
        pass

class DoubleJumpPowerup(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self._load_frames()
        self.spawn_interval = 7000
        self.duration = 30000
    
    def _load_frames(self):
        self.frames = self._load_frames_from_sheet(
            pygame.image.load("assets/double_jump.png").convert_alpha(),
            128, 32, 4
        )
    
    def _load_frames_from_sheet(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def _spawn(self):
        rect = pygame.Rect(
            self.game.WIDTH + random.randint(0, 100), 
            self.game.player.ground_level - random.randint(40, 80), 
            self.frames[0].get_width(), 
            self.frames[0].get_height()
        )
        self.items.append(rect)
    
    def activate(self):
        self.active = True
        self.timer = pygame.time.get_ticks()
    
    def draw(self, screen):
        for dj in self.items:
            frame = pygame.transform.scale(
                self.frames[self.frame_index],
                (32, 32)
            )
            screen.blit(frame, dj)

class ShieldPowerup(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self._load_frames()
        self.spawn_interval = 10000
        self.max_hits = 2
        self.hits = 0
    
    def _load_frames(self):
        self.frames = self._load_frames_from_sheet(
            pygame.image.load("assets/shield.png").convert_alpha(),
            128, 32, 4
        )
    
    def _load_frames_from_sheet(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def _spawn(self):
        rect = pygame.Rect(
            self.game.WIDTH + random.randint(0, 100), 
            self.game.player.ground_level - random.randint(40, 80), 
            self.frames[0].get_width(), 
            self.frames[0].get_height()
        )
        self.items.append(rect)
    
    def activate(self):
        self.active = True
        self.hits = 0
    
    def draw(self, screen):
        for shield in self.items:
            frame = pygame.transform.scale(
                self.frames[self.frame_index],
                (32, 32)
            )
            screen.blit(frame, shield)

class MultiplierPowerup(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self._load_frames()
        self.spawn_interval = 12000
        self.duration = 10000
        self.value = 1
    
    def _load_frames(self):
        self.frames = self._load_frames_from_sheet(
            pygame.image.load("assets/multiplier.png").convert_alpha(),
            128, 32, 4
        )
    
    def _load_frames_from_sheet(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def _spawn(self):
        rect = pygame.Rect(
            self.game.WIDTH + random.randint(0, 100), 
            self.game.player.ground_level - random.randint(40, 80), 
            self.frames[0].get_width(), 
            self.frames[0].get_height()
        )
        self.items.append(rect)
    
    def activate(self):
        self.active = True
        self.timer = pygame.time.get_ticks()
        self.value = 2
    
    def _update_active(self):
        if self.active:
            elapsed = pygame.time.get_ticks() - self.timer
            if elapsed >= self.duration:
                self.active = False
                self.value = 1
    
    def draw(self, screen):
        for multiplier in self.items:
            frame = pygame.transform.scale(
                self.frames[self.frame_index],
                (32, 32)
            )
            screen.blit(frame, multiplier)

class PowerupManager:
    def __init__(self, game):
        self.game = game
        self.double_jump = DoubleJumpPowerup(game)
        self.shield = ShieldPowerup(game)
        self.multiplier = MultiplierPowerup(game)
        
        self.enemy_frames = self._load_frames(
            pygame.image.load("assets/obstacle_enemy.png").convert_alpha(),
            135, 64, 4
        )
        self.enemy_frame_index = 0
        self.enemy_animation_timer = 0
        self.enemy_animation_speed = 150
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        self.double_jump.reset()
        self.shield.reset()
        self.multiplier.reset()
        
        self.enemy_frame_index = 0
        self.enemy_animation_timer = 0
    
    def update(self, dt):
        self.double_jump.update(dt)
        self.shield.update(dt)
        self.multiplier.update(dt)
        
        self._update_enemy_animation(dt)
    
    def _update_enemy_animation(self, dt):
        self.enemy_animation_timer += dt
        if self.enemy_animation_timer >= self.enemy_animation_speed:
            self.enemy_animation_timer = 0
            self.enemy_frame_index = (self.enemy_frame_index + 1) % len(self.enemy_frames)
    
    def draw(self, screen):
        self.double_jump.draw(screen)
        self.shield.draw(screen)
        self.multiplier.draw(screen)
    
    @property
    def dj_active(self):
        return self.double_jump.active
    
    @property
    def dj_timer(self):
        return self.double_jump.timer
    
    @property
    def dj_duration(self):
        return self.double_jump.duration
    
    @property
    def shield_active(self):
        return self.shield.active
    
    @property
    def shield_hits(self):
        return self.shield.hits
    
    @shield_hits.setter
    def shield_hits(self, value):
        self.shield.hits = value
    
    @property
    def max_shield_hits(self):
        return self.shield.max_hits
    
    @max_shield_hits.setter
    def max_shield_hits(self, value):
        self.shield.max_hits = value
    
    @property
    def multiplier_active(self):
        return self.multiplier.active
    
    @property
    def multiplier_timer(self):
        return self.multiplier.timer
    
    @property
    def multiplier_duration(self):
        return self.multiplier.duration
    
    @property
    def multiplier_value(self):
        return self.multiplier.value
    
    @multiplier_value.setter
    def multiplier_value(self, value):
        self.multiplier.value = value
    
    @property
    def shield_spawn_interval(self):
        return self.shield.spawn_interval
    
    @shield_spawn_interval.setter
    def shield_spawn_interval(self, value):
        self.shield.spawn_interval = value
    
    @property
    def dj_spawn_interval(self):
        return self.double_jump.spawn_interval
    
    @dj_spawn_interval.setter
    def dj_spawn_interval(self, value):
        self.double_jump.spawn_interval = value
    
    @property
    def multiplier_spawn_interval(self):
        return self.multiplier.spawn_interval
    
    @multiplier_spawn_interval.setter
    def multiplier_spawn_interval(self, value):
        self.multiplier.spawn_interval = value
    
    @property
    def double_jumps(self):
        return self.double_jump.items
    
    @property
    def shields(self):
        return self.shield.items
    
    @property
    def multipliers(self):
        return self.multiplier.items