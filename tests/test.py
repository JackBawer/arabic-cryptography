from __future__ import annotations

import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "tests" / "data"
TMP = DATA / "tmp"


@dataclass(frozen=True)
class Case:
    lang: str
    label: str
    plain_file: Path
    needle: str


# Needles are lowercase because crack output often normalizes case
CASES = [
    Case("en", "English", DATA / "en_plain.txt", "this is a small english text sample"),
    Case("fr", "French", DATA / "fr_plain.txt", "c'est un petit texte"),
    Case("ar", "Arabic", DATA / "ar_plain.txt", "الله لا اله"),
]


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    p = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{p.stdout}")
    return p.stdout


def fold_accents(s: str) -> str:
    # é -> e, ç -> c, etc.
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def normalize_arabic(s: str) -> str:
    """
    Normalize common Arabic variants that many cipher alphabets normalize anyway.

    This makes tests match app behavior, not linguistic exactness.
    """
    # normalize different alef forms -> alef
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    # taa marbuta -> taa (matches your observed behavior: سنة -> سنت)
    s = s.replace("ة", "ت")
    # alef maqsura -> yaa
    s = s.replace("ى", "ي")
    # hamza on waw/yaa -> hamza (optional, conservative)
    s = s.replace("ؤ", "ء").replace("ئ", "ء")
    # tatweel
    s = s.replace("ـ", "")
    return s


def canonical(s: str, *, lang: str) -> str:
    """
    Canonicalize text for roundtrip comparisons:
    - lowercase
    - language-specific normalization (French accents, Arabic variants)
    - keep only alphanumeric characters (works for Latin + Arabic letters)
    """
    s = s.replace("\r\n", "\n").lower()

    if lang == "fr":
        s = fold_accents(s)

    if lang == "ar":
        s = normalize_arabic(s)

    return "".join(ch for ch in s if ch.isalnum())


def assert_contains(haystack: str, needle: str, msg: str) -> None:
    if needle.lower() not in haystack.lower():
        raise AssertionError(f"{msg}\nExpected to find: {needle!r}\n--- Output ---\n{haystack}\n")


def ensure_files_exist() -> None:
    missing = [c.plain_file for c in CASES if not c.plain_file.exists()]
    if missing:
        raise FileNotFoundError(f"Missing test files: {missing}")


def gen_sub_key(lang: str) -> str:
    # Use your installed library to generate a valid substitution key (reverse alphabet)
    code = r"""
from tilsam.alphabets import get_alphabet
import sys
lang=sys.argv[1]
alpha=get_alphabet(lang)
chars=None
if hasattr(alpha, "chars"):
    c=alpha.chars
    chars=list(c()) if callable(c) else list(c)
elif hasattr(alpha, "characters"):
    chars=list(alpha.characters)
if not chars:
    raise RuntimeError("cannot extract alphabet chars")
s="".join(chars)
print(s[::-1])
"""
    out = subprocess.run(
        ["python", "-", lang],
        input=code,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"Failed to gen substitution key for {lang}:\n{out.stdout}")
    return out.stdout.strip()


def assert_roundtrip(case: Case, roundtrip_text: str) -> None:
    original = case.plain_file.read_text(encoding="utf-8")
    a = canonical(original, lang=case.lang)
    b = canonical(roundtrip_text, lang=case.lang)
    if a != b:
        raise AssertionError(
            f"Roundtrip mismatch for {case.lang}\n"
            f"canonical(original)[:140]={a[:140]!r}\n"
            f"canonical(roundtrip)[:140]={b[:140]!r}\n"
        )


def test_caesar(case: Case) -> None:
    c = TMP / f"{case.lang}_caesar.txt"
    r = TMP / f"{case.lang}_caesar_roundtrip.txt"
    k = TMP / f"{case.lang}_caesar_crack.txt"
    a = TMP / f"{case.lang}_analyze.txt"

    run(["tilsam", "encrypt", "caesar", "--shift", "3", "--lang", case.lang, "--input", str(case.plain_file), "--output", str(c)])
    run(["tilsam", "decrypt", "caesar", "--shift", "3", "--lang", case.lang, "--input", str(c), "--output", str(r)])
    run(["tilsam", "crack", "caesar", "--lang", case.lang, "--input", str(c), "--output", str(k), "--top", "3"])
    run(["tilsam", "analyze", "--lang", case.lang, "--input", str(case.plain_file), "--output", str(a), "--bigrams"])

    assert_roundtrip(case, r.read_text(encoding="utf-8"))

    crack_out = k.read_text(encoding="utf-8")
    assert_contains(crack_out, case.needle, f"Caesar crack did not contain expected plaintext ({case.lang})")

    analyze_out = a.read_text(encoding="utf-8")
    assert_contains(analyze_out, "Letter Frequencies:", f"Analyze output missing letter frequencies ({case.lang})")
    assert_contains(analyze_out, "Bigram Frequencies", f"Analyze output missing bigrams ({case.lang})")


def test_affine(case: Case) -> None:
    c = TMP / f"{case.lang}_affine.txt"
    r = TMP / f"{case.lang}_affine_roundtrip.txt"
    k = TMP / f"{case.lang}_affine_crack.txt"

    run(["tilsam", "encrypt", "affine", "--key-a", "5", "--key-b", "8", "--lang", case.lang, "--input", str(case.plain_file), "--output", str(c)])
    run(["tilsam", "decrypt", "affine", "--key-a", "5", "--key-b", "8", "--lang", case.lang, "--input", str(c), "--output", str(r)])
    run(["tilsam", "crack", "affine", "--lang", case.lang, "--input", str(c), "--output", str(k), "--top", "3"])

    assert_roundtrip(case, r.read_text(encoding="utf-8"))

    crack_out = k.read_text(encoding="utf-8")
    assert_contains(crack_out, case.needle, f"Affine crack did not contain expected plaintext ({case.lang})")


def test_substitution(case: Case) -> None:
    c = TMP / f"{case.lang}_sub.txt"
    r = TMP / f"{case.lang}_sub_roundtrip.txt"
    k = TMP / f"{case.lang}_sub_crack.txt"

    key = gen_sub_key(case.lang)

    run(["tilsam", "encrypt", "substitution", "--key", key, "--lang", case.lang, "--input", str(case.plain_file), "--output", str(c)])
    run(["tilsam", "decrypt", "substitution", "--key", key, "--lang", case.lang, "--input", str(c), "--output", str(r)])
    run(["tilsam", "crack", "substitution", "--lang", case.lang, "--input", str(c), "--output", str(k), "--iterations", "500", "--top", "1"])

    assert_roundtrip(case, r.read_text(encoding="utf-8"))
    # Substitution cracking is heuristic; we don't assert it matches plaintext.


def test_stdin_path() -> None:
    out = run(["tilsam", "encrypt", "caesar", "--shift", "3", "--lang", "en"], input_text="abc")
    if not out.strip():
        raise AssertionError("stdin test produced empty output")


def main() -> None:
    ensure_files_exist()
    TMP.mkdir(parents=True, exist_ok=True)

    for case in CASES:
        test_caesar(case)
        test_affine(case)
        test_substitution(case)
        print(f"PASS: {case.label} ({case.lang})")

    test_stdin_path()
    print("PASS: stdin path")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
