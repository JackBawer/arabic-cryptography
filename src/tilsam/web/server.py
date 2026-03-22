from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request, send_from_directory

from tilsam.alphabets import get_alphabet
from tilsam.analysis import bigram as bigram_mod
from tilsam.analysis import frequency as freq_mod
from tilsam.analysis import tables
from tilsam.ciphers import affine as cipher_affine
from tilsam.ciphers import caesar as cipher_caesar
from tilsam.ciphers import substitution as cipher_substitution
from tilsam.crack import affine as crack_affine
from tilsam.crack import caesar as crack_caesar
from tilsam.crack import substitution as crack_substitution

# parents[3] goes: server.py -> web/ -> tilsam/ -> src/ -> repo root
_GUI_BUILD = Path(__file__).resolve().parents[3] / "gui" / "build"

_LANG_MAP = {
    "english": "en",
    "french": "fr",
    "arabic": "ar",
    "en": "en",
    "fr": "fr",
    "ar": "ar",
}

_ARABIC_UNICODE_START = 0x0600
_ARABIC_UNICODE_END = 0x06FF


def _resolve_lang(language: str, text: str) -> str:
    """Return a two-letter lang code, detecting from text when language is 'auto'."""
    if language.lower() == "auto":
        arabic_count = sum(
            1 for c in text if _ARABIC_UNICODE_START <= ord(c) <= _ARABIC_UNICODE_END
        )
        latin_count = sum(1 for c in text if c.isascii() and c.isalpha())
        if arabic_count > latin_count:
            return "ar"
        french_accents = set("àâäçèéêëîïôöùûüÿœæÀÂÄÇÈÉÊËÎÏÔÖÙÛÜŸŒÆ")
        if any(c in french_accents for c in text):
            return "fr"
        return "en"
    return _LANG_MAP.get(language.lower(), "en")


def _get_freq_tables(lang: str):
    if lang == "en":
        return tables.english_letter_freq(), tables.english_bigram_freq()
    if lang == "ar":
        return tables.arabic_letter_freq(), tables.arabic_bigram_freq()
    if lang == "fr":
        return tables.french_letter_freq(), tables.french_bigram_freq()
    raise ValueError(f"unsupported language: {lang!r}")


