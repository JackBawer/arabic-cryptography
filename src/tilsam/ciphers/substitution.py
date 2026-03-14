from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def _validate_key(key: str, alphabet: Alphabet) -> None:
    n = alphabet.size()
    if len(key) != n:
        raise ValueError(f"Invalid substitution key length: got {len(key)}, expected {n}")

    seen: set[str] = set()
    for ch in key:
        if alphabet.char_to_index(ch) is None:
            raise ValueError(f"Invalid substitution key character: {ch!r} not in alphabet")
        if ch in seen:
            raise ValueError(f"Duplicate substitution key character: {ch!r}")
        seen.add(ch)


def encrypt(plaintext: str, key: str, alphabet: Alphabet) -> str:
    _validate_key(key, alphabet)

    out: list[str] = []
    for ch in plaintext:
        idx = alphabet.char_to_index(ch)
        out.append(ch if idx is None else key[idx])
    return "".join(out)


def decrypt(ciphertext: str, key: str, alphabet: Alphabet) -> str:
    _validate_key(key, alphabet)

    rev: dict[str, str] = {}
    for i in range(alphabet.size()):
        alpha_ch = alphabet.index_to_char(i)
        if alpha_ch is None:
            raise RuntimeError(f"alphabet.index_to_char({i}) returned None")
        rev[key[i]] = alpha_ch

    out: list[str] = []
    for ch in ciphertext:
        out.append(rev.get(ch, ch))
    return "".join(out)
