"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.secret
from nacl.signing import SigningKey, VerifyKey



#SYMETRIC (PAKE)
key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)  # This must be kept secret, this is the combination to your safe
box = nacl.secret.SecretBox(key)  # This is your safe, you can use it to encrypt or decrypt messages
message = b"The president will be exiting through the lower levels"  # This is our message to send, it must be a bytestring as SecretBox will treat it as just a binary blob of data.
encrypted = box.encrypt(message)  # Encrypt our message, it will be exactly 40 bytes longer than the original message as it stores authentication information and the nonce alongside it.
assert len(encrypted) == len(message) + box.NONCE_SIZE + box.MACBYTES
plaintext = box.decrypt(encrypted)
print(plaintext.decode('utf-8'))


#ASYMETRIC
skbob = PrivateKey.generate()  # Generate Bob's private key, which must be kept secret
pkbob = skbob.public_key  # Bob's public key can be given to anyone wishing to send Bob an encrypted message
skalice = PrivateKey.generate()  # Alice does the same and then Alice and Bob exchange public keys
pkalice = skalice.public_key
bob_box = Box(skbob, pkalice)  # Bob wishes to send Alice an encrypted message so Bob must make a Box with his private key and Alice's public key
message = b"Kill all humans"  # This is our message to send, it must be a bytestring as Box will treat it as just a binary blob of data.
encrypted = bob_box.encrypt(message)  # Encrypt our message, it will be exactly 40 bytes longer than the original message as it stores authentication information and the nonce alongside it.
alice_box = Box(skalice, pkbob)  # Alice creates a second box with her private key to decrypt the message
plaintext = alice_box.decrypt(encrypted)  # Decrypt our message, an exception will be raised if the encryption was tampered with or there was otherwise an error.
print(plaintext.decode('utf-8'))

#DIGITAL SIGNATURE

#sign a message
signing_key = SigningKey.generate()  # Generate a new random signing key
signed = signing_key.sign(b"Attack at Dawn")  # Sign a message with the signing key
verify_key = signing_key.verify_key  # Obtain the verify key for a given signing key
verify_key_bytes = verify_key.encode()  # Serialize the verify key to send it to a third party

#verify a message
verify_key = VerifyKey(verify_key_bytes)  # Create a VerifyKey object from a hex serialized public key

# Check the validity of a message's signature. The message and the signature can either be passed together, or  separately if the signature is decoded to raw bytes.
verify_key.verify(signed)
#OR
verify_key.verify(signed.message, signed.signature)


forged = signed[:-1] + bytes([int(signed[-1]) ^ 1]) # Alter the signed message text  Will raise nacl.exceptions.BadSignatureError, since the signature check is failing
verify_key.verify(forged)
#Traceback (most recent call last): nacl.exceptions.BadSignatureError: Signature was forged or corrupt