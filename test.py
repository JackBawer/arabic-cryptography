from tilsam.alphabets import get_alphabet
from tilsam.ciphers import substitution


def reversed_key(alpha) -> str:
    return "".join(alpha.index_to_char(i) for i in range(alpha.size() - 1, -1, -1))


def roundtrip(lang: str, text: str) -> None:
    alpha = get_alphabet(lang)
    key = reversed_key(alpha)

    c = substitution.encrypt(text, key, alpha)
    p = substitution.decrypt(c, key, alpha)

    print(f"[{lang}]")
    print("plain :", text)
    print("cipher:", c)
    print("dec  :", p)
    assert p == text
    print("OK\n")


def main() -> None:
    roundtrip("en", "hello world! 42")
    roundtrip("fr", "bonjour a tous! ca va? 2026")
    roundtrip("ar", "هذا نص عربي للاختبار 123!")


if __name__ == "__main__":
    main()
