from ciphers.affine import affine_encrypt, affine_decrypt
from ciphers.cesar import cesar_encrypt, cesar_decrypt
from ciphers.substitution import substitution_encrypt, substitution_decrypt
from ciphers.common import arabic_letters

plaintext = "مرحبا"
shift = 3

# Cesar
ciphertext = cesar_encrypt(plaintext, shift)
decrypted = cesar_decrypt(ciphertext, shift)

print("Cesar - Encrypted:", ciphertext)
print("Cesar - Decrypted:", decrypted)

# Affine
a, b = 5, 8
ciphertext2 = affine_encrypt(plaintext, a, b)
decrypted2 = affine_decrypt(ciphertext2, a, b)

print("Affine - Encrypted:", ciphertext2)
print("Affine - Decrypted:", decrypted2)

# Substitution
# Shift the alphabet by 1 as a simple substitution key
key = arabic_letters[1:] + arabic_letters[0]

ciphertext3 = substitution_encrypt(plaintext, key)
decrypted3 = substitution_decrypt(ciphertext3, key)

print("Substitution - Encrypted:", ciphertext3)
print("Substitution - Decrypted:", decrypted3)
