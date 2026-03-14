from __future__ import annotations

from tilsam.alphabets.base import Alphabet
from tilsam.analysis import frequency, scoring
from tilsam.ciphers import affine
from tilsam.crack.candidate import Candidate


def _gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)


def crack(ciphertext: str, alphabet: Alphabet, expected_freq: dict[str, float]) -> list[Candidate]:
    n = alphabet.size()
    candidates: list[Candidate] = []

    for a in range(1, n):
        if _gcd(a, n) != 1:
            continue
        for b in range(n):
            try:
                plaintext = affine.decrypt(ciphertext, a, b, alphabet)
            except ValueError:
                # invalid a (no inverse) or other key validation problems
                continue

            observed = frequency.relative(plaintext, alphabet)
            score = scoring.chi_squared(observed, expected_freq, alphabet)
            candidates.append(
                Candidate(
                    plaintext=plaintext,
                    score=score,
                    key_description=f"a={a}, b={b}",
                )
            )

    candidates.sort(key=lambda c: c.score)
    return candidates
