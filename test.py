from __future__ import annotations

from tilsam.alphabets import get_alphabet
from tilsam.analysis import bigram, scoring, tables
from tilsam.crack import substitution as sub_crack


CIPHERTEXT_EN = (
    "gsv jfrxp yildm ulc qfnkh levi gsv ozab wlt zmw gsrh rh z olmtvi hvmgvmxv gl trev "
    "uivjfvmxb zmzobhrh vmlfts wzgz gl dlip drgs kilkviob rm gsrh vckvirnvmg"
)


def _bigram_score(text: str, lang: str) -> float:
    alpha = get_alphabet(lang)
    obs = bigram.relative(text, alpha)

    if lang == "en":
        exp = tables.english_bigram_freq()
    elif lang == "ar":
        exp = tables.arabic_bigram_freq()
    else:
        raise ValueError(f"No bigram table for lang={lang!r}")

    return scoring.chi_squared_bigram(obs, exp)


def test_substitution_en(iterations: int = 300) -> None:
    alpha = get_alphabet("en")

    baseline_score = _bigram_score(CIPHERTEXT_EN, "en")

    cand = sub_crack.crack(
        CIPHERTEXT_EN,
        alpha,
        tables.english_letter_freq(),
        tables.english_bigram_freq(),
        iterations=iterations,
    )[0]

    best_score = _bigram_score(cand.plaintext, "en")

    print(f"\n[en] iterations={iterations}")
    print("cipher   :", CIPHERTEXT_EN[:90] + ("..." if len(CIPHERTEXT_EN) > 90 else ""))
    print("best     :", cand.plaintext[:90] + ("..." if len(cand.plaintext) > 90 else ""))
    print("score (baseline):", baseline_score)
    print("score (best)    :", best_score)
    print("key:", cand.key_description[:60] + "...")

    # "Working" for this heuristic means improvement vs baseline, not perfect recovery.
    assert best_score < baseline_score, "substitution cracker did not improve over baseline"


def main() -> None:
    test_substitution_en(iterations=300)
    print("\nOK")


if __name__ == "__main__":
    main()
