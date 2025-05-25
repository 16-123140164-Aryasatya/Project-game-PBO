import pygame

class Player:
    def __init__(self, game):
        self.game = game
        self.reset()
        
        # Load sprites
        self._load_sprites()
        
        # Hitboxes
        self.normal_hitbox = pygame.Rect(0, 0, 768//8, 64)
        self.roll_hitbox = pygame.Rect(0, 0, 768//8, 32)
        self.attack_hitbox_rect = pygame.Rect(0, 0, 768//8, 64)
    
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
        self.gravity = 0.5
        self.jump_power = -10
        self.ground_level = self.game.HEIGHT - 50
        self.bg_scroll_x = 0
        self.bg_speed = 2
        
        # Animation
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
        
        # Rolling
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_duration = 1000
        
        # Attacking
        self.is_attacking = False
        self.attack_frame_index = 0
        self.attack_animation_timer = 0
        self.attack_animation_speed = 80
        self.attack_timer = 0
        self.attack_duration = 1000
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.attack_hitbox = None
        
        # Game stats
        self.score = 0
        self.coin_score = 0
        self.score_timer = 0
        self.score_interval = 100
        
        # Jumping
        self.has_jumped_once = False
    
    def update(self, dt):
        self._apply_gravity()
        self._check_ground_collision()
        self._check_roll_end()
        self._update_animations(dt)
        self._update_background_scroll()
        self._update_score_timer(dt)
    
    def _apply_gravity(self):
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
    
    def _check_ground_collision(self):
        if self.rect.bottom >= self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0
            self.has_jumped_once = False
    
    def _check_roll_end(self):
        if self.is_rolling and pygame.time.get_ticks() - self.roll_timer >= self.roll_duration:
            self.end_roll()
    
    def _update_animations(self, dt):
        if self.is_rolling:
            self._update_roll_animation(dt)
        elif self.is_attacking:
            self._update_attack_animation(dt)
        else:
            self._update_normal_animation(dt)
    
    def _update_roll_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.roll_frames)
    
    def _update_attack_animation(self, dt):
        self.attack_animation_timer += dt
        if self.attack_animation_timer >= self.attack_animation_speed:
            self.attack_animation_timer = 0
            self.attack_frame_index += 1
            if self.attack_frame_index >= len(self.attack_frames):
                self.attack_frame_index = 0
                self.is_attacking = False
            else:
                self.attack_hitbox = pygame.Rect(
                    self.rect.right - 20, 
                    self.rect.top + 20, 
                    60, 
                    self.rect.height - 40)
    
    def _update_normal_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    def _update_background_scroll(self):
        self.bg_scroll_x = (self.bg_scroll_x - self.bg_speed) % self.game.WIDTH
    
    def _update_score_timer(self, dt):
        self.score_timer += dt
    
    def start_roll(self):
        if not self.is_rolling and not self.is_attacking:
            self.is_rolling = True
            self.is_attacking = False
            self.roll_timer = pygame.time.get_ticks()
            bottom = self.rect.bottom
            self.rect.height = 32
            self.rect.bottom = bottom
    
    def end_roll(self):
        self.is_rolling = False
        self.rect.height = 64
        new_bottom = self.rect.bottom
        self.rect.bottom = new_bottom
        
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.speed_y = 0
    
    def jump(self):
        if self.rect.bottom >= self.ground_level:
            self.speed_y = self.jump_power
            self.has_jumped_once = False
        elif self.game.powerup_manager.dj_active and not self.has_jumped_once:
            self.speed_y = self.jump_power
            self.has_jumped_once = True
    
    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.is_rolling:
                self.end_roll()
            
            self.is_attacking = True
            self.is_rolling = False
            self.attack_frame_index = 0
            self.last_attack_time = current_time
            self.attack_hitbox = pygame.Rect(
                self.rect.right - 20, 
                self.rect.top + 20, 
                60, 
                self.rect.height - 40
            )
    
    def draw(self, screen):
        if self.is_attacking:
            screen.blit(self.attack_frames[self.attack_frame_index], self.rect)
        elif self.is_rolling:
            screen.blit(self.roll_frames[self.frame_index], self.rect)
        else:
            screen.blit(self.frames[self.frame_index], self.rect)