import pygame

pygame.init()
screen = pygame.display.set_mode((1, 1))  # Wajib supaya convert_alpha bisa jalan

shield_spritesheet = pygame.image.load("assets/shield.png").convert_alpha()
print("Ukuran shield.png:", shield_spritesheet.get_size())
