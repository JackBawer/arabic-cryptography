from __future__ import annotations

import subprocess

from tilsam.alphabets import get_alphabet
from tilsam.analysis import bigram, scoring, tables
from tilsam.ciphers import affine as cipher_affine
from tilsam.ciphers import caesar as cipher_caesar
from tilsam.ciphers import substitution as cipher_substitution
from tilsam.crack import affine as crack_affine
from tilsam.crack import caesar as crack_caesar
from tilsam.crack import substitution as crack_substitution


def reversed_key(alpha) -> str:
    return "".join(alpha.index_to_char(i) for i in range(alpha.size() - 1, -1, -1))


def _norm_ws(s: str) -> str:
    return " ".join(s.split())


def _print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _assert_raises(fn, exc_type):
    try:
        fn()
    except exc_type:
        return
    except Exception as e:
        raise AssertionError(f"Expected {exc_type.__name__}, got {type(e).__name__}: {e}") from e
    raise AssertionError(f"Expected {exc_type.__name__} to be raised")


def _expected_letter_freq(lang: str) -> dict[str, float]:
    return {
        "en": tables.english_letter_freq,
        "fr": tables.french_letter_freq,
        "ar": tables.arabic_letter_freq,
    }[lang]()


def _expected_bigram_freq(lang: str) -> dict[tuple[str, str], float]:
    return {
        "en": tables.english_bigram_freq,
        "fr": tables.french_bigram_freq,
        "ar": tables.arabic_bigram_freq,
    }[lang]()


# -------------------------
# Round-trip tests
# -------------------------

def test_caesar_roundtrip(lang: str, plain: str, shift: int) -> None:
    alpha = get_alphabet(lang)
    ct = cipher_caesar.encrypt(plain, shift, alpha)
    pt = cipher_caesar.decrypt(ct, shift, alpha)
    assert _norm_ws(pt) == _norm_ws(plain), f"[{lang}] Caesar roundtrip failed"


def test_affine_roundtrip(lang: str, plain: str, a: int, b: int) -> None:
    alpha = get_alphabet(lang)
    ct = cipher_affine.encrypt(plain, a, b, alpha)
    pt = cipher_affine.decrypt(ct, a, b, alpha)
    assert _norm_ws(pt) == _norm_ws(plain), f"[{lang}] Affine roundtrip failed"


def test_substitution_roundtrip(lang: str, plain: str) -> None:
    alpha = get_alphabet(lang)
    key = reversed_key(alpha)
    ct = cipher_substitution.encrypt(plain, key, alpha)
    pt = cipher_substitution.decrypt(ct, key, alpha)
    assert _norm_ws(pt) == _norm_ws(plain), f"[{lang}] Substitution roundtrip failed"


# -------------------------
# Crack tests
# -------------------------

def test_crack_caesar_short_in_top(lang: str, plain: str, shift: int, top_n: int = 5) -> None:
    """
    For short text, chi-squared ranking can be ambiguous; require the correct plaintext
    to appear in the top N candidates.
    """
    alpha = get_alphabet(lang)
    ct = cipher_caesar.encrypt(plain, shift, alpha)
    candidates = crack_caesar.crack(ct, alpha, _expected_letter_freq(lang))

    got = [_norm_ws(c.plaintext) for c in candidates[:top_n]]
    target = _norm_ws(plain)

    if target not in got:
        print(f"\n[{lang}] Caesar crack short-text debug (top {top_n}):")
        for i, c in enumerate(candidates[:top_n]):
            print(f"  #{i+1} score={c.score:.4f} key={c.key_description:>10} text={c.plaintext!r}")
        raise AssertionError(f"[{lang}] Caesar crack failed: plaintext not found in top {top_n}")


def test_crack_caesar_long_best_is_exact(lang: str, plain: str, shift: int) -> None:
    alpha = get_alphabet(lang)
    ct = cipher_caesar.encrypt(plain, shift, alpha)
    candidates = crack_caesar.crack(ct, alpha, _expected_letter_freq(lang))

    best = _norm_ws(candidates[0].plaintext)
    target = _norm_ws(plain)

    if best != target:
        print(f"\n[{lang}] Caesar crack long-text debug (top 5):")
        for i, c in enumerate(candidates[:5]):
            print(f"  #{i+1} score={c.score:.4f} key={c.key_description:>10} text={c.plaintext[:80]!r}")
        raise AssertionError(f"[{lang}] Caesar crack failed on long text (best candidate not exact)")


def test_crack_affine_long(lang: str, plain: str, a: int, b: int) -> None:
    alpha = get_alphabet(lang)
    ct = cipher_affine.encrypt(plain, a, b, alpha)

    candidates = crack_affine.crack(ct, alpha, _expected_letter_freq(lang))
    assert candidates, "no candidates returned"

    best = _norm_ws(candidates[0].plaintext)
    target = _norm_ws(plain)

    if best != target:
        print(f"\n[{lang}] Affine crack debug (top 5):")
        for i, c in enumerate(candidates[:5]):
            print(f"  #{i+1} score={c.score:.4f} key={c.key_description:>18} text={c.plaintext[:80]!r}")
        raise AssertionError(f"[{lang}] Affine crack failed on long text")


