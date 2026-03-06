from .common import arabic_letters, arabic_frequency_order
from .frequency import build_frequency_table


def substitution_encrypt(text, key):
    table = dict(zip(arabic_letters, key))
    encrypted = ''
    for char in text:
        encrypted += table.get(char, char)
    return encrypted


def substitution_decrypt(text, key):
    reverse_table = dict(zip(key, arabic_letters))
    decrypted = ''
    for char in text:
        decrypted += reverse_table.get(char, char)
    return decrypted


def substitution_break(ciphertext):
    sorted_freq = build_frequency_table(ciphertext)

    guessed_key = {}
    for i, (cipher_letter, _) in enumerate(sorted_freq):
        if i < len(arabic_frequency_order):
            guessed_key[cipher_letter] = arabic_frequency_order[i]

    print("\n🔑 Guessed mapping:")
    for cipher, plain in guessed_key.items():
        print(f"  {cipher} → {plain}")

    decrypted = ''.join(guessed_key.get(char, char) for char in ciphertext)
    print(f"🔓 Decrypted: {decrypted}")

    # Manual correction
    print("\n✏️  Enter corrections (e.g. 'و ه' to map و→ه). Press Enter to skip.")
    while True:
        correction = input("Correct mapping (or Enter to stop): ").strip()
        if not correction:
            break
        parts = correction.split()
        if len(parts) == 2:
            guessed_key[parts[0]] = parts[1]
            decrypted = ''.join(guessed_key.get(char, char) for char in ciphertext)
            print(f"🔓 Updated: {decrypted}")

    return guessed_key, decrypted
