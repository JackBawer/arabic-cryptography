from __future__ import annotations

from dataclasses import dataclass

import typer

from tilsam.alphabets import get_alphabet
from tilsam.analysis import bigram, frequency, tables
from tilsam.ciphers import affine as cipher_affine
from tilsam.ciphers import caesar as cipher_caesar
from tilsam.ciphers import substitution as cipher_substitution
from tilsam.cli.io import read_input, write_output
from tilsam.crack import affine as crack_affine
from tilsam.crack import caesar as crack_caesar
from tilsam.crack import substitution as crack_substitution

app = typer.Typer(help="Classical cipher toolkit")
encrypt_app = typer.Typer(help="Encrypt text with a classical cipher")
decrypt_app = typer.Typer(help="Decrypt text with a classical cipher")
crack_app = typer.Typer(help="Crack a ciphertext using frequency analysis")

app.add_typer(encrypt_app, name="encrypt")
app.add_typer(decrypt_app, name="decrypt")
app.add_typer(crack_app, name="crack")


@dataclass(frozen=True)
class Lang:
    value: str  # "en" | "ar" | "fr"


def detect_lang(text: str) -> Lang:
    arabic_count = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
    latin_count = sum(1 for c in text if c.isascii() and c.isalpha())

    if arabic_count > latin_count:
        return Lang("ar")

    french_accents = set("àâäçèéêëîïôöùûüÿœæÀÂÄÇÈÉÊËÎÏÔÖÙÛÜŸŒÆ")
    if any(c in french_accents for c in text):
        return Lang("fr")

    return Lang("en")


def resolve_lang(lang: str | None, text: str) -> Lang:
    return Lang(lang) if lang is not None else detect_lang(text)


def get_freq_tables(lang: Lang):
    if lang.value == "en":
        return tables.english_letter_freq(), tables.english_bigram_freq()
    if lang.value == "ar":
        return tables.arabic_letter_freq(), tables.arabic_bigram_freq()
    if lang.value == "fr":
        return tables.french_letter_freq(), tables.french_bigram_freq()
    raise ValueError(f"unsupported language: {lang.value!r}")


def format_candidates(candidates, top: int) -> str:
    out_lines: list[str] = []
    for i, c in enumerate(candidates[:top], start=1):
        out_lines.append(f"#{i} [score: {c.score:.4f}] ({c.key_description})")
        out_lines.append(f"  {c.plaintext}")
        out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n"


# ----------------
# Encrypt commands
# ----------------

@encrypt_app.command("caesar")
def encrypt_caesar(
    shift: int = typer.Option(..., "--shift", "-s", help="Shift value"),
    text: str | None = typer.Argument(None, help="Input text (or use --input for file)"),
    input: str | None = typer.Option(None, "--input", "-i", help="Input file"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file"),
    lang: str | None = typer.Option(None, "--lang", "-l", help="Language", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_caesar.encrypt(content, shift, alpha)
    write_output(result, output)


@encrypt_app.command("affine")
def encrypt_affine(
    key_a: int = typer.Option(..., "--key-a", "-a", help="Key a (must be coprime with alphabet size)"),
    key_b: int = typer.Option(..., "--key-b", "-b", help="Key b"),
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_affine.encrypt(content, key_a, key_b, alpha)
    write_output(result, output)


@encrypt_app.command("substitution")
def encrypt_substitution(
    key: str = typer.Option(..., "--key", "-k", help="Substitution key (permutation of alphabet)"),
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_substitution.encrypt(content, key, alpha)
    write_output(result, output)


# ----------------
# Decrypt commands
# ----------------

@decrypt_app.command("caesar")
def decrypt_caesar(
    shift: int = typer.Option(..., "--shift", "-s"),
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_caesar.decrypt(content, shift, alpha)
    write_output(result, output)


@decrypt_app.command("affine")
def decrypt_affine(
    key_a: int = typer.Option(..., "--key-a", "-a"),
    key_b: int = typer.Option(..., "--key-b", "-b"),
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_affine.decrypt(content, key_a, key_b, alpha)
    write_output(result, output)


@decrypt_app.command("substitution")
def decrypt_substitution(
    key: str = typer.Option(..., "--key", "-k"),
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    result = cipher_substitution.decrypt(content, key, alpha)
    write_output(result, output)


# -------------
# Crack commands
# -------------

@crack_app.command("caesar")
def crack_caesar_cmd(
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
    top: int = typer.Option(5, "--top", "-t", help="Number of top candidates to show"),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    letter_freq, _ = get_freq_tables(l)
    candidates = crack_caesar.crack(content, alpha, letter_freq)
    write_output(format_candidates(candidates, top), output)


@crack_app.command("affine")
def crack_affine_cmd(
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
    top: int = typer.Option(5, "--top", "-t"),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    letter_freq, _ = get_freq_tables(l)
    candidates = crack_affine.crack(content, alpha, letter_freq)
    write_output(format_candidates(candidates, top), output)


@crack_app.command("substitution")
def crack_substitution_cmd(
    text: str | None = typer.Argument(None),
    input: str | None = typer.Option(None, "--input", "-i"),
    output: str | None = typer.Option(None, "--output", "-o"),
    lang: str | None = typer.Option(None, "--lang", "-l", case_sensitive=False),
    iterations: int = typer.Option(100, "--iterations", help="Hill-climbing iterations"),
    top: int = typer.Option(5, "--top", "-t", help="Number of top candidates to show"),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)
    letter_freq, bigram_freq = get_freq_tables(l)
    candidates = crack_substitution.crack(
        content, alpha, letter_freq, bigram_freq, iterations=iterations
    )
    write_output(format_candidates(candidates, top), output)

# -------
# Analyze
# -------


@app.command("analyze")
def analyze_cmd(
    text: str | None = typer.Argument(None, help="Input text (or use --input for file)"),
    input: str | None = typer.Option(None, "--input", "-i", help="Input file"),
    lang: str | None = typer.Option(None, "--lang", "-l", help="Language", case_sensitive=False),
    bigrams_: bool = typer.Option(False, "--bigrams", help="Show bigram frequencies too"),
):
    content = read_input(text, input)
    l = resolve_lang(lang, content)
    alpha = get_alphabet(l.value)

    freq = frequency.sorted(content, alpha)
    out_lines: list[str] = ["Letter Frequencies:"]
    max_freq = freq[0][1] if freq else 1.0

    for ch, f in freq:
        bar_len = int((f / max_freq) * 40) if max_freq > 0 else 0
        bar = "#" * bar_len
        out_lines.append(f"  {ch} {f * 100:5.2f}% {bar}")

    if bigrams_:
        out_lines.append("")
        out_lines.append("Bigram Frequencies (top 20):")
        bg = bigram.sorted(content, alpha)
        for (a, b), f in bg[:20]:
            out_lines.append(f"  {a}{b} {f * 100:5.2f}%")

    write_output("\n".join(out_lines), None)


def run() -> None:
    app()
