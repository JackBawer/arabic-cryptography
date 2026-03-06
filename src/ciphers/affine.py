from .common import arabic_letters, arabic_frequency_order
from .frequency import build_frequency_table


def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def affine_encrypt(text, a, b):
    encrypted = ''
    for char in text:
        if char in arabic_letters:
            x = arabic_letters.index(char)
            encrypted += arabic_letters[(a * x + b) % 28]
        else:
            encrypted += char
    return encrypted


def affine_decrypt(text, a, b):
    a_inv = mod_inverse(a, 28)
    if a_inv is None:
        raise ValueError(f"No modular inverse for a={a}, n=28.")
    decrypted = ''
    for char in text:
        if char in arabic_letters:
            y = arabic_letters.index(char)
            decrypted += arabic_letters[(a_inv * (y - b)) % 28]
        else:
            decrypted += char
    return decrypted


def affine_break(ciphertext):
    sorted_freq = build_frequency_table(ciphertext)

    # Try pairs until we find one that works
    for i in range(len(sorted_freq)):
        for j in range(len(sorted_freq)):
            if i == j:
                continue

            c1 = arabic_letters.index(sorted_freq[i][0])
            c2 = arabic_letters.index(sorted_freq[j][0])
            p1 = arabic_letters.index(arabic_frequency_order[i])
            p2 = arabic_letters.index(arabic_frequency_order[j])

            diff_c = (c1 - c2) % 28
            diff_p = (p1 - p2) % 28

            if diff_p == 0:
                continue

            diff_p_inv = mod_inverse(diff_p, 28)
            if diff_p_inv is None:
                continue

            a = (diff_c * diff_p_inv) % 28
            if mod_inverse(a, 28) is None:
                continue

            b = (c1 - a * p1) % 28

            print(f"🔑 Trying pair {sorted_freq[i][0]}/{sorted_freq[j][0]} → a={a}, b={b}")
            decrypted = affine_decrypt(ciphertext, a, b)

            # Check if result looks like Arabic text (basic sanity check)
            arabic_ratio = sum(1 for c in decrypted if c in arabic_letters) / max(len(decrypted), 1)
            if arabic_ratio > 0.3:
                print(f"✅ Found valid key: a={a}, b={b}")
                print(f"🔓 Decrypted: {decrypted}")
                return (a, b), decrypted

    print("❌ Could not break affine cipher.")
    return None, None
