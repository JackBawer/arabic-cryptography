from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from tilsam.alphabets.base import Alphabet

LETTERS: str = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"

# All codepoints that should normalize to ا
_ALIF_VARIANTS = frozenset((
    0x0622,  # آ  ALEF WITH MADDA ABOVE
    0x0623,  # أ  ALEF WITH HAMZA ABOVE
    0x0624,  # ؤ  -- actually WAW WITH HAMZA, skip (maps to و below)
    0x0625,  # إ  ALEF WITH HAMZA BELOW
    0x0671,  # ٱ  ALEF WASLA  ← the missing one
    0x0672,  # ٲ  ALEF WITH WAVY HAMZA ABOVE
    0x0673,  # ٳ  ALEF WITH WAVY HAMZA BELOW
    0x0675,  # ٵ  HIGH HAMZA ALEF
))

# WAW WITH HAMZA ABOVE → و
_WAW_HAMZA = 0x0624  # ؤ

# YEH WITH HAMZA ABOVE → ي
_YEH_HAMZA = 0x0626  # ئ


def _normalize_char(c: str) -> Optional[str]:
    if not c:
        return None
    ch = c[0]
    cp = ord(ch)

    # Skip diacritics / tashkeel / tatweel
    if (0x064B <= cp <= 0x065F) or cp == 0x0670 or cp == 0x0640:
        return None

    # Alif variants → ا
    if cp in _ALIF_VARIANTS:
        return "\u0627"

    # ؤ (waw with hamza) → و
    if cp == _WAW_HAMZA:
        return "\u0648"

    # ئ (yeh with hamza) → ي
    if cp == _YEH_HAMZA:
        return "\u064A"

    # ة (taa marbuta) → ت
    if cp == 0x0629:
        return "\u062A"

    # ى (alef maqsura) → ي
    if cp == 0x0649:
        return "\u064A"

    # Everything else in the core Arabic letter block
    if 0x0627 <= cp <= 0x064A:
        base = ch
        return base if base in LETTERS else None

    return None


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
        idx = LETTERS.find(base)
        return idx if idx != -1 else None

    def index_to_char(self, i: int) -> Optional[str]:
        if 0 <= i < 28:
            return LETTERS[i]
        return None


ARABIC = Arabic()
