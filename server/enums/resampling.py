"""GDAL resampling methods enum."""

from enum import Enum
from typing import Tuple


class Resampling(Enum):
    """GDAL resampling methods."""
    NEAREST = "near"
    BILINEAR = "bilinear" 
    CUBIC = "cubic"
    CUBICSPLINE = "cubicspline"
    LANCZOS = "lanczos"
    AVERAGE = "average"
    MODE = "mode"
    
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return (cls.NEAREST.value, cls.BILINEAR.value, cls.CUBIC.value, 
                cls.CUBICSPLINE.value, cls.LANCZOS.value, cls.AVERAGE.value, 
                cls.MODE.value)
    
    @classmethod
    def exists(cls, method: str) -> bool:
        return method in cls.all()