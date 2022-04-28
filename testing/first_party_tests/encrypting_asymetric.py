#both digital signature and public keys must be handled in an appropriate manner when transfering across a network, this code demonstrates the required principles for this.

import mukkava_encryption
import nacl
from nacl.signing import VerifyKey

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
asymetric = mukkava_encryption.Asymetric()

encrypted = symetric.encrypt(asymetric.public_encryption_key.encode())
decrypted = symetric.decrypt(encrypted)
key = nacl.public.PublicKey(decrypted)

print(asymetric.public_encryption_key, type(asymetric.public_encryption_key),"\n", asymetric.public_encryption_key.encode(), type(asymetric.public_encryption_key.encode()))
print(decrypted, type(decrypted))
print(key, type(key))

encrypted = symetric.encrypt(asymetric.public_verify_key.encode())
decrypted = VerifyKey(encrypted)