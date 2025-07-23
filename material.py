from pygame import Color

NO_DRIFT = 0
DIAGONAL_DRIFT = 1
SIDEWAYS_DRIFT = 2


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

    def __repr__(self):
        return f"Material(name={self.name}, color={self.color}, density={self.density}, drift={self.drift})"
