import pygame, sys
from settings import *
from level import Level


def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    level = Level(start_map, level_map, screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill('black')
        level.run(main=True)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
