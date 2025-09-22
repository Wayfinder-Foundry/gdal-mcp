from __future__ import annotations

import json
import logging
from typing import Dict

from gdal_mcp.app import mcp
from gdal_mcp.utils import run_gdal

log = logging.getLogger(__name__)


@mcp.tool(name="info")
async def info(path: str, fmt: str = "json") -> Dict:
    """
    Get information on a dataset via GDAL 3.11 unified CLI ("gdal info").

    path: Input dataset path or URI
    format: 'json' or 'text' (default: 'json')
    """
    args = ["gdal", "info", path]
    fmt = (fmt or "json").lower()
    if fmt in ("json", "text"):
        args += ["--format", fmt]
    code, out, err = await run_gdal(args)
    if code != 0:
        raise RuntimeError(f"gdal info failed: {err.strip() or out.strip()}")
    if fmt == "json":
        try:
            return json.loads(out)
        except Exception as e:
            log.warning(f"gdal info returned non-JSON output; returning raw text: {e}")
            return {"raw": out}
    else:
        return {"text": out}
