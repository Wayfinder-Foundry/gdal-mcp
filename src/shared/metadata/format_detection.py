"""Format detection and metadata extraction for geospatial datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # Optional dependency
    import pyogrio
except ImportError:  # pragma: no cover - optional
    pyogrio = None  # type: ignore

try:  # Optional dependency
    import fiona  # type: ignore
except ImportError:  # pragma: no cover - optional
    fiona = None  # type: ignore

try:  # Optional dependency
    import rasterio
    from rasterio.errors import RasterioIOError
except ImportError:  # pragma: no cover - optional
    rasterio = None  # type: ignore
    RasterioIOError = Exception  # type: ignore


def read_format_metadata(path: str) -> dict[str, Any]:
    """Inspect a dataset and return driver/format characteristics."""
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(path)

    base: dict[str, Any] = {
        "path": str(resolved),
        "name": resolved.name,
        "suffix": resolved.suffix.lower(),
        "size": resolved.stat().st_size,
    }

    raster_info = _try_rasterio(resolved)
    if raster_info is not None:
        return {**base, **raster_info}

    vector_info = _try_vector(resolved)
    if vector_info is not None:
        return {**base, **vector_info}

    base.update(
        {
            "category": "unknown",
            "driver": None,
            "driver_description": None,
            "details": {},
        }
    )
    return base


def _try_rasterio(resolved: Path) -> dict[str, Any] | None:
    if rasterio is None:
        return None
    try:
        with rasterio.Env(), rasterio.open(resolved) as dataset:
            dtype = dataset.dtypes[0] if dataset.count > 0 and dataset.dtypes else None
            details = {
                "band_count": dataset.count,
                "dtype": dtype,
                "width": dataset.width,
                "height": dataset.height,
            }
            return {
                "category": "raster",
                "driver": dataset.driver,
                "driver_description": getattr(dataset, "driver_description", None),
                "details": details,
            }
    except RasterioIOError:
        return None


def _try_vector(resolved: Path) -> dict[str, Any] | None:
    if pyogrio is not None:
        try:
            info = pyogrio.read_info(resolved)
            return {
                "category": "vector",
                "driver": info.get("driver"),
                "driver_description": info.get("driver_description"),
                "details": {
                    "layer_count": info.get("layer_count", 1),
                    "geometry_type": info.get("geometry_type"),
                },
            }
        except Exception:
            pass

    if fiona is not None:
        try:
            with fiona.open(resolved) as collection:
                return {
                    "category": "vector",
                    "driver": collection.driver,
                    "driver_description": None,
                    "details": {
                        "layer_count": 1,
                        "schema": collection.schema,
                    },
                }
        except Exception:
            pass

    return None
