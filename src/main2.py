from ciphers.cesar import cesar_encrypt, cesar_decrypt, cesar_break
from ciphers.affine import affine_encrypt, affine_decrypt, affine_break
from ciphers.substitution import substitution_encrypt, substitution_decrypt, substitution_break

# Ayat Al-Kursi
plaintext = """اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ
لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ
يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ
وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا وَهُوَ الْعَلِيُّ الْعَظِيمُ"""

print("=" * 60)
print("Original text:")
print(plaintext)

# ─────────────────────────────────────────
# César
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("CÉSAR CIPHER")
print("=" * 60)

shift = 7
cesar_cipher = cesar_encrypt(plaintext, shift)
print(f"Encrypted (shift={shift}):\n{cesar_cipher}")
print(f"\nDecrypted:\n{cesar_decrypt(cesar_cipher, shift)}")
print("\n--- Breaking César ---")
cesar_break(cesar_cipher)

# ─────────────────────────────────────────
# Affine
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("AFFINE CIPHER")
print("=" * 60)

a, b = 5, 8
affine_cipher = affine_encrypt(plaintext, a, b)
print(f"Encrypted (a={a}, b={b}):\n{affine_cipher}")
print(f"\nDecrypted:\n{affine_decrypt(affine_cipher, a, b)}")
print("\n--- Breaking Affine ---")
affine_break(affine_cipher)

# ─────────────────────────────────────────
# Substitution
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("SUBSTITUTION CIPHER")
print("=" * 60)

key = 'بتثجحخدذرزسشصضطظعغفقكلمنهويا'
sub_cipher = substitution_encrypt(plaintext, key)
print(f"Encrypted:\n{sub_cipher}")
print(f"\nDecrypted:\n{substitution_decrypt(sub_cipher, key)}")
print("\n--- Breaking Substitution ---")
substitution_break(sub_cipher)
