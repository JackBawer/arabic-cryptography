from __future__ import annotations

from typing import Protocol, Callable

from tilsam.alphabets.base import Alphabet

from . import caesar, affine, substitution


class CipherModule(Protocol):
    def encrypt(self, plaintext: str, *args, alphabet: Alphabet, **kwargs) -> str: ...
    def decrypt(self, ciphertext: str, *args, alphabet: Alphabet, **kwargs) -> str: ...


_REGISTRY: dict[str, object] = {
    "caesar": caesar,
    "affine": affine,
    "substitution": substitution,
}


def get_cipher(name: str):
    # Return a cipher module by short name: 'caesar', 'affine', 'substitution'.
    key = (name or "").strip().lower()
    if key in _REGISTRY:
        return _REGISTRY[key]
    raise ValueError(
        f"Unsupported cipher: {name!r}. Choose one of: {', '.join(sorted(_REGISTRY))}"
    )


__all__ = ["caesar", "affine", "substitution", "get_cipher"]
