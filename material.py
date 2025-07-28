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
    HEATER = 12
    COOLER = 13


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


# Material flyweights for use in the game
_materials_data = {
    MaterialTypes.EDGE: Material("Edge", Color(0, 0, 0))
    .with_density(1000.0)
    .with_gravity(False)
    .with_thermal_conductivity(0.0),
    MaterialTypes.NONE: Material("None", Color(0, 0, 0))
    .with_density(0.0)
    .with_drift(DriftTypes.SIDEWAYS_DRIFT)
    .with_friction(0.5)
    .with_thermal_conductivity(0.01),
    MaterialTypes.STONE: Material("Stone", Color(128, 128, 128)).with_density(10.0),
    MaterialTypes.SAND: Material("Sand", Color(255, 255, 0))
    .with_density(5.0)
    .with_drift(DriftTypes.DIAGONAL_DRIFT)
    .with_friction(0.7),
    MaterialTypes.WATER: Material("Water", Color(0, 0, 255))
    .with_density(1.0)
    .with_drift(DriftTypes.SIDEWAYS_DRIFT)
    .with_friction(0.5)
    .with_melting_point(100.0, MaterialTypes.STEAM)
    .with_freezing_point(0.0, MaterialTypes.ICE),
    MaterialTypes.OIL: Material("Oil", Color(255, 128, 0))
    .with_density(0.8)
    .with_drift(DriftTypes.SIDEWAYS_DRIFT)
    .with_friction(0.0),
    MaterialTypes.HELIUM: Material("Helium", Color(255, 128, 255))
    .with_density(-1.0)
    .with_drift(DriftTypes.SIDEWAYS_DRIFT)
    .with_friction(0.0),
    MaterialTypes.WALL: Material("Wall", Color(64, 64, 64))
    .with_density(1000.0)
    .with_drift(DriftTypes.NO_DRIFT)
    .with_friction(1.0)
    .with_gravity(False)
    .with_thermal_conductivity(0.0),
    MaterialTypes.ICE: Material("Ice", Color(173, 216, 230))
    .with_density(0.9)
    .with_drift(DriftTypes.NO_DRIFT)
    .with_friction(1.0)
    .with_melting_point(5.0, MaterialTypes.WATER)
    .with_starting_temperature(-25.0),
    MaterialTypes.STEAM: Material("Steam", Color(255, 255, 255))
    .with_density(-0.1)
    .with_freezing_point(95.0, MaterialTypes.WATER)
    .with_starting_temperature(125.0),
    MaterialTypes.LIQUID_NITROGEN: Material("Liquid Nitrogen", Color(173, 222, 255))
    .with_density(0.8)
    .with_drift(DriftTypes.SIDEWAYS_DRIFT)
    .with_friction(0.0)
    .with_melting_point(0.0, MaterialTypes.NONE)  # TODO add nitrogen gas?
    .with_starting_temperature(-196.0),
    MaterialTypes.METAL: Material("Metal", Color(192, 192, 192))
    .with_density(10.0)
    .with_drift(DriftTypes.NO_DRIFT)
    .with_friction(1.0)
    .with_gravity(False)
    .with_thermal_conductivity(1.0),
    MaterialTypes.HEATER: Material("Heater", Color(255, 0, 0))
    .with_density(1000.0)
    .with_drift(DriftTypes.NO_DRIFT)
    .with_friction(1.0)
    .with_gravity(False)
    .with_thermal_conductivity(1.0)
    .with_starting_temperature(150.0),
    MaterialTypes.COOLER: Material("Cooler", Color(72, 72, 255))
    .with_density(1000.0)
    .with_drift(DriftTypes.NO_DRIFT)
    .with_friction(1.0)
    .with_gravity(False)
    .with_thermal_conductivity(1.0)
    .with_starting_temperature(-50.0),
}


def get_material_data(material_type: MaterialTypes) -> Material:
    """Retrieve the material flyweight for the given material type."""
    return _materials_data.get(material_type, _materials_data[MaterialTypes.NONE])
