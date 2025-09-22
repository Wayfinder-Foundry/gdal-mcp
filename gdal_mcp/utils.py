from __future__ import annotations

import asyncio
import logging
import shutil
from typing import Dict, List, Optional, Tuple


log = logging.getLogger(__name__)


def ensure_gdal_available() -> None:
    """Ensure the GDAL 3.11+ unified `gdal` CLI is available on PATH."""
    if shutil.which("gdal") is None:
        raise FileNotFoundError(
            "The 'gdal' CLI was not found on PATH. Ensure GDAL 3.11+ is installed and 'gdal' is available."
        )


async def run_gdal(args: List[str], *, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """Run a gdal command asynchronously.

    Returns (returncode, stdout, stderr).
    """
    ensure_gdal_available()
    log.debug("Running GDAL: %s", " ".join(args))
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    out_b, err_b = await proc.communicate()
    out = out_b.decode("utf-8", errors="replace") if out_b is not None else ""
    err = err_b.decode("utf-8", errors="replace") if err_b is not None else ""
    log.debug("GDAL exited %s", proc.returncode)
    return proc.returncode or 0, out, err
