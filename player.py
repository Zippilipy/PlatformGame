import pygame
import random
from settings import tile_size

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((tile_size/2, tile_size))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft = pos)

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 1
        self.jump_speed = -20

        # status
        self.status = 'idle'
        self.on_ground = False

    def get_input(self, action):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if keys[pygame.K_UP] and self.on_ground:
            self.jump()

        if action == 0:
            self.direction.x = 1
        elif action == 1:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if action == 2 and self.on_ground:
            self.jump()

        return

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1.2:
            self.status = 'fall'
        else:
            if self.direction.x == 0:
                self.status = 'idle'
            else:
                self.status = 'run'

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed


    def update(self):
        self.get_status()
