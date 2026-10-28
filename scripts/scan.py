"""Fetch raw OSM + DEM tiles for one region (real network data only, no fixture fallback).

Usage: PYTHONPATH=engine python scripts/scan.py regions/<id>.yaml out/
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

from pipeline.config import load_region
from pipeline.fetch.dem import fetch_dem
from pipeline.fetch.overpass import fetch_osm, save_raw


def main(region_yaml: str, out_root: str) -> int:
    region = load_region(region_yaml)
    out = Path(out_root) / region.id
    osm = fetch_osm(region.bbox)
    if not osm.get("elements"):
        raise SystemExit(f"{region.id}: Overpass returned no elements")
    save_raw(osm, out)
    fetch_dem(region.bbox, region.dem_zoom, cache_dir=out / "dem")
    files = sorted(p for p in out.rglob("*") if p.is_file())
    manifest = {
        "region": region.id,
        "bbox_swen": list(region.bbox),
        "dem_zoom": region.dem_zoom,
        "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "attribution": region.attribution,
        "files": {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in files},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{region.id}: {len(files)} files, {len(osm['elements'])} OSM elements")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
