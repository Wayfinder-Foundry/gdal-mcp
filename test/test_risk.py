from __future__ import annotations

from src.prompts.risk import RiskClass, classify, input_hash


def test_classify_crs_by_tool_name() -> None:
    risk = classify("raster.reproject", {})
    assert risk is RiskClass.CRS_DATUM


def test_classify_crs_by_arguments() -> None:
    risk = classify("tools.custom", {"target_crs": "EPSG:4326"})
    assert risk is RiskClass.CRS_DATUM


def test_classify_resampling() -> None:
    risk = classify("raster.resample", {"method": "bilinear"})
    assert risk is RiskClass.RESAMPLING


def test_classify_hydrology() -> None:
    risk = classify("terrain.flow_direction", {"flowdir": "d8"})
    assert risk is RiskClass.HYDROLOGY


def test_classify_aggregation() -> None:
    risk = classify("vector.zonal_stats", {"stat": "mean"})
    assert risk is RiskClass.AGGREGATION


def test_classify_none() -> None:
    risk = classify("vector.buffer", {"distance": 10})
    assert risk is RiskClass.NONE


def test_input_hash_includes_risk_and_tool() -> None:
    risk = RiskClass.CRS_DATUM
    hash_one = input_hash(risk, "raster.reproject", {"dst_crs": "EPSG:3857"})
    hash_two = input_hash(risk, "raster.reproject", {"dst_crs": "EPSG:3857"})
    assert hash_one == hash_two
    assert hash_one.startswith("sha256:")


def test_input_hash_ignores_irrelevant_args() -> None:
    risk = RiskClass.CRS_DATUM
    baseline = input_hash(risk, "raster.reproject", {"dst_crs": "EPSG:3857"})
    with_extra = input_hash(
        risk,
        "raster.reproject",
        {"dst_crs": "EPSG:3857", "output_path": "out.tif"},
    )
    assert baseline == with_extra


def test_input_hash_sensitive_to_relevant_args() -> None:
    risk = RiskClass.RESAMPLING
    nearest = input_hash(risk, "raster.resample", {"method": "nearest"})
    cubic = input_hash(risk, "raster.resample", {"method": "cubic"})
    assert nearest != cubic


def test_input_hash_order_insensitive() -> None:
    risk = RiskClass.AGGREGATION
    args_a = {"stat": "mean", "zone_layer": "zones.gpkg"}
    args_b = {"zone_layer": "zones.gpkg", "stat": "mean"}
    hash_a = input_hash(risk, "vector.zonal_stats", args_a)
    hash_b = input_hash(risk, "vector.zonal_stats", args_b)
    assert hash_a == hash_b
