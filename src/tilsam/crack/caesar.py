from __future__ import annotations

from tilsam.alphabets.base import Alphabet
from tilsam.analysis import frequency, scoring
from tilsam.ciphers import caesar
from tilsam.crack.candidate import Candidate


def crack(ciphertext: str, alphabet: Alphabet, expected_freq: dict[str, float]) -> list[Candidate]:
    n = alphabet.size()
    candidates: list[Candidate] = []

    for shift in range(n):
        plaintext = caesar.decrypt(ciphertext, shift, alphabet)
        observed = frequency.relative(plaintext, alphabet)
        score = scoring.chi_squared(observed, expected_freq, alphabet)
        candidates.append(
            Candidate(
                plaintext=plaintext,
                score=score,
                key_description=f"shift={shift}",
            )
        )

    candidates.sort(key=lambda c: c.score)
    return candidates
