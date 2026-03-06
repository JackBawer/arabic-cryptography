from .common import arabic_letters, arabic_frequency_order


def build_frequency_table(text):
    """Count occurrences of each Arabic letter in text"""
    freq = {}
    total = 0
    for char in text:
        if char in arabic_letters:
            freq[char] = freq.get(char, 0) + 1
            total += 1

    # Sort by frequency descending
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    print("\n📊 Frequency Table:")
    print(f"{'Letter':<10} {'Count':<10} {'Percentage'}")
    for letter, count in sorted_freq:
        print(f"  {letter:<10} {count:<10} {count/total*100:.2f}%")

    return sorted_freq
