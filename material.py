from pygame import Color


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
    """ Friction coefficient from 0.0 (no friction) to 1.0 (perfect friction) """
    friction: float = 0.0

    def __init__(self, name: str, color: Color):
        self.name = name
        self.color = color

    def friction(self, friction: float):
        """Chainable setter for friction"""
        self.friction = max(0.0, min(friction, 1.0))
        return self

    def __repr__(self):
        return (
            f"Material(name={self.name}, color={self.color}, friction={self.friction})"
        )
