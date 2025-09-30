from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class ResourceRef:
    uri: str
    path: Optional[str] = None
    size: Optional[int] = None
    checksum: Optional[str] = None
    driver: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RasterInfo:
    path: str
    driver: Optional[str]
    crs: Optional[str]
    width: int
    height: int
    count: int
    dtype: Optional[str]
    transform: List[float]
    bounds: Tuple[float, float, float, float]
    nodata: Optional[float] = None
    overview_levels: List[int] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class VectorInfo:
    path: str
    driver: Optional[str]
    crs: Optional[str]
    layer_count: Optional[int] = None
    geometry_types: List[str] = field(default_factory=list)
    feature_count: Optional[int] = None
    fields: List[Tuple[str, str]] = field(default_factory=list)
