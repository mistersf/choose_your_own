import pygame

# Constants

BOARD_WIDTH = 128
BOARD_HEIGHT = 128

CELL_SIZE = 8

SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE


if __name__ == "__main__":
    print("Starting main.py")

    # Set up pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        pygame.display.flip()

        clock.tick(60)
