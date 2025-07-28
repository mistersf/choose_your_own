import random
import pygame
from pygame import Color

from material import MaterialTypes, DriftTypes, get_material_data

# Constants
# The dimensions of the board in cells
BOARD_WIDTH: int = 128
BOARD_HEIGHT: int = 128

# The size of each cell in pixels
CELL_SIZE: int = 4

# The dimensions of the screen in pixels
SCREEN_WIDTH: int = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT: int = BOARD_HEIGHT * CELL_SIZE

STARTING_TEMPERATURE: float = 20.0

INSULATING_MATERIALS = [
    MaterialTypes.EDGE,
    MaterialTypes.NONE,
    MaterialTypes.WALL,
]

# The current state of the board
# Notably, this is row-major for access, while Pygame uses column-major for PixelArray
# This means that contents[y][x] corresponds to pxarray[x, y]
contents: list[list[MaterialTypes]] = [
    [MaterialTypes.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
]

temps: list[list[float]] = [
    [STARTING_TEMPERATURE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
]

active_material: MaterialTypes = MaterialTypes.SAND
brush_radius: int = 1
drawing: bool = False
erasing: bool = False
temp_overlay: bool = False


def get_material_id_at(x: int, y: int) -> MaterialTypes:
    """Get the material at the given coordinates."""
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        return contents[y][x]
    return MaterialTypes.EDGE  # Return EDGE if out of bounds


def get_temperature(x: int, y: int) -> float:
    """Get the temperature at the given coordinates."""
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        return temps[y][x]
    return STARTING_TEMPERATURE  # Return starting temperature if out of bounds


def initialize_board() -> None:
    """Initialize the board with some default materials. Expects contents to be full of Materials.NONE."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            # if x == 2 and y == 2:
            #     contents[y][x] = Materials.HELIUM
            # continue
            # Fill the bottom with a layer of stone
            if y > BOARD_HEIGHT // 4 * 3:
                contents[y][x] = MaterialTypes.STONE
            elif 50 < x < 60:
                contents[y][x] = MaterialTypes.WALL
            else:
                if x < 10:
                    contents[y][x] = MaterialTypes.WATER
                elif x < 20:
                    contents[y][x] = MaterialTypes.SAND


def draw_board(surface: pygame.Surface) -> None:
    """Draw the board to the screen."""
    pxarray: pygame.PixelArray = pygame.PixelArray(surface)
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if temp_overlay:
                # Draw temperature overlay
                temp = get_temperature(x, y)
                temp = max(
                    0, min(100, temp)
                )  # Clamp temperature to 0-100 for color mapping
                if temp < 10:
                    color = Color(0, 0, int(255 - temp * 25.5))
                elif temp > 90:
                    color = Color(int(255 - (100 - temp) * 25.5), 0, 0)
                else:
                    color = get_material_data(
                        get_material_id_at(x, y)
                    ).color.grayscale()
                pxarray[x, y] = color
            else:
                material = get_material_data(get_material_id_at(x, y))
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
            get_material_data(active_material).color,
            (col, row),
            brush_radius,
            1,
        )
    else:
        screen.set_at((col, row), get_material_data(active_material).color)


def draw_ui(screen: pygame.Surface) -> None:
    text_elements = [
        f"Material <1-0>: {active_material.name}",
        f"Brush Radius <scroll>: {brush_radius}",
        f"Temperature Overlay <F1>: {'On' if temp_overlay else 'Off'}",
    ]
    for i, text in enumerate(text_elements):
        screen.blit(
            OUTLINE_FONT.render(
                text,
                True,
                Color(0, 0, 0),
            ),
            (10, 10 + i * 20),
        )
        screen.blit(
            DEFAULT_FONT.render(
                text,
                True,
                Color(255, 255, 255),
            ),
            (9, 9 + i * 20),
        )


def buffer_swap(
    buffer: list[list[MaterialTypes]],
    x1: int,
    y1: int,
    contents1: MaterialTypes,
    x2: int,
    y2: int,
    contents2: MaterialTypes,
) -> bool:
    """
    Swap two cells in the buffer ONLY IF CLEAN.
    Returns False if the swap was not possible.
    """
    clean1 = (
        buffer[y1][x1] == MaterialTypes.CLEAN
    )  # or buffer[y1][x1] == Materials.NONE
    clean2 = (
        buffer[y2][x2] == MaterialTypes.CLEAN
    )  # or buffer[y2][x2] == Materials.NONE
    if not (clean1 and clean2):
        return False
    temp1 = get_temperature(x1, y1)
    temp2 = get_temperature(x2, y2)
    buffer[y1][x1] = contents2
    temps[y1][x1] = temp2
    buffer[y2][x2] = contents1
    temps[y2][x2] = temp1
    return True


def tick() -> None:
    """Update the board state for the next frame."""
    global contents, temps
    # Temperature conduction
    temps_buffer = [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            material_id = get_material_id_at(x, y)
            if material_id == MaterialTypes.HEATER:
                temps_buffer[y][x] = 150.0
                continue
            elif material_id == MaterialTypes.COOLER:
                temps_buffer[y][x] = -50.0
                continue
            new_temp = get_temperature(x, y)
            divisor = 1.0
            # 10% of the neighboring cells' temperatures are averaged in
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor_x = x + dx
                    neighbor_y = y + dy
                    neighbor_material_id = get_material_id_at(neighbor_x, neighbor_y)
                    thermal_conductivity = get_material_data(
                        neighbor_material_id
                    ).thermal_conductivity
                    if thermal_conductivity <= 0:
                        continue
                    new_temp += (
                        get_temperature(neighbor_x, neighbor_y) * thermal_conductivity
                    )
                    divisor += thermal_conductivity
            temps_buffer[y][x] = new_temp / divisor
    temps = temps_buffer
    # Melting and freezing
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            old_material_id = get_material_id_at(x, y)
            old_material = get_material_data(old_material_id)
            old_temperature = get_temperature(x, y)
            if old_material.melts_to is not None:
                if old_temperature >= old_material.melting_point:
                    # Melt the material
                    contents[y][x] = old_material.melts_to
            if old_material.freezes_to is not None:
                if old_temperature <= old_material.freezing_point:
                    # Freeze the material
                    contents[y][x] = old_material.freezes_to
    # Movement
    buffer = [
        [MaterialTypes.CLEAN for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
    ]
    for y in range(BOARD_HEIGHT):
        left_or_right = random.randint(0, 1)  # Randomly check left or right first
        for x in (
            range(BOARD_WIDTH) if left_or_right == 0 else range(BOARD_WIDTH - 1, -1, -1)
        ):
            if buffer[y][x] != MaterialTypes.CLEAN:
                continue
            old_material_id = get_material_id_at(x, y)
            old_material = get_material_data(old_material_id)
            below_material_id = get_material_id_at(x, y + 1)
            below_material = get_material_data(below_material_id)
            modified = False
            if old_material.gravity:
                # If the material is denser than the one below, swap them
                if old_material.density > below_material.density:
                    modified = buffer_swap(
                        buffer, x, y, old_material_id, x, y + 1, below_material_id
                    )
                else:
                    if random.random() > old_material.friction:
                        if not modified and old_material.drift in [
                            DriftTypes.DIAGONAL_DRIFT,
                            DriftTypes.SIDEWAYS_DRIFT,
                        ]:
                            # Drift down diagonally if possible
                            below_left_contents = get_material_id_at(x - 1, y + 1)
                            below_right_contents = get_material_id_at(x + 1, y + 1)
                            below_left_material = get_material_data(below_left_contents)
                            below_right_material = get_material_data(
                                below_right_contents
                            )
                            # Randomly check left or right first
                            if random.randint(0, 1) == 0:
                                if below_left_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_material_id,
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
                                        old_material_id,
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
                                        old_material_id,
                                        x + 1,
                                        y + 1,
                                        below_right_contents,
                                    )
                                elif below_left_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_material_id,
                                        x - 1,
                                        y + 1,
                                        below_left_contents,
                                    )
                        if not modified and old_material.drift in [
                            DriftTypes.SIDEWAYS_DRIFT
                        ]:
                            # Drift sideways if possible
                            left_contents = get_material_id_at(x - 1, y)
                            right_contents = get_material_id_at(x + 1, y)
                            left_material = get_material_data(left_contents)
                            right_material = get_material_data(right_contents)
                            if random.randint(0, 1) == 0:
                                if left_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_material_id,
                                        x - 1,
                                        y,
                                        left_contents,
                                    )
                                elif right_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_material_id,
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
                                        old_material_id,
                                        x + 1,
                                        y,
                                        right_contents,
                                    )
                                elif left_material.density < old_material.density:
                                    modified = buffer_swap(
                                        buffer,
                                        x,
                                        y,
                                        old_material_id,
                                        x - 1,
                                        y,
                                        left_contents,
                                    )
            # If nothing was modified, keep the old contents.
            # Materials.NONE should still be clean to allow for later movements.
            if not modified:
                buffer[y][x] = (
                    old_material_id
                    if old_material_id != MaterialTypes.CLEAN
                    else MaterialTypes.CLEAN
                )

    # Swap the buffers
    contents = buffer


def place_material_with_mouse(material: MaterialTypes = None) -> None:
    """Draw the active material at the mouse position."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    col: int = mouse_x // CELL_SIZE
    row: int = mouse_y // CELL_SIZE
    place_material_at_cell(col, row, material)


def place_material_at_cell(x: int, y: int, material: MaterialTypes = None) -> None:
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
                temps[n_y][n_x] = get_material_data(material).starting_temperature


if __name__ == "__main__":
    print("Starting main.py")
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    board_surface: pygame.Surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    clock: pygame.time.Clock = pygame.time.Clock()
    DEFAULT_FONT = pygame.font.SysFont("Arial", 16)
    OUTLINE_FONT = pygame.font.SysFont("Arial", 16, bold=True)
    running: bool = True

    initialize_board()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    temp_overlay = not temp_overlay
                elif event.key == pygame.K_1:
                    active_material = MaterialTypes.SAND
                elif event.key == pygame.K_2:
                    active_material = MaterialTypes.WATER
                elif event.key == pygame.K_3:
                    active_material = MaterialTypes.STONE
                elif event.key == pygame.K_4:
                    active_material = MaterialTypes.OIL
                elif event.key == pygame.K_5:
                    active_material = MaterialTypes.HELIUM
                elif event.key == pygame.K_6:
                    active_material = MaterialTypes.WALL
                elif event.key == pygame.K_7:
                    active_material = MaterialTypes.ICE
                elif event.key == pygame.K_8:
                    active_material = MaterialTypes.STEAM
                elif event.key == pygame.K_9:
                    active_material = MaterialTypes.LIQUID_NITROGEN
                elif event.key == pygame.K_0:
                    active_material = MaterialTypes.METAL
                elif event.key == pygame.K_MINUS:
                    active_material = MaterialTypes.HEATER
                elif event.key == pygame.K_EQUALS:
                    active_material = MaterialTypes.COOLER
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
            place_material_with_mouse(MaterialTypes.NONE)
        tick()

        draw_board(board_surface)
        draw_mouse(board_surface)

        screen.blit(
            pygame.transform.scale(board_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
        )

        draw_ui(screen)

        pygame.display.flip()

        clock.tick(60)
