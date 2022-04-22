'''
One problem with headers is that they MUST be encrypted, a malicious listener could
'''
import mukkava_encryption

length_headersize = 4



symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")

def pad(message):
    encrypted_message = symetric.encrypt(message)
    data = f"{len(encrypted_message):<{length_headersize}}"
    encrypted_header = symetric.encrypt(data)
    print(f"Message: {message}  Message Length: {len(message)}\n"
          f"encrypted Message: {encrypted_message}  Encrypted Message Length {len(encrypted_message)}\n"
          f"header data: {data}  header data Length: {len(data)}\n"
          f"encrypted header: {encrypted_header}  encrypted header length: {len(encrypted_header)}\n")

pad("test")
pad("it doesn't matter how long the message is, as long as it length can be represented in 4 bytes I can send it and the encrypted header should be 44 charecters long!")
