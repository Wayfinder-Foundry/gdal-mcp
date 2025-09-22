from __future__ import annotations

import asyncio
import logging
import shutil
from typing import Dict, List, Optional, Tuple


log = logging.getLogger(__name__)


def _map_unified_to_legacy(unified_args: List[str]) -> List[str]:
    """Best-effort mapping from GDAL 3.11 unified CLI to legacy utilities.

    Supports the subset we expose today:
      - gdal info -> gdalinfo
      - gdal convert -> gdal_translate
      - gdal raster reproject -> gdalwarp
    """
    if not unified_args or unified_args[0] != "gdal":
        return unified_args

    def _next_value(flag: str, items: List[str], i: int) -> Tuple[Optional[str], int]:
        if i + 1 < len(items):
            return items[i + 1], i + 1
        log.warning("Missing value for flag %s in args: %s", flag, items)
        return None, i

    # gdal info <path> [--format json|text]
    if len(unified_args) >= 2 and unified_args[1] == "info":
        out: List[str] = ["gdalinfo"]
        i = 2
        fmt = None
        while i < len(unified_args):
            tok = unified_args[i]
            if tok == "--format":
                fmt, i = _next_value(tok, unified_args, i)
            else:
                out.append(tok)
            i += 1
        # Map format to legacy switch
        if fmt and fmt.lower() == "json":
            out.insert(1, "-json")
        return out

    # gdal convert <in> <out> [--output-format DRV] [--overwrite] [--creation-option k=v]* [...]
    if len(unified_args) >= 2 and unified_args[1] == "convert":
        out: List[str] = ["gdal_translate"]
        # Expect input and output as positional args at indices 2 and 3
        if len(unified_args) >= 4:
            out += [unified_args[2], unified_args[3]]
        i = 4
        while i < len(unified_args):
            tok = unified_args[i]
            if tok == "--output-format":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-of", val]
            elif tok == "--overwrite":
                out.append("-overwrite")
            elif tok == "--creation-option":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-co", val]
            else:
                out.append(tok)
            i += 1
        return out

    # gdal raster reproject <in> <out> --dst-crs DST [options]
    if len(unified_args) >= 3 and unified_args[1] == "raster" and unified_args[2] == "reproject":
        out: List[str] = ["gdalwarp"]
        # Positional inputs
        if len(unified_args) >= 5:
            out += [unified_args[3], unified_args[4]]
        i = 5
        while i < len(unified_args):
            tok = unified_args[i]
            if tok == "--dst-crs":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-t_srs", val]
            elif tok == "--src-crs":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-s_srs", val]
            elif tok == "--resampling":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-r", val]
            elif tok == "--resolution":
                val, i = _next_value(tok, unified_args, i)
                if val and "," in val:
                    x, y = val.split(",", 1)
                    out += ["-tr", x, y]
            elif tok == "--size":
                val, i = _next_value(tok, unified_args, i)
                if val and "," in val:
                    w, h = val.split(",", 1)
                    out += ["-ts", w, h]
            elif tok == "--bbox":
                val, i = _next_value(tok, unified_args, i)
                if val and val.count(",") == 3:
                    xmin, ymin, xmax, ymax = val.split(",", 3)
                    out += ["-te", xmin, ymin, xmax, ymax]
            elif tok == "--bbox-crs":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-te_srs", val]
            elif tok == "--overwrite":
                out.append("-overwrite")
            elif tok == "--creation-option":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-co", val]
            elif tok == "--warp-option":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-wo", val]
            elif tok == "--transform-option":
                val, i = _next_value(tok, unified_args, i)
                if val:
                    out += ["-to", val]
            else:
                out.append(tok)
            i += 1
        return out

    # Unknown subcommand, return as-is
    return unified_args


async def run_gdal(args: List[str], *, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """Run a GDAL command asynchronously, with fallback mapping if unified CLI is missing.

    Returns (returncode, stdout, stderr).
    """
    final_args = args
    if args and args[0] == "gdal" and shutil.which("gdal") is None:
        # Attempt legacy mapping
        final_args = _map_unified_to_legacy(args)
        log.info("Unified 'gdal' not found; using legacy mapping: %s", " ".join(final_args))

    exe = final_args[0] if final_args else "gdal"
    if shutil.which(exe) is None:
        raise FileNotFoundError(
            f"Required GDAL executable '{exe}' not found on PATH. Install GDAL or run the Docker image."
        )

    log.debug("Running GDAL: %s", " ".join(final_args))
    proc = await asyncio.create_subprocess_exec(
        *final_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    out_b, err_b = await proc.communicate()
    out = out_b.decode("utf-8", errors="replace") if out_b is not None else ""
    err = err_b.decode("utf-8", errors="replace") if err_b is not None else ""
    log.debug("GDAL exited %s", proc.returncode)
    return proc.returncode or 0, out, err
