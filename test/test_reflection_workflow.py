"""Integration tests for end-to-end reflection workflow."""

from __future__ import annotations

from typing import Any

import pytest
from fastmcp.exceptions import ToolError

from src.middleware.reflection_store import get_store
from src.prompts.justification import Choice, Justification


@pytest.mark.asyncio
async def test_single_reflection_workflow(tmp_path, monkeypatch):
    """Test complete workflow: block → re-invoke with __reflection → success."""

    # Use isolated store for this test
    from src.middleware.reflection_store import DiskStore

    test_store = DiskStore(root=str(tmp_path / "reflections"))
    monkeypatch.setattr("src.middleware.reflection_store._DEFAULT_STORE", test_store)
    monkeypatch.setattr("src.middleware.preflight.get_store", lambda: test_store)

    # Mock a simple tool with single reflection requirement
    from src.middleware.preflight import requires_reflection

    @requires_reflection(
        {
            "prompt_name": "justify_crs_selection",
            "domain": "crs_datum",
            "args_fn": lambda args: {
                "source_crs": args.get("src_crs", "EPSG:4326"),
                "target_crs": args.get("dst_crs", "EPSG:32610"),
                "operation_context": "test",
                "data_type": "raster",
            },
        }
    )
    async def mock_tool(
        src_crs: str,
        dst_crs: str,
        __reflection: dict[str, Any] | None = None,
    ) -> str:
        return f"Reprojected from {src_crs} to {dst_crs}"

    # Step 1: Attempt operation without reflection - should block
    with pytest.raises(ToolError) as exc_info:
        await mock_tool(src_crs="EPSG:4326", dst_crs="EPSG:32610")

    # Step 2: Extract hint from error message
    import json

    error_msg = str(exc_info.value)
    json_start = error_msg.find("{")
    json_data = json.loads(error_msg[json_start:])
    hint = json_data["hint"]
    assert hint["tool"] == "mock_tool"  # Tool name for re-invocation
    assert hint["prompt"] == "justify_crs_selection"
    assert hint["domain"] == "crs_datum"
    assert "hash" in hint
    assert hint["prompt_args"]["target_crs"] == "EPSG:32610"

    # Step 3: Re-invoke with __reflection (simulating model's response)
    justification_json = {
        "intent": "Preserve distance accuracy for flow calculations",
        "alternatives": [{"method": "EPSG:3310", "why_not": "Albers distorts distance"}],
        "choice": {
            "method": "EPSG:32610",
            "rationale": "UTM Zone 10N minimizes distortion",
            "tradeoffs": "Zone boundary artifacts",
        },
        "confidence": "medium",
    }

    result = await mock_tool(
        src_crs="EPSG:4326",
        dst_crs="EPSG:32610",
        __reflection={
            "hash": hint["hash"],
            "domain": hint["domain"],
            "justification": justification_json,
        },
    )

    # Should succeed and persist
    assert "Reprojected" in result

    # Verify persistence
    assert test_store.has(hint["hash"], hint["domain"])

    # Step 4: Subsequent call should use cache (no __reflection needed)
    final_result = await mock_tool(src_crs="EPSG:4326", dst_crs="EPSG:32610")
    assert "Reprojected" in final_result


