"""Fetch Mapillary street-level image metadata + 1024px thumbnails for a region.

Usage: MAPILLARY_TOKEN=... python scripts/scan_imagery.py regions/<id>.yaml out/ [max_images]
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
import yaml

API = "https://graph.mapillary.com/images"
FIELDS = "id,captured_at,compass_angle,computed_geometry,thumb_1024_url,sequence"
CELL = 0.05  # deg; API caps bbox area at 0.01 deg^2


def cells(s, w, n, e):
    y = s
    while y < n:
        x = w
        while x < e:
            yield (x, y, min(x + CELL, e), min(y + CELL, n))
            x += CELL
        y += CELL


def main(region_yaml: str, out_root: str, max_images: int = 3000) -> int:
    cfg = yaml.safe_load(open(region_yaml, encoding="utf-8"))
    s, w, n, e = cfg["bbox"]
    token = os.environ["MAPILLARY_TOKEN"]
    out = Path(out_root) / cfg["id"] / "street"
    (out / "thumbs").mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    meta: dict[str, dict] = {}
    for bbox in cells(s, w, n, e):
        r = sess.get(API, params={"access_token": token, "fields": FIELDS, "limit": 2000,
                                  "bbox": ",".join(f"{v:.6f}" for v in bbox)}, timeout=60)
        r.raise_for_status()
        for im in r.json().get("data", []):
            meta[im["id"]] = im
        time.sleep(0.5)
    picked = sorted(meta.values(), key=lambda m: m.get("captured_at", 0), reverse=True)
    picked = picked[:max_images]
    for im in picked:
        url = im.get("thumb_1024_url")
        if not url:
            continue
        p = out / "thumbs" / f"{im['id']}.jpg"
        if not p.exists():
            p.write_bytes(sess.get(url, timeout=60).content)
    (out / "images.json").write_text(json.dumps(picked), encoding="utf-8")
    print(f"{cfg['id']}: {len(meta)} images found, {len(picked)} kept")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3000))
