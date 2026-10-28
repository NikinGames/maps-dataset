"""Google Photorealistic 3D Tiles region fetch.

Usage: PYTHONPATH=engine python scripts/scan_tiles3d.py regions/<id>.yaml out/
Env: GOOGLE_MAPS_API_KEY required; T3D_ERROR=20, T3D_MAX_TILES=500.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from pipeline.config import load_region
from pipeline.fetch.tiles3d import api_key_from_env, fetch_tileset


def main(region_yaml: str, out_root: str) -> int:
    region = load_region(region_yaml)
    out = Path(out_root) / f"{region.id}-tiles3d"
    m = fetch_tileset(
        region.bbox, out, api_key_from_env(),
        target_error=float(os.environ.get("T3D_ERROR", "20")),
        max_tiles=int(os.environ.get("T3D_MAX_TILES", "500")),
    )
    if m["tile_count"] == 0:
        raise SystemExit(f"{region.id}: no tiles kept (bbox outside coverage?)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
