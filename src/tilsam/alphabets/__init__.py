from __future__ import annotations

from tilsam.alphabets.base import Alphabet
from tilsam.alphabets.english import ENGLISH
from tilsam.alphabets.french import FRENCH
from tilsam.alphabets.arabic import ARABIC

_REGISTRY: dict[str, Alphabet] = {
    "en": ENGLISH,
    "fr": FRENCH,
    "ar": ARABIC,
}


def get_alphabet(lang: str) -> Alphabet:
    # Return an Alphabet instance from a short language code: 'en', 'fr', 'ar'
    key = (lang or "").strip().lower()
    if key in _REGISTRY:
        return _REGISTRY[key]
    raise ValueError(f"Unsupported language: {lang!r}. Choose one of: {', '.join(sorted(_REGISTRY))}")
