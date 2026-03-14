from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tilsam.alphabets.base import Alphabet

LETTERS: str = "abcdefghijklmnopqrstuvwxyz"


@dataclass(frozen=True)
class English(Alphabet):
    def name(self) -> str:
        return "English"

    def size(self) -> int:
        return 26

    def char_to_index(self, c: str) -> Optional[int]:
        if not c:
            return None

        ch = c[0].lower()
        if "a" <= ch <= "z":
            return ord(ch) - ord("a")
        return None

    def index_to_char(self, i: int) -> Optional[str]:
        if 0 <= i < 26:
            return LETTERS[i]
        return None


ENGLISH = English()
