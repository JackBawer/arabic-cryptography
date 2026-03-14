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
    # Strategy
    # 1) Initial key guess from single-letter frequency ranking
    # 2) Hill-climbing improvement using bigram chi-squared and pairwise swaps
    # Returns exactly one Candidate (best key found)
    n = alphabet.size()
    alpha_chars = [alphabet.index_to_char(i) for i in range(n)]
    alpha_chars = [c for c in alpha_chars if c is not None]

    # Step 1: initial guess from letter frequencies
    cipher_sorted = frequency.sorted(ciphertext, alphabet) # [(char, freq)] desc
    expected_sorted = sorted(expected_letter_freq.items(), key=lambda x: x[1], reverse=True)

    # key[i] = guessed plaintext char for ciphertext char with alphabet index
    key: list[str] = [alpha_chars[0]] * n

    for i, ch in enumerate(alpha_chars):
        # Find this ciphertext letter's rank amongst ciphertext frequencies
        rank = _position_in_sorted(cipher_sorted, ch)
        if rank is not None and rank < len(expected_sorted):
            key[i] = expected_sorted[rank][0]

    __fill_missing(key, alpha_chars)

    # Step 2: hill-climbing using bigram chi-squared
    best_score = _score_key(ciphertext, key, alphabet, expected_bigram_freq)

    for _ in range(iterations):
        improved = False
        for i in range(n):
            for j in range(1 + n, n):
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
            key_descritiption=f"key={key_str}",
        )
    ]


