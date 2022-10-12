import pygame
from tiles import Tile
from settings import tile_size, screen_width, level_map
from player import Player

class Level:
    def __init__(self, start_data, level_data, surface):
        self.display_surface = surface
        self.setup_level(start_data)

        self.continue_level = level_data
        self.world_shift = 0
        self.realxpos = tile_size*4.5

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

        if player_x < screen_width * 0.25 and direction_x < 0:
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
        start = int((xposingame - xposonscreen)/tile_size)
        end = int((xposingame + (screen_width - xposonscreen))/tile_size)
        ytile = int(((yposingame)/tile_size))
        xtile = int(round((xposingame)/tile_size))
        array = []
        arraystring = ''
        row_index = 0
        col_index = start
        for row in layout:
            for col in row:
                if(col_index >= start and col_index <= end):
                    if(row_index == ytile and col_index == xtile):
                        arraystring += 'P'
                    else:
                        arraystring += col
                col_index += 1
            array.append(arraystring)
            print(arraystring)
            arraystring = ''
            # print(f'{row_index},{col_index}:{col}')
            row_index += 1
            col_index = 0
        #print(array)


    def run(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.scroll_x()

        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.draw(self.display_surface)
        self.get_state(self.player.sprite.rect.x, self.realxpos, self.player.sprite.rect.y, self.continue_level)
        print(self.player.sprite.status)

