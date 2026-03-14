from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def encrypt(plaintext: str, shift: int, alphabet: Alphabet) -> str:
    n = alphabet.size()
    out: list[str] = []

    for ch in plaintext:
        idx = alphabet.char_to_index(ch)
        if idx is None:
            out.append(ch)  # keep spaces/punctuation/digits
            continue

        new_idx = (idx + shift) % n
        out.append(alphabet.index_to_char(new_idx) or ch)

    return "".join(out)


def decrypt(ciphertext: str, shift: int, alphabet: Alphabet) -> str:
    return encrypt(ciphertext, -shift, alphabet)
