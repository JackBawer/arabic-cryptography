from .common import arabic_letters
from .normalize import normalize_arabic


def build_frequency_table(text, normalize=True, show_table=True):
    """Count occurrences of each Arabic letter in text (optionally normalized)."""
    if normalize:
        text = normalize_arabic(text)

    freq = {}
    total = 0
    for char in text:
        if char in arabic_letters:
            freq[char] = freq.get(char, 0) + 1
            total += 1

    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    if show_table:
        print("\nFrequency Table:")
        print(f"{'Letter':<10} {'Count':<10} {'Percentage'}")
        for letter, count in sorted_freq:
            pct = (count / total * 100) if total else 0.0
            print(f"  {letter:<10} {count:<10} {pct:.2f}%")

    return sorted_freq
