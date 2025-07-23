import random
import pygame
from material import DIAGONAL_DRIFT, SIDEWAYS_DRIFT, Material
from materials import Materials, get_material

# Constants
# The dimensions of the board in cells
BOARD_WIDTH = 128
BOARD_HEIGHT = 128

# The size of each cell in pixels
CELL_SIZE = 4

# The dimensions of the screen in pixels
SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE

# The current state of the board
# Notably, this is row-major for access, while Pygame uses column-major for PixelArray
# This means that contents[y][x] corresponds to pxarray[x, y]
contents = [[Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

active_material = Materials.SAND
brush_radius = 1
drawing = False


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


def buffer_swap(buffer, x1, y1, contents1, x2, y2, contents2):
    """
    Swap two cells in the buffer ONLY IF CLEAN.
    Returns False if the swap was not possible.
    """
    clean1 = buffer[y1][x1] == Materials.CLEAN or buffer[y1][x1] == Materials.NONE
    clean2 = buffer[y2][x2] == Materials.CLEAN or buffer[y2][x2] == Materials.NONE
    if not (clean1 and clean2):
        return False
    buffer[y1][x1] = contents2
    buffer[y2][x2] = contents1
    return True


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
                modified = buffer_swap(
                    buffer, x, y, old_contents, x, y + 1, below_contents
                )
            else:
                if random.random() > old_material.friction:
                    if not modified and old_material.drift >= DIAGONAL_DRIFT:
                        # Drift down diagonally if possible
                        below_left_contents = get_content(x - 1, y + 1)
                        below_right_contents = get_content(x + 1, y + 1)
                        below_left_material = get_material(below_left_contents)
                        below_right_material = get_material(below_right_contents)
                        # Randomly check left or right first
                        if random.randint(0, 1) == 0:
                            if below_left_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer,
                                    x,
                                    y,
                                    old_contents,
                                    x - 1,
                                    y + 1,
                                    below_left_contents,
                                )
                            elif below_right_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer,
                                    x,
                                    y,
                                    old_contents,
                                    x + 1,
                                    y + 1,
                                    below_right_contents,
                                )
                        else:
                            if below_right_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer,
                                    x,
                                    y,
                                    old_contents,
                                    x + 1,
                                    y + 1,
                                    below_right_contents,
                                )
                            elif below_left_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer,
                                    x,
                                    y,
                                    old_contents,
                                    x - 1,
                                    y + 1,
                                    below_left_contents,
                                )
                    if not modified and old_material.drift >= SIDEWAYS_DRIFT:
                        # Drift sideways if possible
                        left_contents = get_content(x - 1, y)
                        right_contents = get_content(x + 1, y)
                        left_material = get_material(left_contents)
                        right_material = get_material(right_contents)
                        if random.randint(0, 1) == 0:
                            if left_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer, x, y, old_contents, x - 1, y, left_contents
                                )
                            elif right_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer, x, y, old_contents, x + 1, y, right_contents
                                )
                        else:
                            if right_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer, x, y, old_contents, x + 1, y, right_contents
                                )
                            elif left_material.density < old_material.density:
                                modified = buffer_swap(
                                    buffer, x, y, old_contents, x - 1, y, left_contents
                                )
            # If nothing was modified, keep the old contents.
            # Materials.NONE should still be clean to allow for later movements.
            if not modified:
                buffer[y][x] = (
                    old_contents if old_contents != Materials.CLEAN else Materials.CLEAN
                )

    # Swap the buffers
    contents = buffer


def draw_at_mouse():
    """Draw the active material at the mouse position."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    col = mouse_x // CELL_SIZE
    row = mouse_y // CELL_SIZE
    draw_at_cell(col, row)


def draw_at_cell(x: int, y: int):
    """Draw the active material at the specified cell, using the brush radius."""
    for dx in range(brush_radius * 2 + 1):
        n_x = x - brush_radius + dx
        for dy in range(brush_radius * 2 + 1):
            n_y = y - brush_radius + dy
            if 0 <= n_x < BOARD_WIDTH and 0 <= n_y < BOARD_HEIGHT:
                contents[n_y][n_x] = active_material


if __name__ == "__main__":
    print("Starting main.py")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
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
                elif event.key == pygame.K_4:
                    active_material = Materials.OIL
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
        if drawing:
            draw_at_mouse()
        tick()

        draw_board(board_surface)

        screen.blit(
            pygame.transform.scale(board_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
        )
        pygame.display.flip()

        clock.tick(60)
