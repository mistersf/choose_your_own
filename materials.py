from pygame import Color
from enum import Enum


class Materials(Enum):
    CLEAN = -1  # Special value for unmodified buffer cell
    EDGE = 0
    NONE = 1
    STONE = 2
    SAND = 3
    WATER = 4
    OIL = 5
    HELIUM = 6
    WALL = 7
    ICE = 8
    STEAM = 9
    LIQUID_NITROGEN = 10
    METAL = 11
