import pygame
from tiles import Tile
from settings import tile_size, screen_width, level_map, start_map, screen_height, level_map_test
from player import Player
import torch
from collections import deque
import numpy as np


class Level:
    def __init__(self, start_data, level_data, surface):
        self.display_surface = surface
        self.setup_level(start_data)

        self.continue_level = level_data
        self.world_shift = 0
        self.realxpos = tile_size * 2
        self.highestx = tile_size * 2
        self.over = False
        self.frames = 0
        self.reward = 0

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        row_index = 0
        col_index = 0
        for row in layout:
            for col in row:
                x = tile_size * col_index
                y = tile_size * row_index
                if col == 'X':
                    tile = Tile(pos=(x, y), size=tile_size, color='grey')
                    self.tiles.add(tile)
                if col == 'P':
                    player = Player(pos=(x, y))
                    self.player.add(player)
                col_index += 1
            row_index += 1
            col_index = 0

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width * 0.25 and direction_x < 0 and self.realxpos >= 288:
            self.world_shift = 8
            self.realxpos -= 8
            player.speed = 0
        elif player_x > screen_width * 0.75 and direction_x > 0:
            self.world_shift = -8
            self.realxpos += 8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8
        if self.realxpos <= 0 and direction_x < 0:
            player.speed = 0
            self.realxpos = 0
            player.rect.left = 0

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        self.realxpos += player.direction.x * player.speed

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    self.realxpos -= player.direction.x * player.speed
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    self.realxpos -= player.direction.x * player.speed

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1.2:
            player.on_ground = False

    def get_state(self, xposonscreen, xposingame, yposingame, layout):
        if (((xposingame - xposonscreen) / tile_size) < 0):
            start = int(np.floor(((xposingame - xposonscreen) / tile_size)))
        else:
            start = int((xposingame - xposonscreen) / tile_size)
        end = int((xposingame - xposonscreen + screen_width) / tile_size)
        ytile = int(((yposingame) / tile_size))
        xtile = int(round((xposingame) / tile_size))
        array = [0] * 209
        row_index = 0
        col_index = start
        counter = 0
        for row in layout:
            for col in row:
                if (col_index >= start and col_index < end):
                    if (row_index == ytile and col_index == xtile):
                        array[counter] = 2
                        counter += 1
                    else:
                        array[counter] = int(col)/2
                        counter += 1
                col_index += 1
            row_index += 1
            col_index = 0

        return array

    def givereward(self):
        if self.realxpos > self.highestx:
            self.reward = 10
            self.highestx = self.realxpos
        else:
            self.reward = -1
        if self.realxpos <= self.highestx and self.frames > self.realxpos + 1000:
            self.over = True
            self.reward = -100
        elif self.player.sprite.rect.y >= screen_height:
            self.over = True
            self.reward = -100
        if self.realxpos >= 2944:
            self.over = True
            self.reward = 100

    def input(self, action):
        self.player.sprite.get_input(action)
        self.givereward()
        return self.reward, self.over, self.highestx

    def restart(self):
        self.setup_level(start_map)
        self.world_shift = 0
        self.realxpos = tile_size * 2
        self.highestx = tile_size * 2
        self.frames = 0
        self.over = False
        self.reward = 0

    def run(self, main=False):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.scroll_x()

        if main:
            self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.draw(self.display_surface)
        self.frames += 1
