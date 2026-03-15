from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from tilsam.alphabets.base import Alphabet
from tilsam.crack.candidate import Candidate


@dataclass(frozen=True)
class _Prepared:
    n: int
    alpha_chars: list[str]
    alpha_index: dict[str, int]
    ct_idx: list[int]
    exp_letter: list[float]
    exp_bigram_pairs: list[tuple[int, int, float]]


def crack(
    ciphertext: str,
    alphabet: Alphabet,
    expected_letter_freq: dict[str, float],
    expected_bigram_freq: dict[tuple[str, str], float],
    iterations: int = 100,
) -> list[Candidate]:
    prep = _prepare(ciphertext, alphabet, expected_letter_freq, expected_bigram_freq)
    if prep is None:
        return [Candidate(plaintext=ciphertext, score=0.0, key_description="key=")]

    base_key = _initial_key_from_letter_freq(prep)
    best_key, best_score = _search(prep, base_key, iterations)

    plaintext = _apply_key(ciphertext, best_key, alphabet)
    return [Candidate(
        plaintext=plaintext,
        score=best_score,
        key_description=f"key={''.join(best_key)}",
    )]


# ── Preparation ───────────────────────────────────────────────────────────────

def _canonicalizer(alphabet: Alphabet) -> Callable[[str], str]:
    fn = getattr(alphabet, "canonicalize", None)
    return fn if callable(fn) else lambda ch: ch  # type: ignore[return-value]


def _prepare(
    ciphertext: str,
    alphabet: Alphabet,
    expected_letter_freq: dict[str, float],
    expected_bigram_freq: dict[tuple[str, str], float],
) -> _Prepared | None:
    n = alphabet.size()
    if n <= 1:
        return None

    alpha_chars: list[str] = []
    alpha_index: dict[str, int] = {}
    for i in range(n):
        ch = alphabet.index_to_char(i)
        if ch is None:
            raise RuntimeError(f"alphabet.index_to_char({i}) returned None")
        alpha_chars.append(ch)
        alpha_index[ch] = i

    canon = _canonicalizer(alphabet)
    ct_idx: list[int] = []
    for ch in ciphertext:
        idx = alphabet.char_to_index(canon(ch))
        if idx is not None:
            ct_idx.append(idx)

    if len(ct_idx) < 2:
        return None

    exp_letter = [float(expected_letter_freq.get(ch, 0.0)) for ch in alpha_chars]

    exp_bigram_pairs: list[tuple[int, int, float]] = []
    for (a, b), f in expected_bigram_freq.items():
        ia = alphabet.char_to_index(a)
        ib = alphabet.char_to_index(b)
        if ia is not None and ib is not None and f > 0.0:
            exp_bigram_pairs.append((ia, ib, float(f)))

    return _Prepared(
        n=n,
        alpha_chars=alpha_chars,
        alpha_index=alpha_index,
        ct_idx=ct_idx,
        exp_letter=exp_letter,
        exp_bigram_pairs=exp_bigram_pairs,
    )


# ── Initial key ───────────────────────────────────────────────────────────────

def _initial_key_from_letter_freq(prep: _Prepared) -> list[str]:
    """Map most-frequent ciphertext chars to most-frequent expected plaintext chars."""
    n = prep.n
    counts = [0] * n
    for i in prep.ct_idx:
        counts[i] += 1

    cipher_rank = sorted(range(n), key=lambda i: counts[i], reverse=True)
    exp_rank = sorted(range(n), key=lambda i: prep.exp_letter[i], reverse=True)

    key = [prep.alpha_chars[0]] * n
    for r in range(n):
        key[cipher_rank[r]] = prep.alpha_chars[exp_rank[r]]

    _fill_missing(key, prep.alpha_chars)
    return key


# ── Search ────────────────────────────────────────────────────────────────────

