from pygame import Color
from material import Material
from enum import Enum


class Materials(Enum):
    NONE = 0
    STONE = 1
    SAND = 2
    WATER = 3


# Material flyweights for use in the game
_materials_data = {
    Materials.NONE: Material("None", Color(0, 0, 0)).friction(0.0),
    Materials.STONE: Material("Stone", Color(128, 128, 128)).friction(1.0),
    Materials.SAND: Material("Sand", Color(255, 255, 0)).friction(0.4),
    Materials.WATER: Material("Water", Color(0, 0, 255)).friction(0.0),
}


def get_material(material_type: Materials) -> Material:
    """Retrieve the material flyweight for the given material type."""
    return _materials_data.get(material_type, _materials_data[Materials.NONE])
