import re


_DIACRITICS_RE = re.compile(r"[\u064B-\u0652]")  # ً ٌ ٍ َ ُ ِ ّ ْ


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text for frequency analysis so it matches `arabic_letters`
    in common.py (28 letters).

    - Removes tashkeel/diacritics (harakat, shadda, sukun, tanween).
    - Normalizes alif variants to ا.
    - Normalizes ى to ي.
    - Normalizes ة to ه.
    - Normalizes ؤ to و, and ئ to ي (simple folding).
    - Removes tatweel (ـ).
    """
    # Remove diacritics
    text = _DIACRITICS_RE.sub("", text)

    # Remove tatweel
    text = text.replace("ـ", "")

    # Normalize letter variants
    text = re.sub(r"[أإآٱ]", "ا", text)
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")
    text = text.replace("ؤ", "و")
    text = text.replace("ئ", "ي")

    return text
