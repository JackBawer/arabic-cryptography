import random
from .common import arabic_letters, arabic_frequency_order
from .frequency import build_frequency_table
from .normalize import normalize_arabic


def substitution_encrypt(text, key):
    table = dict(zip(arabic_letters, key))
    encrypted = ""
    for char in text:
        encrypted += table.get(char, char)
    return encrypted


def substitution_decrypt(text, key):
    reverse_table = dict(zip(key, arabic_letters))
    decrypted = ""
    for char in text:
        decrypted += reverse_table.get(char, char)
    return decrypted


def _complete_mapping(guessed_map):
    """
    guessed_map: dict cipher_letter -> plain_letter (partial)
    Returns a dict cipher_letter -> plain_letter (full for letters seen + assigns remaining).
    """
    used_plain = set(guessed_map.values())
    remaining_plain = [ch for ch in arabic_letters if ch not in used_plain]

    # ensure deterministic completion order (helps reproducibility)
    remaining_plain.sort(key=lambda c: arabic_letters.index(c))

    full = dict(guessed_map)
    for c in arabic_letters:
        if c not in full:
            full[c] = remaining_plain.pop(0)
    return full


def _mapping_to_key(cipher_to_plain):
    """Convert cipher->plain mapping into a substitution 'key' compatible with substitution_decrypt."""
    # substitution_decrypt expects key = cipher_alphabet_in_plaintext_order? No:
    # your substitution_decrypt uses reverse_table = dict(zip(key, arabic_letters))
    # which maps cipher_letter -> plain_letter.
    # So `key` must be a string where position i corresponds to plaintext letter arabic_letters[i]
    # during encryption, but for decrypt we need the actual cipher alphabet.
    #
    # Easiest: produce `key` as the encryption key (plain->cipher), then use substitution_decrypt.
    plain_to_cipher = {plain: cipher for cipher, plain in cipher_to_plain.items()}
    return "".join(plain_to_cipher[p] for p in arabic_letters)


def _score_arabic(text):
    """
    Very small Arabic scoring heuristic.
    Higher is better.
    """
    # Common patterns/words (in normalized text)
    patterns = [
        "ال", "لل", "من", "في", "على", "و", "الله", "لا", "ما", "هو", "هم",
        "هذا", "هذه", "ذلك", "الذي", "التي", "كان", "كانت", "لم", "لن"
    ]

    score = 0
    for p in patterns:
        score += text.count(p) * (5 if len(p) >= 2 else 1)

    # reward spaces (word boundaries) a bit (helps avoid totally random text)
    score += text.count(" ") * 0.2

    return score


def _decrypt_with_cipher_to_plain(ciphertext, cipher_to_plain):
    return "".join(cipher_to_plain.get(ch, ch) for ch in ciphertext)


def substitution_break(ciphertext, normalize=True, iterations=5000, restarts=10, seed=0):
    """
    Improved substitution break:
    - Initial key guess via frequency table (mono-gram)
    - Then hill-climb swaps to maximize an Arabic pattern score

    Still simple, no external libs, and stays "language-frequency" driven.
    """
    rnd = random.Random(seed)

    text = normalize_arabic(ciphertext) if normalize else ciphertext

    # 1) initial mono-gram frequency guess (cipher -> plain)
    sorted_freq = build_frequency_table(text, normalize=False, show_table=True)

    guessed = {}
    for i, (cipher_letter, _) in enumerate(sorted_freq):
        if i < len(arabic_frequency_order):
            guessed[cipher_letter] = arabic_frequency_order[i]

    best_map = _complete_mapping(guessed)
    best_plain = _decrypt_with_cipher_to_plain(text, best_map)
    best_score = _score_arabic(best_plain)

    # 2) refine by hill-climbing: swap plaintext assignments between two cipher letters
    cipher_letters_present = [c for c in arabic_letters if c in set(ch for ch in text if ch in arabic_letters)]
    if len(cipher_letters_present) < 2:
        # nothing to optimize
        key = _mapping_to_key(best_map)
        return key, best_plain

    for _ in range(restarts):
        current = dict(best_map)
        current_plain = _decrypt_with_cipher_to_plain(text, current)
        current_score = _score_arabic(current_plain)

        for _ in range(iterations):
            c1, c2 = rnd.sample(cipher_letters_present, 2)

            # swap their plaintext assignments
            trial = dict(current)
            trial[c1], trial[c2] = trial[c2], trial[c1]

            trial_plain = _decrypt_with_cipher_to_plain(text, trial)
            trial_score = _score_arabic(trial_plain)

            if trial_score >= current_score:
                current = trial
                current_score = trial_score
                current_plain = trial_plain

                if current_score > best_score:
                    best_map = current
                    best_score = current_score
                    best_plain = current_plain

    print("Best score:", best_score)
    print("Decrypted (normalized view):")
    print(best_plain)

    best_key = _mapping_to_key(best_map)
    return best_key, best_plain
