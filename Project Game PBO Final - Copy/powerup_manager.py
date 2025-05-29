import pygame
import random
from abc import ABC, abstractmethod

class Powerup(ABC):
    def __init__(self, game, frames, spawn_interval):
        self._game = game
        self._frames = frames
        self._spawn_interval = spawn_interval
        self._spawn_timer = 0
        self._active = False
        self._frame_index = 0
        self._animation_timer = 0
        self._animation_speed = 100
        self._instances = []
    
    @abstractmethod
    def _activate_effect(self):
        """Abstract method to define powerup effect"""
        pass
    
    @abstractmethod
    def _update_active(self):
        """Abstract method to update active powerup state"""
        pass
    
    def update(self, dt):
        """Update powerup state"""
        self._update_spawning(dt)
        self._update_instances(dt)
        self._update_animation(dt)
        if self._active:
            self._update_active()
    
    def _update_spawning(self, dt):
        """Update powerup spawning logic"""
        if not self._active:
            self._spawn_timer += dt
            if self._spawn_timer >= self._spawn_interval:
                self._spawn_instance()
                self._spawn_timer = 0
    
    def _spawn_instance(self):
        """Spawn a new powerup instance"""
        rect = pygame.Rect(
            self._game.WIDTH + random.randint(0, 100),
            self._game.player.ground_level - random.randint(40, 80),
            self._frames[0].get_width(),
            self._frames[0].get_height()
        )
        self._instances.append(rect)
    
    def _update_instances(self, dt):
        """Update all powerup instances"""
        for instance in self._instances[:]:
            instance.x -= self._game.obstacle_manager.obstacle_speed
            
            if instance.right < 0:
                self._instances.remove(instance)
                continue
            
            if self._game.player.rect.inflate(-80, -30).colliderect(instance):
                self._instances.remove(instance)
                self._activate_effect()
                self._game.play_collectible_sound()
    
    def _update_animation(self, dt):
        """Update animation frames"""
        self._animation_timer += dt
        if self._animation_timer >= self._animation_speed:
            self._animation_timer = 0
            self._frame_index = (self._frame_index + 1) % len(self._frames)
    
    def draw(self, screen):
        """Draw all powerup instances"""
        for instance in self._instances:
            frame = pygame.transform.scale(
                self._frames[self._frame_index],
                (32, 32)
            )
            screen.blit(frame, instance)
    
    @property
    def active(self):
        """Check if powerup is active"""
        return self._active
    
    @property
    def instances(self):
        """Get powerup instances (read-only)"""
        return self._instances

class DoubleJumpPowerup(Powerup):
    def __init__(self, game, frames):
        super().__init__(game, frames, 7000)
        self._duration = 30000
        self._timer = 0
    
    def _activate_effect(self):
        """Activate double jump effect"""
        self._active = True
        self._timer = pygame.time.get_ticks()
        self._game.player.enable_double_jump()
    
    def _update_active(self):
        """Update active double jump state"""
        elapsed = pygame.time.get_ticks() - self._timer
        if elapsed >= self._duration:
            self._active = False
            self._game.player.disable_double_jump()

class ShieldPowerup(Powerup):
    def __init__(self, game, frames):
        super().__init__(game, frames, 10000)
        self._hits = 0
        self._max_hits = 2
    
    def _activate_effect(self):
        """Activate shield effect"""
        self._active = True
        self._hits = 0
        self._game.player.activate_shield()
    
    def register_hit(self):
        """Register a shield hit"""
        if self._active:
            self._hits += 1
            if self._hits >= self._max_hits:
                self._active = False
                self._game.player.deactivate_shield()
            return True
        return False
    
    @property
    def hits_remaining(self):
        """Get remaining shield hits"""
        return self._max_hits - self._hits
    
    def _update_active(self):
        """Shield doesn't time out, only deactivates on hits"""
        pass

class MultiplierPowerup(Powerup):
    def __init__(self, game, frames):
        super().__init__(game, frames, 12000)
        self._duration = 10000
        self._timer = 0
        self._value = 1
    
    def _activate_effect(self):
        """Activate score multiplier"""
        self._active = True
        self._timer = pygame.time.get_ticks()
        self._value = 2
    
    def _update_active(self):
        """Update active multiplier state"""
        elapsed = pygame.time.get_ticks() - self._timer
        if elapsed >= self._duration:
            self._active = False
            self._value = 1
    
    @property
    def value(self):
        """Get current multiplier value"""
        return self._value

class PowerupManager:
    def __init__(self, game):
        self._game = game
        self._load_assets()
        self.reset()
    
    def _load_assets(self):
        """Load all powerup assets"""
        self._dj_frames = self._load_frames(
            pygame.image.load("assets/double_jump.png").convert_alpha(),
            128, 32, 4
        )
        self._shield_frames = self._load_frames(
            pygame.image.load("assets/shield.png").convert_alpha(),
            128, 32, 4
        )
        self._multiplier_frames = self._load_frames(
            pygame.image.load("assets/multiplier.png").convert_alpha(),
            128, 32, 4
        )
        self._enemy_frames = self._load_frames(
            pygame.image.load("assets/obstacle_enemy.png").convert_alpha(),
            135, 64, 4
        )
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        """Helper method to load animation frames"""
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        """Reset all powerup states"""
        self._double_jump = DoubleJumpPowerup(self._game, self._dj_frames)
        self._shield = ShieldPowerup(self._game, self._shield_frames)
        self._multiplier = MultiplierPowerup(self._game, self._multiplier_frames)
        
        self._enemy_frame_index = 0
        self._enemy_animation_timer = 0
        self._enemy_animation_speed = 150
    
    def update(self, dt):
        """Update all powerups"""
        self._double_jump.update(dt)
        self._shield.update(dt)
        self._multiplier.update(dt)
        self._update_enemy_animation(dt)
    
    def _update_enemy_animation(self, dt):
        """Update enemy animation frames"""
        self._enemy_animation_timer += dt
        if self._enemy_animation_timer >= self._enemy_animation_speed:
            self._enemy_animation_timer = 0
            self._enemy_frame_index = (self._enemy_frame_index + 1) % len(self._enemy_frames)
    
    def draw(self, screen):
        """Draw all powerups"""
        self._double_jump.draw(screen)
        self._shield.draw(screen)
        self._multiplier.draw(screen)
    
    # Property getters for powerup states
    @property
    def double_jump_active(self):
        return self._double_jump.active
    
    @property
    def shield_active(self):
        return self._shield.active
    
    @property
    def multiplier_active(self):
        return self._multiplier.active
    
    @property
    def multiplier_value(self):
        return self._multiplier.value
    
    @property
    def shield_hits_remaining(self):
        return self._shield.hits_remaining
    
    @property
    def enemy_frame_index(self):
        return self._enemy_frame_index
    
    # Methods for shield interaction
    def register_shield_hit(self):
        """Register a hit on the shield"""
        return self._shield.register_hit()