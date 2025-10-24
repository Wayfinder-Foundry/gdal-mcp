from __future__ import annotations

import json
from pathlib import Path

from src.middleware.reflection_store import DiskStore
from src.prompts.justification import Alternative, Choice, Justification


def make_sample_justification() -> Justification:
    return Justification(
        intent="Preserve distance accuracy for hydrologic flow calculations",
        alternatives=[
            Alternative(
                method="EPSG:3310",
                why_not="Albers distorts distance in small basins",
            )
        ],
        choice=Choice(
            method="EPSG:32610",
            rationale="UTM Zone 10N minimizes distance distortion",
            tradeoffs="Zone boundary artifacts if watershed crosses zones",
        ),
        confidence="medium",
    )


def test_disk_store_round_trip(tmp_path: Path) -> None:
    store = DiskStore(root=str(tmp_path / "justifications"))
    justification = make_sample_justification()
    domain = "crs_datum"

    path = store.put("hash123", justification, domain)

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["intent"] == "Preserve distance accuracy for hydrologic flow calculations"
    assert data["confidence"] == "medium"
    assert "_meta" in data

    loaded = store.get(str(path))
    assert loaded is not None
    assert loaded["intent"] == "Preserve distance accuracy for hydrologic flow calculations"


def test_disk_store_missing(tmp_path: Path) -> None:
    store = DiskStore(root=str(tmp_path / "justifications"))
    missing = store.get(str(tmp_path / "justifications" / "missing.json"))
    assert missing is None
