import cchardet
import mukkava_encryption

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
test1 = b"test"
test2 = "test".encode()
test3 = symetric.encrypt(test1)

print(type(test3))
print(cchardet.detect(test1))
print(cchardet.detect(test2))
print(cchardet.detect(test3))

nacl.utils.EncryptedMessage