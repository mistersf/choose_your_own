import pygame
from material import Material
from materials import Materials

# Constants
# The dimensions of the board in cells
BOARD_WIDTH = 128
BOARD_HEIGHT = 128

# The size of each cell in pixels
CELL_SIZE = 8

# The dimensions of the screen in pixels
SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE

# The current state of the board
contents = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
# The buffer for the next frame
buffer = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


if __name__ == "__main__":
    print("Starting main.py")
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
