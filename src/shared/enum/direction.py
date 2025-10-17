"""Directional enumerations for spatial extent metadata."""

from .string import String


class Cardinal(String):
    """Cardinal directions for spatial extent bounds."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Relative(String):
    """Relative directions for spatial extent bounds."""

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
