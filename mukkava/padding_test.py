'''
One problem with headers is that they MUST be encrypted, a malicious listener could
'''
import mukkava_encryption


symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
asym1 = mukkava_encryption.Asymetric()
asym2 = mukkava_encryption.Asymetric()

asym1.setup(asym2.public_encryption_key_bytes, asym2.public_verify_key_bytes)
asym2.setup(asym1.public_encryption_key_bytes, asym1.public_verify_key_bytes)

def symetric_pad(message):
    encrypted_message = symetric.encrypt(message)
    data = f"{len(encrypted_message):<{mukkava_encryption.message_length_hsize}}"
    encrypted_header = symetric.encrypt(data)
    print(f"Message: {message}  Message Length: {len(message)}\n"
          f"encrypted Message: {encrypted_message}  Encrypted Message Length {len(encrypted_message)}\n"
          f"header data: {data}  header data Length: {len(data)}\n"
          f"encrypted header data: {encrypted_header}  encrypted header data length: {len(encrypted_header)}\n")

def asymetric_pad(message):
    encrypted_message = asym1.encrypt(message)
    data = f"{len(encrypted_message):<{mukkava_encryption.message_length_hsize}}"
    encrypted_header = asym1.encrypt(data)
    print(f"Message: {message}  Message Length: {len(message)}\n"
          f"encrypted Message: {encrypted_message}  Encrypted Message Length {len(encrypted_message)}\n"
          f"header data: {data}  header data Length: {len(data)}\n"
          f"encrypted header data: {encrypted_header}  encrypted header data length: {len(encrypted_header)}\n")


# symetric_pad("test")
# symetric_pad("it doesn't matter how long the message is, as long as it length can be represented in 4 bytes I can make a encrypted header (that will allways be 44 charecter bytes long) for it that defines this messages length!")
# asymetric_pad("this is a asym test")
# asymetric_pad("this is a asym test thats slightly larger and attempts to proove asym header lengths normalise at 108 charecters of length")

symetric_pad("TEXT")
symetric_pad("VOIC")
symetric_pad("HDSK")
symetric_pad("TEXT")
symetric_pad("VOIC")
symetric_pad("HDSK")