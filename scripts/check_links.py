#!/usr/bin/env python3
"""Check relative Markdown links in tracked project documentation."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"(?<!!)\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


def markdown_files():
    yield ROOT / "README.md"
    yield ROOT / "CONTRIBUTING.md"
    for directory in ("docs", "research", "templates"):
        yield from sorted((ROOT / directory).rglob("*.md"))


def main():
    missing = []
    checked = 0
    for document in markdown_files():
        text = document.read_text(encoding="utf-8")
        in_fence = False
        for number, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK.finditer(line):
                target = match.group(1) or match.group(2)
                if target.startswith(("https:", "http:", "mailto:", "#")):
                    continue
                path = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not path:
                    continue
                checked += 1
                if not (document.parent / path).exists():
                    missing.append(f"{document.relative_to(ROOT)}:{number}: {target}")
    if missing:
        print("Missing relative links:\n" + "\n".join(missing), file=sys.stderr)
        return 1
    print(f"Checked {checked} relative Markdown links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
