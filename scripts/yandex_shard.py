"""Run one Yandex places shard against a region.

Invoked from the workflow as:
    python scripts/yandex_shard.py <region-id> <shard-index> <shard-count> <max-per-query>

Runs with `engine/` as the current directory so `pipeline` is importable.
An empty shard is a normal outcome (that slice of the category list had no results),
so it exits 0 and lets the merge step decide whether anything was collected.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print("usage: yandex_shard.py <region> <index> <count> <max-per-query>")
        return 2

    region_id, index, count, max_per = argv[1], int(argv[2]), int(argv[3]), int(argv[4])

    from pipeline.config import load_region
    from pipeline.fetch.yandex_places import DEFAULT_QUERIES, scan_region

    region = load_region(f"../regions/{region_id}.yaml")
    queries = DEFAULT_QUERIES[index::count] if count > 1 else DEFAULT_QUERIES
    if not queries:
        print(f"shard {index}: no queries assigned")
        return 0

    print(f"shard {index}: {queries}")
    try:
        scan_region(
            region.bbox,
            Path("data/raw/yandex") / region.id / f"shard_{index}",
            queries=queries,
            max_places_per_query=max_per,
        )
    except SystemExit as err:
        print(f"shard {index}: {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
