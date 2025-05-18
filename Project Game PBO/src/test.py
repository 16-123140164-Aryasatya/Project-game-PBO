import pygame

pygame.init()
screen = pygame.display.set_mode((1, 1))  # Wajib supaya convert_alpha bisa jalan

shield_spritesheet = pygame.image.load("assets/shield.png").convert_alpha()
obstacle_img = pygame.image.load("assets/multiplier.png").convert_alpha()
print("Ukuran shield.png:", obstacle_img.get_size())
