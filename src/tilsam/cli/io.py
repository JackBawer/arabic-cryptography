from __future__ import annotations

import sys
from pathlib import Path


def read_input(text: str | None, file: str | None) -> str:
    # Read input from: direct text, file, or stdin.
    # Priority: text > file > stdin
    if text is not None:
        return text
    if file is not None:
        return Path(file).read_text(encoding="utf-8")
    return sys.stdin.read()


def write_output(content: str, file: str | None) -> None:
    # Write output to file or stdout.
    # Always end stdout with newline for CLI friendliness.
    if file is not None:
        Path(file).write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
