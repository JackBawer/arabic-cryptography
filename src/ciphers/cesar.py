from .common import arabic_letters, arabic_frequency_order
from .frequency import build_frequency_table


def cesar_encrypt(text, shift):
    encrypted = ''
    for char in text:
        if char in arabic_letters:
            idx = arabic_letters.index(char)
            encrypted += arabic_letters[(idx + shift) % 28]
        else:
            encrypted += char
    return encrypted


def cesar_decrypt(ciphertext, shift):
    return cesar_encrypt(ciphertext, -shift)


def cesar_break(ciphertext):
    """Guess the shift by finding the most frequent letter"""
    sorted_freq = build_frequency_table(ciphertext)

    # Most frequent letter in cipher
    most_frequent_cipher = sorted_freq[0][0]

    # In Arabic, 'ا' is the most common letter (index 0 in arabic_frequency_order)
    most_frequent_arabic = arabic_frequency_order[0]  # → 'ا'

    # The shift is the difference between their indices
    cipher_idx = arabic_letters.index(most_frequent_cipher)
    arabic_idx = arabic_letters.index(most_frequent_arabic)

    guessed_shift = (cipher_idx - arabic_idx) % 28

    print(f"\n🔑 Most frequent letter in cipher: {most_frequent_cipher}")
    print(f"🔑 Assumed to be: {most_frequent_arabic}")
    print(f"🔑 Guessed shift: {guessed_shift}")

    decrypted = cesar_decrypt(ciphertext, guessed_shift)
    print(f"🔓 Decrypted: {decrypted}")

    return guessed_shift, decrypted