@pytest.mark.asyncio
async def test_chained_reflection_workflow(tmp_path, monkeypatch):
    """Test workflow for multi-risk operation requiring 2 reflections via re-invocation."""

    # Use isolated store for this test
    from src.middleware.reflection_store import DiskStore

    test_store = DiskStore(root=str(tmp_path / "reflections"))
    monkeypatch.setattr("src.middleware.reflection_store._DEFAULT_STORE", test_store)
    monkeypatch.setattr("src.middleware.preflight.get_store", lambda: test_store)

    from src.middleware.preflight import requires_reflection

    @requires_reflection(
        [
            {
                "prompt_name": "justify_crs_selection",
                "domain": "crs_datum",
                "args_fn": lambda args: {
                    "source_crs": args.get("src_crs"),
                    "target_crs": args.get("dst_crs"),
                    "operation_context": "reproject",
                    "data_type": "raster",
                },
            },
            {
                "prompt_name": "justify_resampling_method",
                "domain": "resampling",
                "args_fn": lambda args: {
                    "data_type": "raster",
                    "method": args.get("resampling"),
                    "source_resolution": "original",
                    "target_resolution": "resampled",
                    "operation_context": "reprojection resampling",
                },
            },
        ]
    )
    async def mock_reproject(
        src_crs: str,
        dst_crs: str,
        resampling: str,
        __reflection: dict[str, Any] | None = None,
    ) -> str:
        return f"Reprojected with {resampling}"

    # Step 1: Attempt operation - should require first reflection
    with pytest.raises(ToolError) as exc_info:
        await mock_reproject(src_crs="EPSG:4326", dst_crs="EPSG:32610", resampling="bilinear")

    import json

    error_msg = str(exc_info.value)
    json_start = error_msg.find("{")
    json_data = json.loads(error_msg[json_start:])
    hint1 = json_data["hint"]
    assert hint1["tool"] == "mock_reproject"
    assert hint1["prompt"] in ["justify_crs_selection", "justify_resampling_method"]
    assert "remaining_reflections" in hint1  # Indicates multi-risk
    assert hint1["remaining_reflections"] == 1

    # Step 2: Re-invoke with first reflection - should persist & block for second
    with pytest.raises(ToolError) as exc_info2:
        await mock_reproject(
            src_crs="EPSG:4326",
            dst_crs="EPSG:32610",
            resampling="bilinear",
            __reflection={
                "hash": hint1["hash"],
                "domain": hint1["domain"],
                "justification": {
                    "intent": "Preserve property X",
                    "alternatives": [],
                    "choice": {"method": "Y", "rationale": "because", "tradeoffs": "none"},
                    "confidence": "high",
                },
            },
        )

    # Verify first reflection was persisted
    assert test_store.has(hint1["hash"], hint1["domain"])

    # Step 3: Extract hint for second reflection

    error_msg2 = str(exc_info2.value)
    json_start2 = error_msg2.find("{")
    json_data2 = json.loads(error_msg2[json_start2:])
    hint2 = json_data2["hint"]
    assert hint2["prompt"] != hint1["prompt"]  # Different reflection
    assert hint2["domain"] != hint1["domain"]

    # Step 4: Re-invoke with second reflection
    result2 = await mock_reproject(
        src_crs="EPSG:4326",
        dst_crs="EPSG:32610",
        resampling="bilinear",
        __reflection={
            "hash": hint2["hash"],
            "domain": hint2["domain"],
            "justification": {
                "intent": "Preserve property Z",
                "alternatives": [{"method": "nearest", "why_not": "blocky"}],
                "choice": {
                    "method": "bilinear",
                    "rationale": "smooth",
                    "tradeoffs": "interpolates",
                },
                "confidence": "medium",
            },
        },
    )

    # Should succeed now
    assert "bilinear" in result2

    # Step 5: Subsequent call should use cache
    result3 = await mock_reproject(src_crs="EPSG:4326", dst_crs="EPSG:32610", resampling="bilinear")
    assert "bilinear" in result3


@pytest.mark.asyncio
async def test_cache_hit_workflow(tmp_path):
    """Verify cached justifications allow execution without blocking."""

    from src.middleware.preflight import (
        _hash_prompt_content,
        _normalize_prompt_args,
        _stable_hash,
        requires_reflection,
    )

    # Pre-populate cache
    store = get_store()
    justification = Justification(
        intent="Test intent",
        alternatives=[],
        choice=Choice(method="test", rationale="test", tradeoffs="none"),
        confidence="high",
    )

    # Calculate the hash that will be generated
    prompt_args = {
        "source_crs": "EPSG:4326",
        "target_crs": "EPSG:32610",
        "operation_context": "test",
        "data_type": "raster",
    }
    prompt_name = "justify_crs_selection"
    normalized_args = _normalize_prompt_args(prompt_args)
    prompt_hash = _hash_prompt_content(prompt_name)
    hash_key = _stable_hash("mock_cached_tool", normalized_args, "crs_datum", prompt_hash)

    # Store the justification
    domain = "crs_datum"
    store.put(hash_key, justification, domain)

    # Create tool
    @requires_reflection(
        {
            "prompt_name": prompt_name,
            "domain": "crs_datum",
            "args_fn": lambda _args: dict(prompt_args),
        }
    )
    async def mock_cached_tool(
        __reflection: dict[str, Any] | None = None,
    ) -> str:
        return "success"

    # Tool should execute without ToolError (cache hit)
    result = await mock_cached_tool()
    assert result == "success"


def test_invalid_justification_schema():
    """Verify pydantic validates justification schema correctly."""

    # Invalid: confidence not in allowed values
    with pytest.raises(ValueError):
        Justification(
            intent="test",
            alternatives=[],
            choice=Choice(method="x", rationale="y", tradeoffs="z"),
            confidence="invalid_value",  # type: ignore[arg-type]
        )


def test_low_confidence_accepted() -> None:
    """Verify low-confidence justifications are accepted."""

    just = Justification(
        intent="Uncertain choice",
        alternatives=[],
        choice=Choice(method="x", rationale="guessing", tradeoffs="many"),
        confidence="low",
    )

    assert just.confidence == "low"

    # Verify it can be persisted
    store = get_store()
    path = store.put("sha256:test_low", just, "test_domain")
    assert path.exists()
