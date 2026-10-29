"""Assign one Apify token per shard, or mark the shard as skipped.

Reads `APIFY_TOKENS` (comma-separated) and `SHARD_INDEX`, then appends either
`APIFY_TOKENS=<token>` or `SHARD_SKIP=1` to `$GITHUB_ENV`.

Keeping this out of inline YAML removes the nested-quoting that made the old
workflow's Python block impossible to read and easy to break.
"""
from __future__ import annotations

import os
import sys


def clean(raw: str) -> list[str]:
    out: list[str] = []
    for part in raw.replace("\ufeff", "").split(","):
        tok = part.replace("\u200b", "").replace("\u00a0", "").strip().strip("'\"").strip()
        if tok and tok not in out:
            out.append(tok)
    return out


def main() -> int:
    tokens = clean(os.environ.get("APIFY_TOKENS") or "")
    index = int(os.environ.get("SHARD_INDEX") or "0")
    env_file = os.environ.get("GITHUB_ENV")

    if not env_file:
        print("GITHUB_ENV is not set; nothing to write.")
        return 1

    if index >= len(tokens):
        with open(env_file, "a", encoding="utf-8") as fh:
            fh.write("SHARD_SKIP=1\n")
        print(f"shard {index}: no token available ({len(tokens)} tokens), skipping")
        return 0

    with open(env_file, "a", encoding="utf-8") as fh:
        fh.write(f"APIFY_TOKENS={tokens[index]}\n")
    print(f"shard {index}: token assigned ({len(tokens)} tokens total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
