from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def chi_squared(
    observed: dict[str, float],
    expected: dict[str, float],
    alphabet: Alphabet,
) -> float:
    score = 0.0
    for i in range(alphabet.size()):
        ch = alphabet.index_to_char(i)
        if ch is None:
            continue
        obs = observed.get(ch, 0.0)
        exp = expected.get(ch, 0.0)
        if exp > 0.0:
            diff = obs - exp
            score += (diff * diff) / exp
    return score


def chi_squared_bigram(
    observed: dict[tuple[str, str], float],
    expected: dict[tuple[str, str], float],
) -> float:
    score = 0.0
    for pair, exp in expected.items():
        if exp > 0.0:
            obs = observed.get(pair, 0.0)
            diff = obs - exp
            score += (diff * diff) / exp
    return score
