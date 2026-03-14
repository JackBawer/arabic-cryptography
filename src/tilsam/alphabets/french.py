from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tilsam.alphabets.base import Alphabet

LETTERS: str = "abcdefghijklmnopqrstuvwxyz"


def _normalize_char(c: str) -> Optional[str]:
    # Normalize French accented characters to their base letter
    # Returns None for non-letter characters

    if not c:
        return None

    ch = c[0].lower()

    if "a" <= ch <= "z":
        return ch

    if ch in ("à", "â", "ä"):
        return "a"
    if ch == "ç":
        return "c"
    if ch in ("è", "é", "ê", "ë"):
        return "e"
    if ch in ("î", "ï"):
        return "i"
    if ch in ("ô", "ö"):
        return "o"
    if ch in ("ù", "û", "ü"):
        return "u"
    if ch == "ÿ":
        return "y"
    if ch == "œ":
        return "o"  # ligature — map to 'o' for cipher purposes
    if ch == "æ":
        return "a"  # ligature — map to 'a' for cipher purposes

    return None


@dataclass(frozen=True)
class French(Alphabet):
    def name(self) -> str:
        return "french"

    def size(self) -> int:
        return 26

    def char_to_index(self, c: str) -> Optional[int]:
        base = _normalize_char(c)
        if base is None:
            return None
        return ord(base) - ord("a")

    def index_to_char(self, i: int) -> Optional[str]:
        if 0 <= i < 26:
            return LETTERS[i]
        return None


FRENCH = French()
