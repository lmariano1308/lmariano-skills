#!/usr/bin/env python3
"""Measured visual QA for the demonstration preview, using the standard library only.

The script reads the page and its stylesheet, extracts the declared custom
properties, computes WCAG contrast for the declared pairs and checks the layout
invariants that break silently at 390 px. It does not render the page, so its
result is labelled ``static``; a browser pass is the stronger claim.

Usage:
    python3 qa/check_preview.py [preview/index.html] [--json out.json]
Exit code is 0 only when every blocking check passes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PAIRS = (
    ("contrast.ink-on-surface", "--ink", "--surface", 4.5),
    ("contrast.ink2-on-surface", "--ink-2", "--surface", 4.5),
    ("contrast.ink-on-bg", "--ink", "--bg", 4.5),
    ("contrast.ink2-on-bg", "--ink-2", "--bg", 4.5),
)
LITERAL_PAIRS = (("contrast.button-label", "#ffffff", "--accent", 4.5),)
MIN_CONTROL_HEIGHT = 44


def _channel(value: float) -> float:
    value /= 255.0
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    raw = color.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(char * 2 for char in raw)
    red, green, blue = (int(raw[index : index + 2], 16) for index in (0, 2, 4))
    return 0.2126 * _channel(red) + 0.7152 * _channel(green) + 0.0722 * _channel(blue)


def contrast(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


def parse_tokens(html: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;}]+);", html):
        tokens.setdefault(name, value.strip())
    return tokens


def resolve(token: str, tokens: dict[str, str]) -> str | None:
    if token.startswith("--"):
        return tokens.get(token)
    return token


def run(path: Path) -> dict[str, object]:
    html = path.read_text(encoding="utf-8")
    tokens = parse_tokens(html)
    checks: list[dict[str, object]] = []

    def record(identifier: str, measured: object, expected: str, passed: bool, blocking: bool = True) -> None:
        checks.append(
            {
                "id": identifier,
                "measured": measured,
                "expected": expected,
                "passed": passed,
                "blocking": blocking,
            }
        )

    for identifier, foreground, background, threshold in PAIRS + LITERAL_PAIRS:
        first = resolve(foreground, tokens)
        second = resolve(background, tokens)
        if first is None or second is None:
            record(identifier, "token missing", f">= {threshold}", False)
            continue
        value = contrast(first, second)
        record(identifier, value, f">= {threshold}", value >= threshold)

    record("document.doctype", html.lstrip().lower().startswith("<!doctype html>"), "html5 doctype", html.lstrip().lower().startswith("<!doctype html>"))
    record("document.lang", "lang=" in html, "present", "lang=" in html)
    record("document.viewport", "width=device-width" in html, "present", "width=device-width" in html)
    title = re.search(r"<title>([^<]*)</title>", html)
    record("document.title", (title.group(1).strip() if title else ""), "non-empty", bool(title and title.group(1).strip()))

    hidden = re.search(r"(opacity\s*:\s*0(?![.\d])|visibility\s*:\s*hidden)", html)
    record("content.visible-by-default", hidden.group(0) if hidden else "none", "none", hidden is None)

    control = tokens.get("--control-h", "")
    height = int(re.sub(r"[^0-9]", "", control) or 0)
    record("layout.control-height", f"{height}px", f">= {MIN_CONTROL_HEIGHT}px", height >= MIN_CONTROL_HEIGHT)

    record("layout.max-width", "max-width" in html, "present", "max-width" in html)
    record(
        "layout.mobile-breakpoint",
        "@media (max-width" in html,
        "present",
        "@media (max-width" in html,
        blocking=False,
    )

    blocking_failures = sum(1 for check in checks if check["blocking"] and not check["passed"])
    return {
        "target": str(path),
        "mode": "static",
        "viewports": [390, 1440],
        "checks": checks,
        "blocking_failures": blocking_failures,
    }


def main(argv: list[str]) -> int:
    arguments = [item for item in argv[1:] if not item.startswith("--")]
    json_out: Path | None = None
    if "--json" in argv:
        index = argv.index("--json")
        if index + 1 < len(argv):
            json_out = Path(argv[index + 1])
            arguments = [item for item in arguments if item != argv[index + 1]]

    default = Path(__file__).resolve().parents[1] / "preview" / "index.html"
    target = Path(arguments[0]) if arguments else default
    if not target.is_file():
        print(f"preview not found: {target}", file=sys.stderr)
        return 2

    result = run(target)
    checks = result["checks"]
    assert isinstance(checks, list)
    print(f"Visual QA (static mode) — {target}")
    print(f"{'check':<32}{'measured':>12}  {'expected':<20}result")
    for check in checks:
        measured = f"{check['measured']}"[:18]
        state = "PASS" if check["passed"] else ("FAIL" if check["blocking"] else "WARN")
        print(f"{check['id']:<32}{measured:>12}  {check['expected']:<20}{state}")
    print(f"blocking_failures: {result['blocking_failures']}")

    if json_out is not None:
        json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["blocking_failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
