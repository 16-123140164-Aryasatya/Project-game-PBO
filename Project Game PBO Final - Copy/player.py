import pygame
from abc import ABC, abstractmethod

class Character(ABC):
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.speed_y = 0
        self.gravity = 0.5
        self.jump_power = -10
        self.ground_level = self.game.HEIGHT - 50
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
    
    @abstractmethod
    def _load_sprites(self):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def draw(self, screen):
        pass
    
    def _apply_gravity(self):
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
    
    def _check_ground_collision(self):
        if self.rect.bottom >= self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0
    
    def _update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    def jump(self):
        if self.rect.bottom >= self.ground_level:
            self.speed_y = self.jump_power

class Player(Character):
    def __init__(self, game):
        super().__init__(game)
        self._load_sprites()
        self.reset()
        
        # Hitboxes
        self._normal_hitbox = pygame.Rect(0, 0, 768//8, 64)
        self._roll_hitbox = pygame.Rect(0, 0, 768//8, 32)
        self._attack_hitbox = pygame.Rect(0, 0, 768//8, 64)
    
    def _load_sprites(self):
        player_spritesheet = pygame.image.load("assets/player.png").convert_alpha()
        self.frames = self._load_frames(player_spritesheet, 768, 64, 8)
        
        self.roll_frames = self._load_frames(
            pygame.image.load("assets/player_roll.png").convert_alpha(), 
            768, 32, 8
        )
        
        self.attack_frames = self._load_frames(
            pygame.image.load("assets/player_attack.png").convert_alpha(),
            768, 64, 8
        )
    
    def _load_frames(self, spritesheet, total_width, height, frame_count):
        frame_width = total_width // frame_count
        return [spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)) 
                for i in range(frame_count)]
    
    def reset(self):
        self.rect = pygame.Rect(100, self.game.HEIGHT - 64 - 50, 768//8, 64)
        self.speed_y = 0
        self.bg_scroll_x = 0
        self.bg_speed = 2
        
        # Animation
        self.frame_index = 0
        self.animation_timer = 0
        
        # Rolling
        self._is_rolling = False
        self._roll_timer = 0
        self._roll_duration = 1000
        
        # Attacking
        self._is_attacking = False
        self._attack_frame_index = 0
        self._attack_animation_timer = 0
        self._attack_animation_speed = 80
        self._attack_cooldown = 0
        self._last_attack_time = 0
        self._attack_hitbox = None
        
        # Game stats
        self._score = 0
        self._coin_score = 0
        self._score_timer = 0
        self._score_interval = 100
        
        # Jumping
        self._has_jumped_once = False
    
    @property
    def is_rolling(self):
        return self._is_rolling
    
    @property
    def is_attacking(self):
        return self._is_attacking
    
    @property
    def attack_hitbox(self):
        return self._attack_hitbox
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        self._score = value
    
    @property
    def coin_score(self):
        return self._coin_score
    
    @coin_score.setter
    def coin_score(self, value):
        self._coin_score = value
    
    @property
    def score_timer(self):
        return self._score_timer
    
    @score_timer.setter
    def score_timer(self, value):
        self._score_timer = value
    
    @property
    def score_interval(self):
        return self._score_interval
    
    @property
    def has_jumped_once(self):
        return self._has_jumped_once
    
    def update(self, dt):
        self._apply_gravity()
        self._check_ground_collision()
        self._check_roll_end()
        self._update_animations(dt)
        self._update_background_scroll()
        self._update_score_timer(dt)
    
    def _check_roll_end(self):
        if self._is_rolling and pygame.time.get_ticks() - self._roll_timer >= self._roll_duration:
            self.end_roll()
    
    def _update_animations(self, dt):
        if self._is_rolling:
            self._update_roll_animation(dt)
        elif self._is_attacking:
            self._update_attack_animation(dt)
        else:
            self._update_normal_animation(dt)
    
    def _update_roll_animation(self, dt):
        super()._update_animation(dt)
    
    def _update_attack_animation(self, dt):
        self._attack_animation_timer += dt
        if self._attack_animation_timer >= self._attack_animation_speed:
            self._attack_animation_timer = 0
            self._attack_frame_index += 1
            if self._attack_frame_index >= len(self.attack_frames):
                self._attack_frame_index = 0
                self._is_attacking = False
            else:
                self._attack_hitbox = pygame.Rect(
                    self.rect.right - 20, 
                    self.rect.top + 20, 
                    60, 
                    self.rect.height - 40)
    
    def _update_normal_animation(self, dt):
        super()._update_animation(dt)
    
    def _update_background_scroll(self):
        self.bg_scroll_x = (self.bg_scroll_x - self.bg_speed) % self.game.WIDTH
    
    def _update_score_timer(self, dt):
        self._score_timer += dt
    
    def start_roll(self):
        if not self._is_rolling and not self._is_attacking:
            self._is_rolling = True
            self._is_attacking = False
            self._roll_timer = pygame.time.get_ticks()
            bottom = self.rect.bottom
            self.rect.height = 32
            self.rect.bottom = bottom
    
    def end_roll(self):
        self._is_rolling = False
        self.rect.height = 64
        new_bottom = self.rect.bottom
        self.rect.bottom = new_bottom
        
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0
    
    def jump(self):
        if self.rect.bottom >= self.ground_level:
            self.speed_y = self.jump_power
            self._has_jumped_once = False
        elif self.game.powerup_manager.dj_active and not self._has_jumped_once:
            self.speed_y = self.jump_power
            self._has_jumped_once = True
    
    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self._last_attack_time > self._attack_cooldown:
            if self._is_rolling:
                self.end_roll()
            
            self._is_attacking = True
            self._is_rolling = False
            self._attack_frame_index = 0
            self._last_attack_time = current_time
            self._attack_hitbox = pygame.Rect(
                self.rect.right - 20, 
                self.rect.top + 20, 
                60, 
                self.rect.height - 40
            )
    
    def draw(self, screen):
        if self._is_attacking:
            screen.blit(self.attack_frames[self._attack_frame_index], self.rect)
        elif self._is_rolling:
            screen.blit(self.roll_frames[self.frame_index], self.rect)
        else:
            screen.blit(self.frames[self.frame_index], self.rect)