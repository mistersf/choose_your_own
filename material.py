from pygame import Color
from enum import Enum


class DriftTypes(Enum):
    NO_DRIFT = 0
    DIAGONAL_DRIFT = 1
    SIDEWAYS_DRIFT = 2


class MaterialTypes(Enum):
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


class Material:
    """
    A representation of a material in the game.
    Used as a flyweight!
    """

    # Name and Visuals
    """ Display name of the material """
    name: str = ""
    """ Color of the material, used for rendering """
    color: Color = Color(0, 0, 0)

    # Physics
    """ Density of the material, used for falling checks"""
    density: float = 1.0
    """ Does this material move sideways or diagonally?
    0 = moves down only
    1 = moves down and diagonally
    2 = moves down, diagonally, and sideways
    """
    drift: int = 0

    """ "Friction" of the material, used for falling checks.
    The probability that the material will not fall left or right (diagonally or sideways).
    0.0 means no friction (always falls), 1.0 means maximum friction (never falls sideways).
    Note that drift must be set to 1 or 2 for this to have an effect.
    A value between 0.0 (no friction) and 1.0 (maximum friction).
    """
    friction: float = 0.5

    """ Is this material affected by gravity?"""
    gravity: bool = True

    """ What temperature does this material melt at? 
    Requires melt_to to be set to a valid material."""
    melting_point: float = 0.0
    """ What material does this material melt into when heated?
    If None, the material does not melt."""
    melts_to: MaterialTypes = None

    """ What temperature does this material freeze at? 
    Requires freezes_to to be set to a valid material."""
    freezing_point: float = 0.0
    """ What material does this material freeze into when heated?
    If None, the material does not melt."""
    freezes_to: MaterialTypes = None

    starting_temperature: float = 20.0
    thermal_conductivity: float = 0.1

    def __init__(self, name: str, color: Color):
        self.name = name
        self.color = color

    def with_density(self, density: float):
        """Chainable setter for density"""
        self.density = density
        return self

    def with_drift(self, drift: int):
        """Chainable setter for drift"""
        self.drift = drift
        return self

    def with_friction(self, friction: float):
        """Chainable setter for friction"""
        self.friction = max(0.0, min(1.0, friction))
        return self

    def with_gravity(self, gravity: bool):
        """Chainable setter for gravity"""
        self.gravity = gravity
        return self

    def with_melting_point(self, melting_point: float, melts_to: MaterialTypes):
        """Chainable setter for melting point and melts_to"""
        self.melting_point = melting_point
        self.melts_to = melts_to
        return self

    def with_freezing_point(self, freezing_point: float, freezes_to: MaterialTypes):
        """Chainable setter for freezing point and freezes_to"""
        self.freezing_point = freezing_point
        self.freezes_to = freezes_to
        return self

    def with_starting_temperature(self, starting_temperature: float):
        """Chainable setter for starting temperature"""
        self.starting_temperature = starting_temperature
        return self

    def with_thermal_conductivity(self, thermal_conductivity: float):
        """Chainable setter for thermal conductivity"""
        self.thermal_conductivity = thermal_conductivity
        return self

    def __repr__(self):
        return f"Material(name={self.name}, color={self.color}, density={self.density}, drift={self.drift})"
