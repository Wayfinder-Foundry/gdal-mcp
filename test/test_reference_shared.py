from __future__ import annotations

from src.shared.reference import (
    Category,
    OpType,
    choose_resampling,
    get_common_crs,
    get_geospatial_glossary,
    list_compression_methods,
    list_resampling_methods,
    normalize_resampling,
    resampling_guide,
)


def test_common_crs_default_and_filtering() -> None:
    entries = get_common_crs()
    assert entries, "Expected default CRS list"
    coverage_values = {entry["coverage"] for entry in entries}
    assert "global" in coverage_values

    europe_entries = get_common_crs("europe")
    assert europe_entries
    assert all(entry["coverage"] == "europe" for entry in europe_entries)


def test_resampling_methods_filters() -> None:
    methods = list_resampling_methods()
    assert any(m["name"] == "NEAREST" for m in methods)

    categorical = list_resampling_methods(category="categorical")
    assert categorical
    assert all(m["category"] == Category.CATEGORICAL for m in categorical)

    aggregate = list_resampling_methods(op_type="aggregate")
    assert aggregate
    assert all(m["op_type"] == OpType.AGGREGATE for m in aggregate)


def test_resampling_normalize_and_choose() -> None:
    nearest = normalize_resampling("nearest")
    assert nearest is not None and nearest["gdal_name"] == "nearest"

    cubic_spline_alias = normalize_resampling("cubic-spline")
    assert cubic_spline_alias is not None and cubic_spline_alias["name"] == "CUBIC_SPLINE"

    categorical_down = choose_resampling(is_categorical=True, scale_ratio=0.5)
    assert categorical_down["name"] in {"MODE", "NEAREST"}

    continuous_up = choose_resampling(is_categorical=False, scale_ratio=2.0)
    assert continuous_up["name"] in {"LANCZOS", "CUBIC", "BILINEAR"}

    continuous_down = choose_resampling(is_categorical=False, scale_ratio=0.25)
    assert continuous_down["name"] in {"GAUSS", "AVERAGE", "CUBIC", "NEAREST"}


def test_resampling_guide() -> None:
    guide = resampling_guide()
    assert len(guide) >= 3

    nearest_entries = resampling_guide("nearest")
    assert nearest_entries and all("nearest" in entry["method"] for entry in nearest_entries)


def test_compression_methods() -> None:
    methods = list_compression_methods()
    assert methods
    names = {m["name"] for m in methods}
    assert "LZW" in names


def test_geospatial_glossary_filtering() -> None:
    glossary = get_geospatial_glossary()
    assert glossary
    terms = {entry["term"].lower() for entry in glossary}
    assert "crs" in terms

    filtered = get_geospatial_glossary("vector")
    assert filtered and all("vector" in entry["term"].lower() for entry in filtered)