def _format_candidates(candidates: list[Any], top: int) -> str:
    lines: list[str] = []
    for i, c in enumerate(candidates[:top], start=1):
        lines.append(f"#{i} [score: {c.score:.4f}] ({c.key_description})")
        lines.append(f"  {c.plaintext}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # ------------------------------------------------------------------
    # API – execute (encrypt / decrypt / crack)
    # ------------------------------------------------------------------

    @app.post("/api/execute")
    def api_execute():
        data = request.get_json(force=True, silent=True) or {}
        cipher: str = data.get("cipher", "Caesar")
        language: str = data.get("language", "English")
        mode: str = data.get("mode", "Encrypt")
        text: str = data.get("text", "")

        if not text:
            return jsonify({"error": "No input text provided"}), 400

        lang = _resolve_lang(language, text)
        try:
            alpha = get_alphabet(lang)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

        cipher_lower = cipher.lower()
        mode_lower = mode.lower()

        try:
            if mode_lower in ("encrypt", "decrypt"):
                fn_map = {
                    ("caesar", "encrypt"): lambda: cipher_caesar.encrypt(
                        text, int(data.get("shift", 3)), alpha
                    ),
                    ("caesar", "decrypt"): lambda: cipher_caesar.decrypt(
                        text, int(data.get("shift", 3)), alpha
                    ),
                    ("affine", "encrypt"): lambda: cipher_affine.encrypt(
                        text,
                        int(data.get("affineA", 5)),
                        int(data.get("affineB", 8)),
                        alpha,
                    ),
                    ("affine", "decrypt"): lambda: cipher_affine.decrypt(
                        text,
                        int(data.get("affineA", 5)),
                        int(data.get("affineB", 8)),
                        alpha,
                    ),
                    ("substitution", "encrypt"): lambda: cipher_substitution.encrypt(
                        text, _sub_key_string(data, alpha), alpha
                    ),
                    ("substitution", "decrypt"): lambda: cipher_substitution.decrypt(
                        text, _sub_key_string(data, alpha), alpha
                    ),
                }
                key = (cipher_lower, mode_lower)
                if key not in fn_map:
                    return jsonify({"error": f"Unknown cipher/mode: {cipher}/{mode}"}), 400
                result = fn_map[key]()
                return jsonify({"result": result})

            if mode_lower == "crack":
                top = int(data.get("top", 5))
                letter_freq, bigram_freq = _get_freq_tables(lang)
                if cipher_lower == "caesar":
                    candidates = crack_caesar.crack(text, alpha, letter_freq)
                elif cipher_lower == "affine":
                    candidates = crack_affine.crack(text, alpha, letter_freq)
                elif cipher_lower == "substitution":
                    iterations = int(data.get("iterations", 100))
                    candidates = crack_substitution.crack(
                        text, alpha, letter_freq, bigram_freq, iterations=iterations
                    )
                else:
                    return jsonify({"error": f"Unknown cipher: {cipher}"}), 400
                return jsonify({"result": _format_candidates(candidates, top)})

            return jsonify({"error": f"Unknown mode: {mode}"}), 400

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # ------------------------------------------------------------------
    # API – analyze
    # ------------------------------------------------------------------

    @app.post("/api/analyze")
    def api_analyze():
        data = request.get_json(force=True, silent=True) or {}
        text: str = data.get("text", "")
        language: str = data.get("language", "English")
        show_bigrams: bool = bool(data.get("showBigrams", False))

        if not text:
            return jsonify({"error": "No input text provided"}), 400

        lang = _resolve_lang(language, text)
        try:
            alpha = get_alphabet(lang)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

        freq = freq_mod.sorted(text, alpha)
        max_freq = freq[0][1] if freq else 1.0
        frequencies = [
            {
                "letter": ch,
                "freq": round(f * 100, 2),
                "rel": round(f / max_freq, 4) if max_freq > 0 else 0,
            }
            for ch, f in freq
        ]

        result: dict = {"frequencies": frequencies}

        if show_bigrams:
            bg = bigram_mod.sorted(text, alpha)
            result["bigrams"] = [
                {"pair": f"{a}{b}", "freq": round(f * 100, 2)}
                for (a, b), f in bg[:20]
            ]

        return jsonify(result)

    # ------------------------------------------------------------------
    # Serve the built React app (static files)
    # ------------------------------------------------------------------

    @app.get("/")
    @app.get("/<path:path>")
    def serve_static(path: str = ""):
        if not _GUI_BUILD.exists():
            return (
                "React app not built. Run 'npm run build' inside the gui/ directory first.",
                503,
            )
        target = _GUI_BUILD / path if path else _GUI_BUILD / "index.html"
        if target.exists() and target.is_file():
            return send_from_directory(str(_GUI_BUILD), path if path else "index.html")
        # SPA fallback – let React Router handle unknown paths
        return send_from_directory(str(_GUI_BUILD), "index.html")

    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sub_key_string(data: dict, alpha) -> str:
    """
    Accept substitution key as either:
      - a plain string (e.g. "ZYXWVUTSRQPONMLKJIHGFEDCBA")
      - a dict mapping letter -> cipher-letter (from the React grid)
    """
    raw = data.get("subKey", "")
    if isinstance(raw, dict):
        # React grid sends {A: "Z", B: "Y", ...}; build ordered string
        if hasattr(alpha, "chars"):
            chars = alpha.chars
            plain_letters = list(chars() if callable(chars) else chars)
        elif hasattr(alpha, "characters"):
            plain_letters = list(alpha.characters)
        else:
            plain_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return "".join(raw.get(ch, ch) for ch in plain_letters)
    return str(raw)
