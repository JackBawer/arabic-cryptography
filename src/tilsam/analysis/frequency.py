from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def count(text: str, alphabet: Alphabet) -> dict[str, int]:
    counts: dict[str, int] = {}

    for ch in text:
        idx = alphabet.char_to_index(ch)
        if idx is None:
            continue
        canonical = alphabet.index_to_char(idx) or ch
        counts[canonical] = counts.get(canonical, 0) + 1

    return counts


def relative(text: str, alphabet: Alphabet) -> dict[str, float]:
    counts_ = count(text, alphabet)
    total = sum(counts_.values())
    if total == 0:
        return {}
    return {c: n / total for c, n in counts_.items()}


def sorted(text: str, alphabet: Alphabet) -> list[tuple[str, float]]:
    freq = relative(text, alphabet)
    pairs = list(freq.items())
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs
