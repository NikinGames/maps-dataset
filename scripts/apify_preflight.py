"""Report which Apify tokens in APIFY_TOKENS are usable, without running an actor.

Used as a workflow preflight so a broken secret fails once, with a readable message,
instead of seven parallel shards each discovering it separately.

Exit code 0 when at least one token works, 1 otherwise. Never prints a full token.

Usage:
    python scripts/apify_preflight.py            # human-readable report
    python scripts/apify_preflight.py --gha      # also writes `usable=N` to $GITHUB_OUTPUT
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

API = "https://api.apify.com/v2/users/me"


def clean(raw: str) -> list[str]:
    """Split and sanitise a token list.

    A UTF-8 BOM at the start of the secret is the classic failure: the value looks
    fine in the UI, every request returns 401, and GitHub's masking does not match
    the token because the stored value has an invisible prefix.
    """
    out: list[str] = []
    for part in raw.replace("\ufeff", "").split(","):
        tok = part.replace("\u200b", "").replace("\u00a0", "").strip().strip("'\"").strip()
        if tok and tok not in out:
            out.append(tok)
    return out


def mask(token: str) -> str:
    return f"{token[:11]}…{token[-4:]}" if len(token) > 18 else "***"


def probe(token: str) -> tuple[bool, str]:
    req = urllib.request.Request(f"{API}?token={token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8", "replace")
        import json

        data = (json.loads(payload).get("data") or {})
        return True, str(data.get("username", "?"))
    except urllib.error.HTTPError as err:
        return False, f"HTTP {err.code}"
    except Exception as err:  # noqa: BLE001
        return False, type(err).__name__


def main() -> int:
    raw = os.environ.get("APIFY_TOKENS") or os.environ.get("APIFY_TOKEN") or ""
    tokens = clean(raw)

    if "\ufeff" in raw:
        print("[preflight] WARNING: APIFY_TOKENS starts with a UTF-8 BOM; stripped.")
    if not tokens:
        print("[preflight] APIFY_TOKENS is empty.")
        return 1

    alive = 0
    for i, tok in enumerate(tokens):
        ok, detail = probe(tok)
        if ok:
            alive += 1
            print(f"[preflight] token {i} ({mask(tok)}) OK as {detail}")
        else:
            print(f"[preflight] token {i} ({mask(tok)}) -> {detail}")

    print(f"[preflight] {alive}/{len(tokens)} tokens usable")

    if "--gha" in sys.argv:
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a", encoding="utf-8") as fh:
                fh.write(f"usable={alive}\n")

    if alive == 0:
        print(
            "[preflight] No usable token. Renew the APIFY_TOKENS secret "
            "(Apify Console -> Settings -> Integrations) and check the monthly "
            "usage hard limit on each account."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
