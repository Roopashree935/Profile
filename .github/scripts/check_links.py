#!/usr/bin/env python3
"""Static checks for the portfolio site.

Runs in CI (see .github/workflows/ci.yml) and locally with:
    python3 .github/scripts/check_links.py

It fails the build on:
  * a local href/src that points at a file which does not exist
  * a page with no <title>, no meta description, or not exactly one <h1>
  * an image without an alt attribute

It deliberately does not check external URLs — network calls in CI are flaky
and would fail the build for someone else's outage, not ours.
"""

from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "#")
# A leading "/" is a site-root reference (e.g. the 404 page's absolute asset
# path). It cannot be resolved from the filesystem without knowing the deploy
# base, so it is skipped rather than reported as broken.
SKIP_PREFIXES = ("//", "/")
ATTR_RE = re.compile(r'(?:href|src|srcset)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

failures: list[str] = []


class PageCheck(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.has_title = False
        self.has_description = False
        self._in_title = False
        self.img_missing_alt: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self.has_title = True
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and d.get("name", "").lower() == "description":
            if d.get("content", "").strip():
                self.has_description = True
        elif tag == "img":
            if "alt" not in d:
                self.img_missing_alt.append(d.get("src", "(no src)"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False


def html_files() -> list[str]:
    return sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))


def check_links(name: str, text: str) -> None:
    for raw in ATTR_RE.findall(text):
        raw = raw.strip()
        # Skip the whole value first. A data URI contains commas and quotes, so
        # splitting it before this check would invent bogus "references".
        if not raw or raw.startswith(SKIP_SCHEMES) or raw.startswith(SKIP_PREFIXES):
            continue
        for candidate in raw.split(","):
            ref = candidate.strip().split(" ")[0]
            if not ref:
                continue
            path = ref.split("#")[0].split("?")[0]
            if not path:
                continue
            resolved = os.path.normpath(os.path.join(ROOT, os.path.dirname(name), path))
            if not os.path.exists(resolved):
                failures.append(f"{name}: missing local reference -> {ref}")


def check_page(name: str, text: str) -> None:
    parser = PageCheck()
    parser.feed(text)
    if not parser.has_title:
        failures.append(f"{name}: no <title>")
    if not parser.has_description:
        failures.append(f"{name}: no meta description")
    if parser.h1 != 1:
        failures.append(f"{name}: expected exactly one <h1>, found {parser.h1}")
    for src in parser.img_missing_alt:
        failures.append(f"{name}: <img> without alt -> {src}")


def main() -> int:
    pages = html_files()
    if not pages:
        print("No HTML files found — nothing to check.")
        return 1

    for name in pages:
        with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
            text = fh.read()
        check_links(name, text)
        check_page(name, text)

    print(f"Checked {len(pages)} page(s): {', '.join(pages)}")
    if failures:
        print(f"\n{len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
