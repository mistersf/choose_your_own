import pygame
from material import Material
from materials import Materials, get_material

# Constants
# The dimensions of the board in cells
BOARD_WIDTH = 128
BOARD_HEIGHT = 128

# The size of each cell in pixels
# UNIMPLEMENTED, set to 1 for now
CELL_SIZE = 1

# The dimensions of the screen in pixels
SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE

# The current state of the board
contents = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
# The buffer for the next frame
buffer = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def draw_board(screen):
    """Draw the board to the screen."""
    pxarray = pygame.PixelArray(screen)
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            material = get_material(contents[y][x])
            pxarray[x, y] = material.color


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

        draw_board(screen)

        pygame.display.flip()

        clock.tick(60)
