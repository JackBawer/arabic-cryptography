<div align="center">

# tilsam

**A classical cipher toolkit written in Python**

<!-- Badges (adjust links/labels as needed) -->
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org)
[![Style](https://img.shields.io/badge/style-ruff%2Fblack-000000.svg)](https://github.com/astral-sh/ruff)

</div>

---

## Overview

**tilsam** is a small classical cryptography toolkit providing:

- **Encryption / decryption** for common classical ciphers
- **Cracking** (key recovery attempts) using frequency analysis
- **Language-aware alphabets** (English, French, Arabic)
- **Text analysis**: letter frequency and bigram frequency

It is designed to be simple to run from the command line and easy to reuse as a Python library.

---

## Installation

### Editable install (development)

```sh
git clone <https://github.com/JackBawer/tilsam.git>
cd tilsam

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Normal install

```sh
pip install .
```

> If you publish it later, you can replace the above with:
>
> ```sh
> pip install tilsam
> ```

---

## Usage (CLI)

Run:

```sh
tilsam --help
```

### Caesar

```sh
# Encrypt (shift 3)
tilsam encrypt caesar --lang en --shift 3 "hello world"

# Decrypt
tilsam decrypt caesar --lang en --shift 3 "khoor zruog"

# Crack (tries all shifts and ranks candidates)
tilsam crack caesar --lang en --top 5 "khoor zruog"
```

### Affine

```sh
# Encrypt (a=5, b=8)
tilsam encrypt affine --lang en --key-a 5 --key-b 8 "attack at dawn"

# Decrypt
tilsam decrypt affine --lang en --key-a 5 --key-b 8 "izzisg iz xiov"

# Crack (tries all valid (a,b) pairs and ranks candidates)
tilsam crack affine --lang en --top 5 "izzisg iz xiov"
```

> Note: frequency-based cracking works best on **longer ciphertexts**.

### Substitution

```sh
# Encrypt (key must be a permutation of the alphabet for the chosen language)
tilsam encrypt substitution --lang en \
  --key "zyxwvutsrqponmlkjihgfedcba" \
  "the quick brown fox jumps over the lazy dog"

# Decrypt
tilsam decrypt substitution --lang en \
  --key "zyxwvutsrqponmlkjihgfedcba" \
  "gsv jfrxp yildm ulc qfnkh levi gsv ozab wlt"

# Crack (hill-climbing; run multiple times for better odds)
tilsam crack substitution --lang en --iterations 5000 \
  "PASTE_SUBSTITUTION_CIPHERTEXT_HERE"
```

### Analysis

```sh
# Single-letter frequency analysis
tilsam analyze --lang en "some text to analyze"

# Bigram frequency analysis
tilsam analyze --lang en --bigrams "some text to analyze"
```

### Languages

```sh
# French text
tilsam encrypt caesar --lang fr --shift 3 "bonjour le monde"

# Arabic text (best without diacritics/harakat unless your alphabet supports them)
tilsam encrypt caesar --lang ar --shift 5 "مر��با بالعالم"
```

---

## Usage (GUI)

**tilsam** ships with two GUI flavours: a **web-based React GUI** (recommended) and a legacy Qt desktop GUI.

### Web GUI (React)

The web GUI runs in your browser and is launched directly from the CLI.

#### 1. Install web dependencies

```sh
pip install "tilsam[web]"
```

#### 2. Build the React front-end

```sh
cd gui
npm install
npm run build
cd ..
```

#### 3. Launch the GUI via the CLI

```sh
tilsam gui
```

This starts a local web server on <http://127.0.0.1:5173> and opens your browser automatically.

Available options:

```
tilsam gui --help

  --host        Host to bind to      [default: 127.0.0.1]
  --port  -p    Port to listen on    [default: 5173]
  --no-browser  Skip auto-open browser
```

#### Development mode (hot-reload)

Start Flask first, then start the React dev server in a second terminal.
The dev server automatically proxies `/api/*` requests to Flask:

```sh
# Terminal 1 – Python backend
tilsam gui --no-browser

# Terminal 2 – React dev server
cd gui
npm start
```

Then open <http://localhost:3000>.

---

### Desktop GUI (Qt)

The legacy PySide6 desktop application is still available.

#### Dependencies

Install the GUI dependencies in your virtual environment:

```sh
pip install -r dependencies.txt
```

> If your project does not expose an extra named `gui`, install the required Qt dependency directly
> (for example, `PySide6` or `PyQt6`) according to your `pyproject.toml`.

#### Run the desktop GUI

```sh
tilsam-gui
```

Or as a module:

```sh
python -m tilsam.gui
```

### Notes

- Cracking operations are CPU-bound and may take noticeable time for long ciphertexts and/or large iteration counts.
- If you want more control over parameters and output formatting, prefer the CLI cracking commands.

---

## Usage (Python library)

You can import and use the cipher and cracking modules directly:

```python
from tilsam.alphabets import get_alphabet
from tilsam.ciphers import caesar

alpha = get_alphabet("en")
ciphertext = caesar.encrypt("hello world", shift=3, alphabet=alpha)
plaintext = caesar.decrypt(ciphertext, shift=3, alphabet=alpha)

print(ciphertext)
print(plaintext)
```

Cracking (example):

```python
from tilsam.alphabets import get_alphabet
from tilsam.analysis import tables
from tilsam.crack import caesar as caesar_crack

alpha = get_alphabet("fr")
expected = tables.english_letter_freq()  # (depending on your tables mapping)
candidates = caesar_crack.crack("SVQXFYI...", alpha, expected)

for c in candidates[:5]:
    print(c.score, c.key_description, c.plaintext)
```

---

## Features

### Ciphers
- **Caesar** — shift cipher with integer key
- **Affine** — multiplicative + additive cipher (validates modular inverse where required)
- **Substitution** — full alphabet permutation cipher

### Languages / alphabets
- **English** — 26-letter Latin alphabet
- **French** — Latin alphabet with normalization (project-defined)
- **Arabic** — Arabic alphabet with project-defined normalization

### Cracking
- **Caesar** — brute-force all shifts, ranked by chi-squared scoring
- **Affine** — brute-force all valid (a, b) key pairs, ranked by chi-squared scoring
- **Substitution** — hill-climbing using frequency and bigram scoring (iterations configurable)

### Analysis
- Letter frequency distribution
- Bigram distribution
- Reference frequency tables (project-defined in `tilsam.analysis.tables`)

---

## Project structure

```text
tilsam/
├── pyproject.toml
├── docs/
│   └── tilsam.1.txt
└── src/
    └── tilsam/
        ├── main.py                 # entry point
        ├── cli/
        │   ├── app.py              # Typer app
        │   └── io.py               # CLI I/O helpers
        ├── alphabets/
        │   ├── base.py
        │   ├── english.py
        │   ├── french.py
        │   └── arabic.py
        ├── ciphers/
        │   ├── caesar.py
        │   ├── affine.py
        │   └── substitution.py
        ├── analysis/
        │   ├── frequency.py
        │   ├── bigram.py
        │   ├── scoring.py
        │   └── tables.py
        └── crack/
            ├── candidate.py
            ├── caesar.py
            ├── affine.py
            └── substitution.py
```

The repository also contains a React front-end that is served by the web module:

```text
tilsam/
├── gui/                        # React web GUI (front-end)
│   ├── package.json
│   └── src/
│       └── App.js              # main React component (calls /api/*)
└── src/
    └── tilsam/
        └── web/
            └── server.py       # Flask web server + REST API
```

---

## Development

### Run locally

```sh
pip install -e .
tilsam --help
```

### Notes on cracking
Cracking results depend heavily on:
- ciphertext length
- language tables
- scoring method
- (for substitution) random initializations + number of iterations

For substitution cracking, it’s normal to run the command multiple times and/or increase `--iterations`.

---

## License
MIT License - Copyright (c) 2026 Mohammed Said Louni

MIT License (see `LICENSE`).
