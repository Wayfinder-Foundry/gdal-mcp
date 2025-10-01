from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import typer

from .utils import run_gdal

app = typer.Typer(add_completion=False)


@app.command()
def main(
    input: Path = typer.Option(..., exists=True, help="Input raster for smoke benchmark"),
    dst_crs: str = typer.Option("EPSG:4326", help="Destination CRS for reprojection"),
    out: Path = typer.Option(Path("bench/out.tif"), help="Output path"),
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    code, _out, err = asyncio.run(run_gdal([
        "gdal", "raster", "reproject", str(input), str(out), "--dst-crs", dst_crs, "--overwrite"
    ]))
    dt = time.perf_counter() - t0

    result = {
        "ok": code == 0,
        "seconds": round(dt, 3),
        "stderr": err.strip(),
        "output": str(out),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    app()
