from __future__ import annotations

from tilsam.alphabets.base import Alphabet


def _gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    # Extended Euclidean algorithm.
    # Returns (g, x, y) such that: a*x + b*y = g = gcd(a, b)
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = _egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def _modinv(a: int, n: int) -> int:
    # Modular inverse of a modulo n
    # Raises ValueError if inverse does not exist
    a = a % n
    g, x, _ = _egcd(a, n)
    if g != 1:
        raise ValueError(f"No modular inverse: a={a} is not coprime with n={n}")
    return x % n


def encrypt(plaintext: str, a: int, b: int, alphabet: Alphabet) -> str:
    n = alphabet.size()
    if _gcd(a, n) != 1:
        raise ValueError(f"Invalid key: gcd(a={a}, n={n}) != 1")

    b = b % n

    out: list[str] = []
    for ch in plaintext:
        x = alphabet.char_to_index(ch)
        if x is None:
            out.append(ch)
            continue

        y = (a * x + b) % n
        out.append(alphabet.index_to_char(y) or ch)

    return "".join(out)


def decrypt(ciphertext: str, a: int, b: int, alphabet: Alphabet) -> str:
    n = alphabet.size()
    if _gcd(a, n) != 1:
        raise ValueError(f"Invalid key: gcd(a={a}, n={n}) != 1")

    b = b % n
    a_inv = _modinv(a, n)

    out: list[str] = []
    for ch in ciphertext:
        y = alphabet.char_to_index(ch)
        if y is None:
            out.append(ch)
            continue

        x = (a_inv * (y - b)) % n
        out.append(alphabet.index_to_char(x) or ch)

    return "".join(out)
