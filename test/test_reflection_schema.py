from __future__ import annotations

from pathlib import Path

import pytest

from src.prompts.justification import Alternative, Choice, Justification


@pytest.fixture
def sample_justification() -> Justification:
    return Justification(
        intent="Preserve distance accuracy for hydrologic flow calculations",
        alternatives=[
            Alternative(
                method="EPSG:3310",
                why_not="Albers distorts distance in small basins",
            ),
            Alternative(
                method="EPSG:4326",
                why_not="Geographic CRS lacks equal-distance projection",
            ),
        ],
        choice=Choice(
            method="EPSG:32610",
            rationale="UTM Zone 10N minimizes distance distortion within watershed extent",
            tradeoffs="Zone boundary artifacts if watershed crosses into Zone 11",
        ),
        confidence="medium",
    )


def test_schema_accepts_valid_justification(
    sample_justification: Justification,
) -> None:
    assert (
        sample_justification.intent == "Preserve distance accuracy for hydrologic flow calculations"
    )
    assert sample_justification.confidence == "medium"
    assert len(sample_justification.alternatives) == 2


def test_schema_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        Justification(
            intent="Test intent",
            alternatives=[],
            choice=Choice(method="x", rationale="y", tradeoffs="z"),
            confidence="invalid",  # type: ignore
        )


def test_schema_round_trip_json(sample_justification: Justification, tmp_path: Path) -> None:
    path = tmp_path / "justification.json"
    path.write_text(sample_justification.model_dump_json(indent=2), encoding="utf-8")

    loaded = Justification.model_validate_json(path.read_text(encoding="utf-8"))
    assert loaded == sample_justification
