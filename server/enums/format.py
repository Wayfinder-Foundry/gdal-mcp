"""GDAL raster formats enum."""

from enum import Enum
from typing import Tuple


class Format(Enum):
    """Common GDAL raster formats."""
    GTIFF = "GTiff"
    PNG = "PNG"
    JPEG = "JPEG"
    HFA = "HFA"
    ENVI = "ENVI"
    NETCDF = "NetCDF"
    VRT = "VRT"
    
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return (cls.GTIFF.value, cls.PNG.value, cls.JPEG.value, cls.HFA.value, 
                cls.ENVI.value, cls.NETCDF.value, cls.VRT.value)
    
    @classmethod
    def supported(cls, fmt: str) -> bool:
        return fmt in cls.all()