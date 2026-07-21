#!/usr/bin/env python3
"""Fail when a public HTML page is missing the site's Counter.dev client."""

from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path

COUNTER_SRC = "/assets/counter.js"
COUNTER_ID = "1a87eb0e-c422-4942-bce1-c55f9dca58f4"
COUNTER_UTC_OFFSET = "-7"
COUNTER_SERVER = "https://counter.dev"
EXCLUDED_PARTS = {".git", ".github", ".githooks", ".preview", "node_modules"}


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.scripts: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.scripts.append(dict(attrs))


EXPECTED_ATTRIBUTES = {
    "src": COUNTER_SRC,
    "data-id": COUNTER_ID,
    "data-utcoffset": COUNTER_UTC_OFFSET,
    "data-server": COUNTER_SERVER,
}


def public_html_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.html")
        if not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    )


def validate_page(path: Path) -> list[str]:
    parser = ScriptCollector()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        return [f"could not read page: {exc}"]

    counters = [script for script in parser.scripts if script.get("src") == COUNTER_SRC]
    if not counters:
        return [f"missing {COUNTER_SRC} script"]
    if len(counters) > 1:
        return [f"contains {len(counters)} Counter scripts; expected exactly one"]

    script = counters[0]
    mismatches = [
        f'{name}={script.get(name)!r} (expected {expected!r})'
        for name, expected in EXPECTED_ATTRIBUTES.items()
        if script.get(name) != expected
    ]
    if "defer" not in script:
        mismatches.append("missing defer attribute")
    return mismatches


def main() -> int:
    default_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root, help="site root to check")
    args = parser.parse_args()
    root = args.root.resolve()

    client = root / COUNTER_SRC.removeprefix("/")
    failures: list[tuple[str, list[str]]] = []
    if not client.is_file():
        failures.append((str(client.relative_to(root)), ["tracking client does not exist"]))

    pages = public_html_files(root)
    if not pages:
        failures.append((".", ["no public HTML pages found"]))

    for page in pages:
        errors = validate_page(page)
        if errors:
            failures.append((str(page.relative_to(root)), errors))

    if failures:
        print("Counter coverage check failed:", file=sys.stderr)
        for page, errors in failures:
            print(f"  {page}", file=sys.stderr)
            for error in errors:
                print(f"    - {error}", file=sys.stderr)
        print("\nEvery public HTML page must contain:", file=sys.stderr)
        print(
            f'<script defer src="{COUNTER_SRC}" data-id="{COUNTER_ID}" '
            f'data-utcoffset="{COUNTER_UTC_OFFSET}" data-server="{COUNTER_SERVER}"></script>',
            file=sys.stderr,
        )
        return 1

    print(f"Counter coverage OK: {len(pages)} public HTML pages checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
