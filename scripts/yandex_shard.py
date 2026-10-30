"""Run one Yandex places shard against a region.

Invoked from the workflow as:
    python scripts/yandex_shard.py <region-id> <shard-index> <shard-count> <max-per-query>

Runs with `engine/` as the current directory so `pipeline` is importable.
An empty shard is a normal outcome (that slice of the category list had no
results), so it exits 0 and lets the merge step decide whether anything was
collected. An auth/quota failure is NOT normal and fails the job red —
otherwise every shard goes green on dead tokens and the merge publishes an
empty archive that looks like a successful scan.
"""
from __future__ import annotations

import sys
from pathlib import Path

# The workflow invokes this from the repo root; Python only puts the script's
# own directory on sys.path, so `pipeline` (inside engine/) is not importable
# without this. Add the engine dir explicitly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print("usage: yandex_shard.py <region> <index> <count> <max-per-query>")
        return 2

    region_id, index, count, max_per = argv[1], int(argv[2]), int(argv[3]), int(argv[4])

    from pipeline.fetch.status import EmptyResult
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
    except EmptyResult as err:
        # Legitimately empty slice of the category list — merge decides.
        print(f"shard {index}: empty ({err})")
        return 0
    # Anything else (token exhaustion, auth, network) propagates: red build.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
