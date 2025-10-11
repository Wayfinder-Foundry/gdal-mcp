from enum import Enum


class String(str, Enum):
    """Base class for string-backed enumerations."""

    def __new__(cls, value: str) -> "String":
        """Create a new string-based enum member."""
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
