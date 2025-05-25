import pygame
import random

class PowerupManager:
    def __init__(self, game):
        self.game = game
        self.reset()
        self._load_assets()
    
    def _load_assets(self):
        self.dj_frames = self._load_frames(
            pygame.image.load("assets/double_jump.png").convert_alpha(),
            128, 32, 4
        )
        self.shield_frames = self._load_frames(
            pygame.image.load("assets/shield.png").convert_alpha(),
            128, 32, 4
        )
        self.multiplier_frames = self._load_frames(
            pygame.image.load("assets/multiplier.png").convert_alpha(),
            128, 32, 4
        )
        self.enemy_frames = self._load_frames(
            pygame.image.load("assets/obstacle_enemy.png").convert_alpha(),
            135, 64, 4
        )
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        self.double_jumps = []
        self.shields = []
        self.multipliers = []
        
        self.dj_spawn_timer = 0
        self.dj_spawn_interval = 7000
        self.shield_spawn_timer = 0
        self.shield_spawn_interval = 10000
        self.multiplier_spawn_timer = 0
        self.multiplier_spawn_interval = 12000
        
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
    
    def update(self, dt):
        self._update_animations(dt)
        self._spawn_powerups(dt)
        self._update_active_powerups()
    
    def _update_animations(self, dt):
        self._update_dj_animation(dt)
        self._update_shield_animation(dt)
        self._update_multiplier_animation(dt)
        self._update_enemy_animation(dt)
    
    def _update_dj_animation(self, dt):
        self.dj_animation_timer += dt
        if self.dj_animation_timer >= self.dj_animation_speed:
            self.dj_animation_timer = 0
            self.dj_frame_index = (self.dj_frame_index + 1) % len(self.dj_frames)
    
    def _update_shield_animation(self, dt):
        self.shield_animation_timer += dt
        if self.shield_animation_timer >= self.shield_animation_speed:
            self.shield_animation_timer = 0
            self.shield_frame_index = (self.shield_frame_index + 1) % len(self.shield_frames)
    
    def _update_multiplier_animation(self, dt):
        self.multiplier_animation_timer += dt
        if self.multiplier_animation_timer >= self.multiplier_animation_speed:
            self.multiplier_animation_timer = 0
            self.multiplier_frame_index = (self.multiplier_frame_index + 1) % len(self.multiplier_frames)
    
    def _update_enemy_animation(self, dt):
        self.enemy_animation_timer += dt
        if self.enemy_animation_timer >= self.enemy_animation_speed:
            self.enemy_animation_timer = 0
            self.enemy_frame_index = (self.enemy_frame_index + 1) % len(self.enemy_frames)
    
    def _spawn_powerups(self, dt):
        if not self.dj_active:
            self._spawn_double_jump(dt)
        
        if not self.shield_active:
            self._spawn_shield(dt)
        
        if not self.multiplier_active:
            self._spawn_multiplier(dt)
        
        self._update_powerups()
    
    def _spawn_double_jump(self, dt):
        self.dj_spawn_timer += dt
        if self.dj_spawn_timer >= self.dj_spawn_interval:
            rect = pygame.Rect(
                self.game.WIDTH + random.randint(0, 100), 
                self.game.player.ground_level - random.randint(40, 80), 
                self.dj_frames[0].get_width(), 
                self.dj_frames[0].get_height()
            )
            self.double_jumps.append(rect)
            self.dj_spawn_timer = 0
    
    def _spawn_shield(self, dt):
        self.shield_spawn_timer += dt
        if self.shield_spawn_timer >= self.shield_spawn_interval:
            rect = pygame.Rect(
                self.game.WIDTH + random.randint(0, 100), 
                self.game.player.ground_level - random.randint(40, 80), 
                self.shield_frames[0].get_width(), 
                self.shield_frames[0].get_height()
            )
            self.shields.append(rect)
            self.shield_spawn_timer = 0
    
    def _spawn_multiplier(self, dt):
        self.multiplier_spawn_timer += dt
        if self.multiplier_spawn_timer >= self.multiplier_spawn_interval:
            rect = pygame.Rect(
                self.game.WIDTH + random.randint(0, 100), 
                self.game.player.ground_level - random.randint(40, 80), 
                self.multiplier_frames[0].get_width(), 
                self.multiplier_frames[0].get_height()
            )
            self.multipliers.append(rect)
            self.multiplier_spawn_timer = 0
    
    def _update_powerups(self):
        self._update_double_jumps()
        self._update_shields()
        self._update_multipliers()
    
    def _update_double_jumps(self):
        for dj in self.double_jumps[:]:
            dj.x -= self.game.obstacle_manager.obstacle_speed
            
            if dj.right < 0:
                self.double_jumps.remove(dj)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(dj):
                self.double_jumps.remove(dj)
                self.dj_active = True
                self.dj_timer = pygame.time.get_ticks()
                self.game.play_collectible_sound()
    
    def _update_shields(self):
        for shield in self.shields[:]:
            shield.x -= self.game.obstacle_manager.obstacle_speed
            
            if shield.right < 0:
                self.shields.remove(shield)
                continue
            
            if self.game.player.rect.inflate(-80, -30).colliderect(shield):
                self.shields.remove(shield)
                self.shield_active = True
                self.shield_hits = 0
                self.game.play_collectible_sound()
    
    def _update_multipliers(self):
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
                self.game.play_collectible_sound()
    
    def _update_active_powerups(self):
        self._update_dj_active()
        self._update_multiplier_active()
    
    def _update_dj_active(self):
        if self.dj_active:
            elapsed = pygame.time.get_ticks() - self.dj_timer
            if elapsed >= self.dj_duration:
                self.dj_active = False
    
    def _update_multiplier_active(self):
        if self.multiplier_active:
            elapsed = pygame.time.get_ticks() - self.multiplier_timer
            if elapsed >= self.multiplier_duration:
                self.multiplier_active = False
                self.multiplier_value = 1
    
    def draw(self, screen):
        self._draw_double_jumps(screen)
        self._draw_shields(screen)
        self._draw_multipliers(screen)
    
    def _draw_double_jumps(self, screen):
        for dj in self.double_jumps:
            frame = pygame.transform.scale(
                self.dj_frames[self.dj_frame_index],
                (32, 32)
            )
            screen.blit(frame, dj)
    
    def _draw_shields(self, screen):
        for shield in self.shields:
            frame = pygame.transform.scale(
                self.shield_frames[self.shield_frame_index],
                (32, 32)
            )
            screen.blit(frame, shield)
    
    def _draw_multipliers(self, screen):
        for multiplier in self.multipliers:
            frame = pygame.transform.scale(
                self.multiplier_frames[self.multiplier_frame_index],
                (32, 32)
            )
            screen.blit(frame, multiplier)