"""Street View grid scan: metadata-only by default, optional heading images.

Usage: PYTHONPATH=engine python scripts/scan_streetview.py regions/<id>.yaml out/
Env: GOOGLE_SV_KEY required; SV_STEP_M=50, SV_FETCH_IMAGES=0|1, SV_SLEEP=0.05.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from pipeline.config import load_region
from pipeline.fetch.streetview import api_key_from_env, scan_region


def main(region_yaml: str, out_root: str) -> int:
    region = load_region(region_yaml)
    out = Path(out_root) / f"{region.id}-streetview"
    panos = scan_region(
        region.bbox, out, api_key_from_env(),
        step_m=float(os.environ.get("SV_STEP_M", "50")),
        crs_utm=region.crs_utm,
        fetch_images=os.environ.get("SV_FETCH_IMAGES") == "1",
        sleep_s=float(os.environ.get("SV_SLEEP", "0.05")),
    )
    if not panos:
        raise SystemExit(f"{region.id}: no panoramas (check API key / quota / region)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
