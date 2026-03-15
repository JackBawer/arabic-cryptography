#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests/data/tmp

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

assert_contains() {
  local file="$1"
  local needle="$2"
  grep -qiF "$needle" "$file" || fail "Expected '$needle' in $file"
}

# ---------- Caesar ----------
for lang in en fr ar; do
  in="tests/data/${lang}_plain.txt"
  c="tests/data/tmp/${lang}_caesar.txt"
  r="tests/data/tmp/${lang}_caesar_roundtrip.txt"
  k="tests/data/tmp/${lang}_caesar_crack.txt"
  a="tests/data/tmp/${lang}_analyze.txt"

  tilsam encrypt caesar --shift 3 --lang "$lang" --input "$in" --output "$c"
  tilsam decrypt caesar --shift 3 --lang "$lang" --input "$c" --output "$r"
  tilsam crack caesar --lang "$lang" --input "$c" --output "$k" --top 3
  tilsam analyze --lang "$lang" --input "$in" --output "$a" --bigrams

  case "$lang" in
    en) assert_contains "$r" "THIS IS A SMALL ENGLISH TEXT SAMPLE" ;;
    fr) assert_contains "$r" "C'EST UN PETIT TEXTE" ;;
    ar) assert_contains "$r" "الله لا اله" ;;
  esac
  ok "Caesar $lang: encrypt/decrypt/crack/analyze"
done

# ---------- Affine ----------
for lang in en fr ar; do
  in="tests/data/${lang}_plain.txt"
  c="tests/data/tmp/${lang}_affine.txt"
  r="tests/data/tmp/${lang}_affine_roundtrip.txt"
  k="tests/data/tmp/${lang}_affine_crack.txt"

  tilsam encrypt affine --key-a 5 --key-b 8 --lang "$lang" --input "$in" --output "$c" \
    || fail "Affine encrypt failed for $lang (maybe invalid a for that alphabet). Try another a."

  tilsam decrypt affine --key-a 5 --key-b 8 --lang "$lang" --input "$c" --output "$r" \
    || fail "Affine decrypt failed for $lang"

  tilsam crack affine --lang "$lang" --input "$c" --output "$k" --top 3 \
    || fail "Affine crack failed for $lang"

  case "$lang" in
    en) assert_contains "$r" "THIS IS A SMALL ENGLISH TEXT SAMPLE" ;;
    fr) assert_contains "$r" "C'EST UN PETIT TEXTE" ;;
    ar) assert_contains "$r" "الله لا اله" ;;
  esac
  ok "Affine $lang: encrypt/decrypt/crack"
done

# ---------- Substitution ----------
gen_sub_key() {
  local lang="$1"
  python - "$lang" <<'PY'
from tilsam.alphabets import get_alphabet
import sys

lang = sys.argv[1]
alpha = get_alphabet(lang)

# Try common shapes: attribute .chars, method .chars(), or fallback
chars = None
if hasattr(alpha, "chars"):
    c = alpha.chars
    if callable(c):
        chars = list(c())
    else:
        chars = list(c)
elif hasattr(alpha, "characters"):
    chars = list(alpha.characters)

if not chars:
    raise RuntimeError(f"Could not extract alphabet characters for lang={lang!r}")

s = "".join(chars)
print(s[::-1])
PY
}

for lang in en fr ar; do
  in="tests/data/${lang}_plain.txt"
  c="tests/data/tmp/${lang}_sub.txt"
  r="tests/data/tmp/${lang}_sub_roundtrip.txt"
  k="tests/data/tmp/${lang}_sub_crack.txt"

  key="$(gen_sub_key "$lang")"

  tilsam encrypt substitution --key "$key" --lang "$lang" --input "$in" --output "$c"
  tilsam decrypt substitution --key "$key" --lang "$lang" --input "$c" --output "$r"
  tilsam crack substitution --lang "$lang" --input "$c" --output "$k" --iterations 500 --top 1

  case "$lang" in
    en) assert_contains "$r" "THIS IS A SMALL ENGLISH TEXT SAMPLE" ;;
    fr) assert_contains "$r" "C'EST UN PETIT TEXTE" ;;
    ar) assert_contains "$r" "الله لا اله" ;;
  esac
  ok "Substitution $lang: encrypt/decrypt/crack"
done

ok "ALL CLI TESTS PASSED"
