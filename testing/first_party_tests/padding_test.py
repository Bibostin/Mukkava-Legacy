'''
One problem with headers is that they MUST be encrypted, a malicious listener could
'''
import mukkava_encryption


symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")

def pad(message):
    encrypted_message = symetric.encrypt(message)
    data = f"{len(encrypted_message):<{mukkava_encryption.message_length_hsize}}"
    encrypted_header = symetric.encrypt(data)
    print(f"Message: {message}  Message Length: {len(message)}\n"
          f"encrypted Message: {encrypted_message}  Encrypted Message Length {len(encrypted_message)}\n"
          f"header data: {data}  header data Length: {len(data)}\n"
          f"encrypted header data: {encrypted_header}  encrypted header data length: {len(encrypted_header)}\n")

pad("test")
pad("it doesn't matter how long the message is, as long as it length can be represented in 4 bytes I can make a encrypted header (that will allways be 44 charecter bytes long) for it that defines this messages length!")
