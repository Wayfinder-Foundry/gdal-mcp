from __future__ import annotations

import pytest

PROMPTS = [
    "List all rasters available in the workspace so I know what I can reproject.",
    "Show the format details for tiny_raster.tif.",
    "Which CRS should I use for a European dataset?",
    "I need to downsample categorical land cover; which resampling method should I pick?",
    "What compression options are available for GeoTIFF imagery versus DEMs?",
    "Define NDVI in geospatial analysis.",
]


@pytest.mark.parametrize("prompt", PROMPTS)
def test_prompt_suite_runs(prompt: str) -> None:
    """Placeholder test verifying prompt enumeration; hook for live harness."""
    assert prompt  # placeholder assertion; integration harness will execute prompts
