from __future__ import annotations

from tilsam.alphabets.base import Alphabet
from tilsam.analysis import bigram, frequency, scoring
from tilsam.crack.candidate import Candidate


def crack(
    ciphertext: str,
    alphabet: Alphabet,
    expected_letter_freq: dict[str, float],
    expected_bigram_freq: dict[tuple[str, str], float],
    iterations: int = 100,
) -> list[Candidate]:
    # Strategy:
    # 1) Initial key guess from single-letter frequency ranking
    # 2) Hill-climbing improvement using bigram chi-squared and pairwise swaps
    # Returns exactly one Candidate (best key found)
    n = alphabet.size()

    alpha_chars: list[str] = []
    for i in range(n):
        ch = alphabet.index_to_char(i)
        if ch is None:
            raise RuntimeError(f"alphabet.index_to_char({i}) returned None")
        alpha_chars.append(ch)

    # Step 1: initial guess from letter frequencies
    cipher_sorted = frequency.sorted(ciphertext, alphabet)  # [(char, freq)] desc
    expected_sorted = sorted(expected_letter_freq.items(), key=lambda x: x[1], reverse=True)

    # key[i] = guessed plaintext char for ciphertext char with alphabet index i
    key: list[str] = [alpha_chars[0]] * n

    for i, ch in enumerate(alpha_chars):
        rank = _position_in_sorted(cipher_sorted, ch)
        if rank is not None and rank < len(expected_sorted):
            key[i] = expected_sorted[rank][0]

    _fill_missing(key, alpha_chars)

    # Step 2: hill-climbing using bigram chi-squared
    best_score = _score_key(ciphertext, key, alphabet, expected_bigram_freq)

    for _ in range(iterations):
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                key[i], key[j] = key[j], key[i]
                new_score = _score_key(ciphertext, key, alphabet, expected_bigram_freq)
                if new_score < best_score:
                    best_score = new_score
                    improved = True
                else:
                    # swap back
                    key[i], key[j] = key[j], key[i]

        if not improved:
            break

    plaintext = _apply_key(ciphertext, key, alphabet)
    key_str = "".join(key)

    return [
        Candidate(
            plaintext=plaintext,
            score=best_score,
            key_description=f"key={key_str}",
        )
    ]


def _position_in_sorted(sorted_pairs: list[tuple[str, float]], ch: str) -> int | None:
    for idx, (c, _) in enumerate(sorted_pairs):
        if c == ch:
            return idx
    return None


def _apply_key(ciphertext: str, key: list[str], alphabet: Alphabet) -> str:
    # Apply a substitution key to decrypt:
    # ciphertext char at alphabet index i -> key[i]
    out: list[str] = []
    for ch in ciphertext:
        idx = alphabet.char_to_index(ch)
        if idx is None:
            out.append(ch)
        else:
            out.append(key[idx])
    return "".join(out)


def _score_key(
    ciphertext: str,
    key: list[str],
    alphabet: Alphabet,
    expected_bigram_freq: dict[tuple[str, str], float],
) -> float:
    plaintext = _apply_key(ciphertext, key, alphabet)
    observed = bigram.relative(plaintext, alphabet)
    return scoring.chi_squared_bigram(observed, expected_bigram_freq)


def _fill_missing(key: list[str], alpha_chars: list[str]) -> None:
    # Fill any duplicate/missing entries so key is a valid permutation.
    used = [False] * len(alpha_chars)
    needs_fill: list[int] = []

    for i, k in enumerate(key):
        try:
            pos = alpha_chars.index(k)
        except ValueError:
            needs_fill.append(i)
            continue

        if used[pos]:
            needs_fill.append(i)
        else:
            used[pos] = True

    unused = [c for idx, c in enumerate(alpha_chars) if not used[idx]]

    for i in needs_fill:
        if unused:
            key[i] = unused.pop()
