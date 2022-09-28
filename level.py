import pygame
from tiles import Tile
from settings import tile_size, screen_width, level_map
from player import Player


class Level:
    def __init__(self, level_data, surface):
        self.tiles = None # Declaring variables
        self.player = None
        self.display_surface = surface
        self.setup_level(level_data)

        self.world_shift = 0
        self.real_x_pos = 288

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
                #print(f'{row_index},{col_index}:{col}')
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

        if player_x < screen_width * 0.25 and direction_x < 0: #Scrolling
            self.world_shift = 8
            self.real_x_pos -= 8
            player.speed = 0
            if player_x < screen_width * 0.25 - 8: # Prevent from "glitching out" of the scrolling to the left
                player.rect.x += 8
                self.real_x_pos += 8
        elif player_x > screen_width * 0.75 and direction_x > 0:
            self.world_shift = -8
            self.real_x_pos += 8
            player.speed = 0
            if player_x > screen_width * 0.75 + 8: # Prevent from "glitching out" of the scrolling to the right
                player.rect.x -= 8
                self.real_x_pos -= 8
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        self.real_x_pos += player.direction.x * player.speed

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    self.real_x_pos -= player.direction.x * player.speed
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    self.real_x_pos -= player.direction.x * player.speed

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

    def get_state(self, xposonscreen, xposingame, yposingame, layout):
        start = int((xposingame - xposonscreen)/tile_size)
        end = int((xposingame + (screen_width - xposonscreen))/tile_size)
        ytile = int((yposingame / tile_size))
        xtile = int(round(xposingame / tile_size))
        array = []
        arraaystring = ''
        row_index = 0
        col_index = start
        for row in layout:
            for col in row:
                if start <= col_index <= end:
                    if row_index == ytile and col_index == xtile:
                        arraaystring += 'P'
                    else:
                        arraaystring += col
                col_index += 1
            array.append(arraaystring)
            print(arraaystring)
            arraaystring = ''
            # print(f'{row_index},{col_index}:{col}')
            row_index += 1
            col_index = 0
        #print(array)

    def run(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)

        self.horizontal_movement_collision()
        self.vertical_movement_collision() # By doing the horizontal movement first then vertical it means that collisions are much easier to work with.
        self.scroll_x()
        self.player.update()
        self.player.draw(self.display_surface)
        self.get_state(self.player.sprite.rect.x, self.real_x_pos, self.player.sprite.rect.y, level_map)
