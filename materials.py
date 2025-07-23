from pygame import Color
from material import Material, NO_DRIFT, DIAGONAL_DRIFT, SIDEWAYS_DRIFT
from enum import Enum


class Materials(Enum):
    CLEAN = -1  # Special value for unmodified buffer cell
    EDGE = 0
    NONE = 1
    STONE = 2
    SAND = 3
    WATER = 4
    OIL = 5


# Material flyweights for use in the game
_materials_data = {
    Materials.EDGE: Material("Edge", Color(0, 0, 0)).with_density(1000.0),
    Materials.NONE: Material("None", Color(0, 0, 0)).with_density(0.0),
    Materials.STONE: Material("Stone", Color(128, 128, 128)).with_density(10.0),
    Materials.SAND: Material("Sand", Color(255, 255, 0))
    .with_density(5.0)
    .with_drift(DIAGONAL_DRIFT),
    Materials.WATER: Material("Water", Color(0, 0, 255))
    .with_density(1.0)
    .with_drift(SIDEWAYS_DRIFT),
    Materials.OIL: Material("Oil", Color(255, 128, 0))
    .with_density(0.8)
    .with_drift(SIDEWAYS_DRIFT),
}


def get_material(material_type: Materials) -> Material:
    """Retrieve the material flyweight for the given material type."""
    return _materials_data.get(material_type, _materials_data[Materials.NONE])
