from .float import Float


class Percentile(Float):
    """
    Enumeration representing common percentiles.

    This class provides an enumeration of common percentiles often used in
    statistical computations or data analysis. Each enum member has a
    corresponding float value representing its percentage.

    Attributes
    ----------
    P10 : float
        Represents the 10th percentile.
    P25 : float
        Represents the 25th percentile.
    P50 : float
        Represents the 50th percentile (median).
    P75 : float
        Represents the 75th percentile.
    P90 : float
        Represents the 90th percentile.
    P95 : float
        Represents the 95th percentile.
    P99 : float
        Represents the 99th percentile.
    """

    P10 = 10.0
    P25 = 25.0
    P50 = 50.0
    P75 = 75.0
    P90 = 90.0
    P95 = 95.0
    P99 = 99.0

    @classmethod
    def all(cls) -> tuple[float, ...]:
        """Return all percentile values as floats."""
        return tuple(float(member.value) for member in cls)

    def __float__(self) -> float:
        """Return the float value represented by this percentile."""
        return self.value

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Percentile.{self.name}"

    def __str__(self) -> str:
        """Return a human-readable representation."""
        return f"{self.name} ({self.value}%)"
