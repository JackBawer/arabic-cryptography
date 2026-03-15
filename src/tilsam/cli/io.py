from __future__ import annotations

import sys
from pathlib import Path


def read_input(
    text: str | None,
    file: str | None,
    *,
    encoding: str = "utf-8",
) -> str:
    """
    Read input from: direct text, file, or stdin.
    Priority: text > file > stdin

    - text: returned as-is
    - file: read with the provided encoding (default utf-8)
    - stdin: read from sys.stdin as provided by the terminal piping
    """
    if text is not None:
        return text
    if file is not None:
        return Path(file).read_text(encoding=encoding)
    return sys.stdin.read()


def write_output(
    content: str,
    file: str | None,
    *,
    encoding: str = "utf-8",
) -> None:
    """
    Write output to file or stdout.

    - file: write with the provided encoding (default utf-8)
    - stdout: print and ensure it ends with a newline for CLI friendliness
    """
    if file is not None:
        Path(file).write_text(content, encoding=encoding)
        return

    sys.stdout.write(content)
    if not content.endswith("\n"):
        sys.stdout.write("\n")
