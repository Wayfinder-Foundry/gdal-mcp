from enum import Enum


class Float(float, Enum):
    """
    Base class for float-based enumerations.

    This class provides a base for creating enumerations that are based on float values.
    It ensures that each enum member has a corresponding float value and provides
    methods for accessing and representing these values.
    """

    def __new__(cls, value: float) -> "Float":
        """Create a new float-based enum member."""
        obj = float.__new__(cls, value)
        obj._value_ = value
        return obj
