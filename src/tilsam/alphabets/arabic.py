from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tilsam.alphabets.base import Alphabet

LETTERS: str = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"


def _normalize_char(c: str) -> Optional[str]:
    # Normalize Arabic char to its base isolated form

    # - Ignores diacritics (tashkeel)
    # - Normalizes alif variants
    # - Normalizes taa marbuta
    # - Keeps only chars that exist in LETTERS

    if not c:
        return None

    ch = c[0]
    cp = ord(ch)

    # Skip diacritics (tashkeel) entirely
    if (0x064B <= cp <= 0x065F) or cp == 0x0670:
        return None

    # Normalize variants
    if cp in (0x0622, 0x0623, 0x0625):  # آ أ إ
        base = "\u0627"  # ا
    elif cp == 0x0629:  # ة
        base = "\u062A"  # ت
    elif cp == 0x0649:  # ى
        base = "\u064A"  # ي
    elif 0x0627 <= cp <= 0x064A:
        base = ch
    else:
        return None

    return base if base in LETTERS else None


@dataclass(frozen=True)
class Arabic(Alphabet):
    def name(self) -> str:
        return "arabic"

    def size(self) -> int:
        return 28

    def char_to_index(self, c: str) -> Optional[int]:
        base = _normalize_char(c)
        if base is None:
            return None
        return LETTERS.find(base)  # 0..27

    def index_to_char(self, i: int) -> Optional[str]:
        if 0 <= i < 28:
            return LETTERS[i]
        return None


# Singleton instance (convenient for registry)
ARABIC = Arabic()
