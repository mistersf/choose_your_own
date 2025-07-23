import random
import pygame
from pygame import Color

from constants import NO_DRIFT, DIAGONAL_DRIFT, SIDEWAYS_DRIFT
from materials import Materials
from material import Material

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
    Materials.EDGE,
    Materials.NONE,
    Materials.WALL,
]

# Material flyweights for use in the game
_materials_data = {
    Materials.EDGE: Material("Edge", Color(0, 0, 0))
    .with_density(1000.0)
    .with_gravity(False)
    .with_thermal_conductivity(0.0),
    Materials.NONE: Material("None", Color(0, 0, 0))
    .with_density(0.0)
    .with_drift(SIDEWAYS_DRIFT)
    .with_friction(0.5)
    .with_thermal_conductivity(0.01),
    Materials.STONE: Material("Stone", Color(128, 128, 128)).with_density(10.0),
    Materials.SAND: Material("Sand", Color(255, 255, 0))
    .with_density(5.0)
    .with_drift(DIAGONAL_DRIFT)
    .with_friction(0.7),
    Materials.WATER: Material("Water", Color(0, 0, 255))
    .with_density(1.0)
    .with_drift(SIDEWAYS_DRIFT)
    .with_friction(0.5)
    .with_melting_point(100.0, Materials.STEAM)
    .with_freezing_point(0.0, Materials.ICE),
    Materials.OIL: Material("Oil", Color(255, 128, 0))
    .with_density(0.8)
    .with_drift(SIDEWAYS_DRIFT)
    .with_friction(0.0),
    Materials.HELIUM: Material("Helium", Color(255, 128, 255))
    .with_density(-1.0)
    .with_drift(SIDEWAYS_DRIFT)
    .with_friction(0.0),
    Materials.WALL: Material("Wall", Color(64, 64, 64))
    .with_density(1000.0)
    .with_drift(NO_DRIFT)
    .with_friction(1.0)
    .with_gravity(False)
    .with_thermal_conductivity(0.0),
    Materials.ICE: Material("Ice", Color(173, 216, 230))
    .with_density(0.9)
    .with_drift(NO_DRIFT)
    .with_friction(1.0)
    .with_melting_point(1.0, Materials.WATER)
    .with_starting_temperature(-5.0),
    Materials.STEAM: Material("Steam", Color(255, 255, 255))
    .with_density(-0.1)
    .with_freezing_point(99.0, Materials.WATER)
    .with_starting_temperature(105.0),
    Materials.LIQUID_NITROGEN: Material("Liquid Nitrogen", Color(173, 222, 255))
    .with_density(0.8)
    .with_drift(SIDEWAYS_DRIFT)
    .with_friction(0.0)
    .with_melting_point(0.0, Materials.NONE)  # TODO add nitrogen gas?
    .with_starting_temperature(-196.0),
    Materials.METAL: Material("Metal", Color(192, 192, 192))
    .with_density(10.0)
    .with_drift(NO_DRIFT)
    .with_friction(1.0)
    .with_thermal_conductivity(1.0),
}


def get_material(material_type: Materials) -> Material:
    """Retrieve the material flyweight for the given material type."""
    return _materials_data.get(material_type, _materials_data[Materials.NONE])


# The current state of the board
# Notably, this is row-major for access, while Pygame uses column-major for PixelArray
# This means that contents[y][x] corresponds to pxarray[x, y]
contents: list[list[Materials]] = [
    [Materials.NONE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
]

temps: list[list[float]] = [
    [STARTING_TEMPERATURE for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
]

active_material: Materials = Materials.SAND
brush_radius: int = 1
drawing: bool = False
erasing: bool = False
temp_overlay: bool = False


def get_material_id_at(x: int, y: int) -> Materials:
    """Get the material at the given coordinates."""
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        return contents[y][x]
    return Materials.EDGE  # Return EDGE if out of bounds


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
                    color = get_material(get_material_id_at(x, y)).color.grayscale()
                pxarray[x, y] = color
            else:
                material = get_material(get_material_id_at(x, y))
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
            if get_material_id_at(x, y) in INSULATING_MATERIALS:
                temps_buffer[y][x] = STARTING_TEMPERATURE
                continue
            # TODO better temp shifting (conductivity?)
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
                    if neighbor_material_id in INSULATING_MATERIALS:
                        continue
                    thermal_conductivity = get_material(
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
            old_material = get_material(old_material_id)
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
        [Materials.CLEAN for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
    ]
    for y in range(BOARD_HEIGHT):
        left_or_right = random.randint(0, 1)  # Randomly check left or right first
        for x in (
            range(BOARD_WIDTH) if left_or_right == 0 else range(BOARD_WIDTH - 1, -1, -1)
        ):
            if buffer[y][x] != Materials.CLEAN:
                continue
            old_material_id = get_material_id_at(x, y)
            old_material = get_material(old_material_id)
            below_material_id = get_material_id_at(x, y + 1)
            below_material = get_material(below_material_id)
            modified = False
            if old_material.gravity:
                # If the material is denser than the one below, swap them
                if old_material.density > below_material.density:
                    modified = buffer_swap(
                        buffer, x, y, old_material_id, x, y + 1, below_material_id
                    )
                else:
                    if random.random() > old_material.friction:
                        if not modified and old_material.drift >= DIAGONAL_DRIFT:
                            # Drift down diagonally if possible
                            below_left_contents = get_material_id_at(x - 1, y + 1)
                            below_right_contents = get_material_id_at(x + 1, y + 1)
                            below_left_material = get_material(below_left_contents)
                            below_right_material = get_material(below_right_contents)
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
                        if not modified and old_material.drift >= SIDEWAYS_DRIFT:
                            # Drift sideways if possible
                            left_contents = get_material_id_at(x - 1, y)
                            right_contents = get_material_id_at(x + 1, y)
                            left_material = get_material(left_contents)
                            right_material = get_material(right_contents)
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
                    if old_material_id != Materials.CLEAN
                    else Materials.CLEAN
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
                temps[n_y][n_x] = get_material(material).starting_temperature


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
                if event.key == pygame.K_F1:
                    temp_overlay = not temp_overlay
                elif event.key == pygame.K_1:
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
                elif event.key == pygame.K_7:
                    active_material = Materials.ICE
                elif event.key == pygame.K_8:
                    active_material = Materials.STEAM
                elif event.key == pygame.K_9:
                    active_material = Materials.LIQUID_NITROGEN
                elif event.key == pygame.K_0:
                    active_material = Materials.METAL
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
