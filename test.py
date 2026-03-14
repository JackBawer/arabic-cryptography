from __future__ import annotations

from tilsam.alphabets import get_alphabet
from tilsam.analysis import bigram, scoring, tables
from tilsam.ciphers import substitution as sub_cipher
from tilsam.crack import substitution as sub_crack


def reversed_key(alpha) -> str:
    return "".join(alpha.index_to_char(i) for i in range(alpha.size() - 1, -1, -1))


def bigram_score(text: str, lang: str) -> float:
    alpha = get_alphabet(lang)
    obs = bigram.relative(text, alpha)
    if lang == "fr":
        exp = tables.french_bigram_freq()
    else:
        raise ValueError(lang)
    return scoring.chi_squared_bigram(obs, exp)


def main() -> None:
    alpha = get_alphabet("fr")
    key = reversed_key(alpha)

    plain = (
        "bonjour a tous ceci est une phrase assez longue pour tester le cassage "
        "par analyse de frequences et de bigrammes dans un texte francais "
        "afin d obtenir des resultats plus stables"
    )

    ciphertext = sub_cipher.encrypt(plain, key, alpha)

    baseline = bigram_score(ciphertext, "fr")
    cand = sub_crack.crack(
        ciphertext,
        alpha,
        tables.french_letter_freq(),
        tables.french_bigram_freq(),
        iterations=500,
    )[0]
    best = bigram_score(cand.plaintext, "fr")

    print("\n[fr] substitution crack")
    print("cipher   :", ciphertext[:90] + ("..." if len(ciphertext) > 90 else ""))
    print("best     :", cand.plaintext[:90] + ("..." if len(cand.plaintext) > 90 else ""))
    print("score (baseline):", baseline)
    print("score (best)    :", best)
    print("key:", cand.key_description[:60] + "...")

    assert best < baseline, "did not improve over baseline"
    print("\nOK")


if __name__ == "__main__":
    main()