def test_crack_substitution_improves(lang: str, plain: str, iterations: int) -> None:
    """
    Substitution cracking is stochastic: assert improvement in bigram chi-squared
    (lower is better), compared to ciphertext baseline.
    """
    alpha = get_alphabet(lang)
    key = reversed_key(alpha)
    ct = cipher_substitution.encrypt(plain, key, alpha)

    exp_letters = _expected_letter_freq(lang)
    exp_bigrams = _expected_bigram_freq(lang)

    baseline = scoring.chi_squared_bigram(bigram.relative(ct, alpha), exp_bigrams)

    cand = crack_substitution.crack(ct, alpha, exp_letters, exp_bigrams, iterations=iterations)[0]
    best = scoring.chi_squared_bigram(bigram.relative(cand.plaintext, alpha), exp_bigrams)

    if not (best < baseline):
        print(f"\n[{lang}] Substitution crack debug:")
        print(f"  baseline={baseline:.4f} best={best:.4f}")
        print(f"  cand text={cand.plaintext[:120]!r}")
        print(f"  cand key ={cand.key_description[:120]!r}")
        raise AssertionError(f"[{lang}] substitution crack did not improve baseline")


# -------------------------
# Validation / error tests
# -------------------------

def test_invalid_affine_key(lang: str) -> None:
    alpha = get_alphabet(lang)

    # a=2 should be invalid for common alph sizes (26, 28, ...)
    def _do():
        cipher_affine.encrypt("test", 2, 1, alpha)

    _assert_raises(_do, ValueError)


def test_invalid_substitution_key_length(lang: str) -> None:
    alpha = get_alphabet(lang)
    bad_key = "a" * (alpha.size() - 1)

    def _do():
        cipher_substitution.encrypt("test", bad_key, alpha)

    _assert_raises(_do, ValueError)


def test_invalid_substitution_key_duplicate(lang: str) -> None:
    alpha = get_alphabet(lang)
    chars = alpha.chars()
    if len(chars) < 2:
        return

    bad_key = "".join([chars[0]] * len(chars))

    def _do():
        cipher_substitution.encrypt("test", bad_key, alpha)

    _assert_raises(_do, ValueError)


# -------------------------
# CLI smoke tests
# -------------------------

def test_cli_smoke() -> None:
    """
    Requires: pip install -e .
    This checks the entrypoint + one encrypt/decrypt flow.
    """
    p = subprocess.run(
        ["tilsam", "encrypt", "caesar", "--lang", "en", "--shift", "3", "hello world"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert p.returncode == 0, f"CLI encrypt failed: {p.stderr}"
    ct = p.stdout.strip()

    p = subprocess.run(
        ["tilsam", "decrypt", "caesar", "--lang", "en", "--shift", "3", ct],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert p.returncode == 0, f"CLI decrypt failed: {p.stderr}"
    assert _norm_ws(p.stdout.strip()) == "hello world"


def main() -> None:
    _print_section("tilsam comprehensive tests")

    _print_section("1) Round-trip encrypt/decrypt")
    test_caesar_roundtrip("en", "hello world", shift=3)
    test_caesar_roundtrip("fr", "la rencontre est prevue a la cafeteria", shift=5)
    test_caesar_roundtrip("ar", "مرحبا بالعالم", shift=5)

    test_affine_roundtrip("en", "attack at dawn", a=5, b=8)
    test_affine_roundtrip("fr", "bonjour a tous", a=5, b=8)
    test_affine_roundtrip("ar", "هذا نص عربي للاختبار", a=3, b=5)

    test_substitution_roundtrip("en", "the quick brown fox jumps over the lazy dog")
    test_substitution_roundtrip("fr", "bonjour a tous ceci est un test")
    test_substitution_roundtrip("ar", "هذا نص عربي للاختبار")
    print("OK")

    _print_section("2) Crack (frequency analysis)")
    # short texts: must be in top N
    test_crack_caesar_short_in_top("en", "hello world", shift=3, top_n=5)
    test_crack_caesar_short_in_top("fr", "il faut travailler pour reussir", shift=10, top_n=5)
    test_crack_caesar_short_in_top("ar", "هذا نص عربي للاختبار", shift=7, top_n=5)

    # long texts: should be best candidate exactly
    long_en = ("the quick brown fox jumps over the lazy dog " * 6).strip()
    test_crack_caesar_long_best_is_exact("en", long_en, shift=11)

    # Affine crack needs longer text for stability
    long_fr = (
        "bonjour a tous ceci est une phrase assez longue pour tester l analyse de frequences "
        "et verifier le cassage du chiffrement affine " * 2
    ).strip()
    long_ar = (
        "هذا نص عربي طويل نسبيا لاختبار كسر الشفرة باستخدام تحليل الترددات "
        "ويجب ان يكون النص طويلا للحصول على نتائج افضل " * 2
    ).strip()

    test_crack_affine_long("en", long_en, a=5, b=8)
    test_crack_affine_long("fr", long_fr, a=5, b=8)
    test_crack_affine_long("ar", long_ar, a=3, b=5)

    # Substitution crack: stable improvement test (French tables exist and are used in your old test)
    test_crack_substitution_improves("fr", long_fr, iterations=8000)
    print("OK")

    _print_section("3) Validation / error handling")
    test_invalid_affine_key("en")
    test_invalid_affine_key("ar")
    test_invalid_substitution_key_length("en")
    test_invalid_substitution_key_length("ar")
    test_invalid_substitution_key_duplicate("en")
    test_invalid_substitution_key_duplicate("ar")
    print("OK")

    _print_section("4) CLI smoke")
    try:
        test_cli_smoke()
        print("OK")
    except FileNotFoundError:
        print("SKIP: tilsam CLI not found on PATH (run `pip install -e .`)")

    _print_section("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
