import random
import pygame
from material import DIAGONAL_DRIFT, SIDEWAYS_DRIFT, Material
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
# Notably, this is row-major for access, while Pygame uses column-major for PixelArray
# This means that contents[y][x] corresponds to pxarray[x, y]
contents = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

active_material = Materials.SAND


def get_content(x: int, y: int) -> Materials:
    """Get the material at the given coordinates."""
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        return contents[y][x]
    return Materials.EDGE  # Return EDGE if out of bounds


def initialize_board():
    """Initialize the board with some default materials."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if y < BOARD_HEIGHT // 4:
                contents[y][x] = Materials.STONE
            elif x > BOARD_WIDTH // 4 and y < BOARD_HEIGHT // 2:
                contents[y][x] = Materials.SAND
            else:
                contents[y][x] = Materials.NONE


def draw_board(screen):
    """Draw the board to the screen."""
    pxarray = pygame.PixelArray(screen)
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            material = get_material(get_content(x, y))
            pxarray[x, y] = material.color


def tick():
    """Update the board state for the next frame."""
    global contents
    buffer = [
        [Materials.CLEAN for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
    ]
    # For now, just copy the current contents to the buffer
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if buffer[y][x] != Materials.CLEAN:
                continue
            old_contents = get_content(x, y)
            old_material = get_material(old_contents)
            below_contents = get_content(x, y + 1)
            below_material = get_material(below_contents)
            modified = False
            # If the material is denser than the one below, swap them
            if old_material.density > below_material.density:
                buffer[y + 1][x] = old_contents
                buffer[y][x] = below_contents
                modified = True
            elif old_material.drift >= DIAGONAL_DRIFT:
                # Drift down diagonally if possible
                below_left_contents = get_content(x - 1, y + 1)
                below_right_contents = get_content(x + 1, y + 1)
                below_left_material = get_material(below_left_contents)
                below_right_material = get_material(below_right_contents)
                # Randomly check left or right first
                if random.randint(0, 1) == 0:
                    if below_left_material.density < old_material.density:
                        buffer[y + 1][x - 1] = old_contents
                        buffer[y][x] = below_left_contents
                        modified = True
                    elif below_right_material.density < old_material.density:
                        buffer[y + 1][x + 1] = old_contents
                        buffer[y][x] = below_right_contents
                        modified = True
                else:
                    if below_right_material.density < old_material.density:
                        buffer[y + 1][x + 1] = old_contents
                        buffer[y][x] = below_right_contents
                        modified = True
                    elif below_left_material.density < old_material.density:
                        buffer[y + 1][x - 1] = old_contents
                        buffer[y][x] = below_left_contents
                        modified = True
            elif old_material.drift >= SIDEWAYS_DRIFT:
                # Drift sideways if possible
                left_contents = get_content(x - 1, y)
                right_contents = get_content(x + 1, y)
                left_material = get_material(left_contents)
                right_material = get_material(right_contents)
                if random.randint(0, 1) == 0:
                    if left_material.density < old_material.density:
                        buffer[y][x - 1] = old_contents
                        buffer[y][x] = left_contents
                        modified = True
                    elif right_material.density < old_material.density:
                        buffer[y][x + 1] = old_contents
                        buffer[y][x] = right_contents
                        modified = True
                else:
                    if right_material.density < old_material.density:
                        buffer[y][x + 1] = old_contents
                        buffer[y][x] = right_contents
                        modified = True
                    elif left_material.density < old_material.density:
                        buffer[y][x - 1] = old_contents
                        buffer[y][x] = left_contents
                        modified = True
            # If nothing was modified, keep the old contents
            if not modified:
                buffer[y][x] = old_contents

    # Swap the buffers
    contents = buffer


if __name__ == "__main__":
    print("Starting main.py")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    initialize_board()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    active_material = Materials.SAND
                elif event.key == pygame.K_2:
                    active_material = Materials.WATER
                elif event.key == pygame.K_3:
                    active_material = Materials.STONE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = mouse_x // CELL_SIZE
                    row = mouse_y // CELL_SIZE
                    if 0 <= col < BOARD_WIDTH and 0 <= row < BOARD_HEIGHT:
                        contents[row][col] = active_material

        tick()

        draw_board(screen)

        pygame.display.flip()

        clock.tick(60)