def _search(prep: _Prepared, base_key: list[str], iterations: int) -> tuple[list[str], float]:
    """
    Multi-restart hill-climbing.

    iterations maps directly to random-swap trials per restart so the UI
    control is meaningful across its full range. After all restarts a final
    deterministic exhaustive-swap polish pass is applied (mirrors the Rust
    version's approach).
    """
    scorer = _make_scorer(prep)
    rng = random.Random()          # non-deterministic seed

    # Scale restarts and trials from iterations so the control is useful
    # iterations=10  →  2 restarts, ~1 000 trials each
    # iterations=100 →  5 restarts, ~4 000 trials each
    # iterations=1 000 → 10 restarts, ~20 000 trials each
    restarts = max(2, min(20, iterations // 20))
    trials = max(500, min(50_000, iterations * 40))

    best_key = base_key.copy()
    best_score = scorer(best_key)

    for r in range(restarts):
        key = base_key.copy()
        # Each restart perturbs by a different amount so they explore
        # different parts of the space.
        _randomize_key(key, rng, swaps=max(1, prep.n // 4 + r * 2))
        cur_score = scorer(key)

        for _ in range(trials):
            i = rng.randrange(prep.n)
            j = rng.randrange(prep.n)
            if i == j:
                continue
            key[i], key[j] = key[j], key[i]
            new_score = scorer(key)
            if new_score < cur_score:
                cur_score = new_score
                if new_score < best_score:
                    best_score = new_score
                    best_key = key.copy()
            else:
                key[i], key[j] = key[j], key[i]

    # Deterministic polish: exhaustive pairwise sweep until no improvement
    # (same as Rust version's hill-climbing loop)
    best_key, best_score = _exhaustive_polish(best_key, best_score, scorer, prep.n)

    return best_key, best_score


def _exhaustive_polish(
    key: list[str],
    score: float,
    scorer,
    n: int,
) -> tuple[list[str], float]:
    """One or more passes of all O(n²) swaps until no swap improves the score."""
    improved = True
    while improved:
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                key[i], key[j] = key[j], key[i]
                new_score = scorer(key)
                if new_score < score:
                    score = new_score
                    improved = True
                else:
                    key[i], key[j] = key[j], key[i]
    return key, score


# ── Scorer ────────────────────────────────────────────────────────────────────

def _make_scorer(prep: _Prepared):
    """
    Returns a callable key → float (lower is better).

    Uses only bigram chi-squared for the main score — letter frequencies are
    already baked into the initial key guess and add noise during hill-climbing.
    A small letter penalty is kept to break ties on very short texts.
    """
    n = prep.n
    ct_idx = prep.ct_idx
    alpha_index = prep.alpha_index
    exp_letter = prep.exp_letter
    exp_bigram_pairs = prep.exp_bigram_pairs

    total = float(len(ct_idx))
    total_b = float(len(ct_idx) - 1)

    def scorer(key: list[str]) -> float:
        counts = [0] * n
        bcounts = [[0] * n for _ in range(n)]
        prev: int | None = None
        for ci in ct_idx:
            pi = alpha_index[key[ci]]
            counts[pi] += 1
            if prev is not None:
                bcounts[prev][pi] += 1
            prev = pi

        # Bigram chi-squared (primary signal)
        bigram_score = 0.0
        if total_b > 0.0:
            for i, j, exp in exp_bigram_pairs:
                obs = bcounts[i][j] / total_b
                diff = obs - exp
                bigram_score += (diff * diff) / exp

        # Letter chi-squared (small tiebreaker, less weight than before)
        letter_score = 0.0
        for i, exp in enumerate(exp_letter):
            if exp > 0.0:
                obs = counts[i] / total
                diff = obs - exp
                letter_score += (diff * diff) / exp

        return 0.1 * letter_score + 0.9 * bigram_score

    return scorer


# ── Key utilities ─────────────────────────────────────────────────────────────

def _apply_key(ciphertext: str, key: list[str], alphabet: Alphabet) -> str:
    canon = _canonicalizer(alphabet)
    out: list[str] = []
    for ch in ciphertext:
        ch = canon(ch)
        idx = alphabet.char_to_index(ch)
        out.append(ch if idx is None else key[idx])
    return "".join(out)


def _randomize_key(key: list[str], rng: random.Random, *, swaps: int) -> None:
    n = len(key)
    for _ in range(swaps):
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i != j:
            key[i], key[j] = key[j], key[i]


def _fill_missing(key: list[str], alpha_chars: list[str]) -> None:
    used = [False] * len(alpha_chars)
    needs_fill: list[int] = []
    for i, k in enumerate(key):
        try:
            pos = alpha_chars.index(k)
        except ValueError:
            needs_fill.append(i)
            continue
        if used[pos]:
            needs_fill.append(i)
        else:
            used[pos] = True
    unused = [c for idx, c in enumerate(alpha_chars) if not used[idx]]
    for i in needs_fill:
        if unused:
            key[i] = unused.pop()
