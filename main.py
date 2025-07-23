import random
import pygame
from material import DIAGONAL_DRIFT, SIDEWAYS_DRIFT
from materials import Materials, get_material

# Constants
# The dimensions of the board in cells
BOARD_WIDTH: int = 128
BOARD_HEIGHT: int = 128

# The size of each cell in pixels
CELL_SIZE: int = 4

# The dimensions of the screen in pixels
SCREEN_WIDTH: int = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT: int = BOARD_HEIGHT * CELL_SIZE

# The current state of the board
# Notably, this is row-major for access, while Pygame uses column-major for PixelArray
# This means that contents[y][x] corresponds to pxarray[x, y]
contents: list[list[Materials]] = [
    [Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
]

active_material: Materials = Materials.SAND
brush_radius: int = 1
drawing: bool = False
erasing: bool = False


def get_content(x: int, y: int) -> Materials:
    """Get the material at the given coordinates."""
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        return contents[y][x]
    return Materials.EDGE  # Return EDGE if out of bounds


def initialize_board() -> None:
    """Initialize the board with some default materials. Expects contents to be full of Materials.NONE."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            # if x == 2 and y == 2:
            #     contents[y][x] = Materials.HELIUM
            # continue
            # Fill the bottom with a layer of stone
            if y > BOARD_HEIGHT // 4 * 3:
                contents[y][x] = Materials.STONE
            elif 50 < x < 60:
                contents[y][x] = Materials.WALL
            else:
                if x < 10:
                    contents[y][x] = Materials.WATER
                elif x < 20:
                    contents[y][x] = Materials.SAND


def draw_board(surface: pygame.Surface) -> None:
    """Draw the board to the screen."""
    pxarray: pygame.PixelArray = pygame.PixelArray(surface)
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            material = get_material(get_content(x, y))
            pxarray[x, y] = material.color


def draw_mouse(screen: pygame.Surface) -> None:
    """Draw the active material at the mouse position."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    col: int = mouse_x // CELL_SIZE
    row: int = mouse_y // CELL_SIZE
    # Draw a circle around the cell to indicate the approximate brush radius
    if brush_radius > 0:
        pygame.draw.circle(
            screen,
            get_material(active_material).color,
            (col, row),
            brush_radius,
            1,
        )
    else:
        screen.set_at((col, row), get_material(active_material).color)


def buffer_swap(
    buffer: list[list[Materials]],
    x1: int,
    y1: int,
    contents1: Materials,
    x2: int,
    y2: int,
    contents2: Materials,
) -> bool:
    """
    Swap two cells in the buffer ONLY IF CLEAN.
    Returns False if the swap was not possible.
    """
    clean1 = buffer[y1][x1] == Materials.CLEAN  # or buffer[y1][x1] == Materials.NONE
    clean2 = buffer[y2][x2] == Materials.CLEAN  # or buffer[y2][x2] == Materials.NONE
    if not (clean1 and clean2):
        return False
    buffer[y1][x1] = contents2
    buffer[y2][x2] = contents1
    return True


def tick() -> None:
    """Update the board state for the next frame."""
    global contents
    buffer = [
        [Materials.CLEAN for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
    ]
    # For now, just copy the current contents to the buffer
    for y in range(BOARD_HEIGHT):
        left_or_right = random.randint(0, 1)  # Randomly check left or right first
        for x in (
            range(BOARD_WIDTH) if left_or_right == 0 else range(BOARD_WIDTH - 1, -1, -1)
        ):
            if buffer[y][x] != Materials.CLEAN:
                continue
            old_contents = get_content(x, y)
            old_material = get_material(old_contents)
            below_contents = get_content(x, y + 1)
            below_material = get_material(below_contents)
            modified = False
            if old_material.gravity:
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
                                elif (
                                    below_right_material.density < old_material.density
                                ):
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
                                        buffer,
                                        x,
                                        y,
                                        old_contents,
                                        x - 1,
                                        y,
                                        left_contents,
                                    )
                                elif right_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_contents,
                                        x + 1,
                                        y,
                                        right_contents,
                                    )
                            else:
                                if right_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_contents,
                                        x + 1,
                                        y,
                                        right_contents,
                                    )
                                elif left_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_contents,
                                        x - 1,
                                        y,
                                        left_contents,
                                    )
            # If nothing was modified, keep the old contents.
            # Materials.NONE should still be clean to allow for later movements.
            if not modified:
                buffer[y][x] = (
                    old_contents if old_contents != Materials.CLEAN else Materials.CLEAN
                )

    # Swap the buffers
    contents = buffer


def place_material_with_mouse(material: Materials = None) -> None:
    """Draw the active material at the mouse position."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    col: int = mouse_x // CELL_SIZE
    row: int = mouse_y // CELL_SIZE
    place_material_at_cell(col, row, material)


def place_material_at_cell(x: int, y: int, material: Materials = None) -> None:
    """
    Draw the given material at the specified cell, using the brush radius.
    Draws the active material if none is specified.
    """
    if material is None:
        material = active_material
    for dx in range(brush_radius * 2 + 1):
        n_x = x - brush_radius + dx
        for dy in range(brush_radius * 2 + 1):
            n_y = y - brush_radius + dy
            if (dx - brush_radius) ** 2 + (dy - brush_radius) ** 2 > brush_radius**2:
                continue
            if 0 <= n_x < BOARD_WIDTH and 0 <= n_y < BOARD_HEIGHT:
                contents[n_y][n_x] = material


if __name__ == "__main__":
    print("Starting main.py")
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    board_surface: pygame.Surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    clock: pygame.time.Clock = pygame.time.Clock()
    running: bool = True

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
                elif event.key == pygame.K_5:
                    active_material = Materials.HELIUM
                elif event.key == pygame.K_6:
                    active_material = Materials.WALL
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    drawing = True
                elif event.button == pygame.BUTTON_RIGHT:
                    erasing = True
                elif event.button == pygame.BUTTON_WHEELUP:
                    brush_radius = min(brush_radius + 1, 10)
                elif event.button == pygame.BUTTON_WHEELDOWN:
                    brush_radius = max(brush_radius - 1, 0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    drawing = False
                elif event.button == pygame.BUTTON_RIGHT:
                    erasing = False
        if drawing:
            place_material_with_mouse()
        elif erasing:
            place_material_with_mouse(Materials.NONE)
        tick()

        draw_board(board_surface)
        draw_mouse(board_surface)

        screen.blit(
            pygame.transform.scale(board_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
        )
        pygame.display.flip()

        clock.tick(60)
