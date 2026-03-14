from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def count(text: str, alphabet: Alphabet) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}

    alpha_chars: list[str] = []
    for ch in text:
        idx = alphabet.char_to_index(ch)
        if idx is None:
            continue
        canonical = alphabet.index_to_char(idx)
        if canonical is None:
            continue
        alpha_chars.append(canonical)

    for i in range(len(alpha_chars) - 1):
        pair = (alpha_chars[i], alpha_chars[i + 1])
        counts[pair] = counts.get(pair, 0) + 1

    return counts


def relative(text: str, alphabet: Alphabet) -> dict[tuple[str, str], float]:
    counts_ = count(text, alphabet)
    total = sum(counts_.values())
    if total == 0:
        return {}
    return {pair: n / total for pair, n in counts_.items()}


def sorted(text: str, alphabet: Alphabet) -> list[tuple[tuple[str, str], float]]:
    freq = relative(text, alphabet)
    pairs = list(freq.items())
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs

