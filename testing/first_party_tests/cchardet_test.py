'''
Chardet is a library for detecting the encoding type of data, I was originally going to use it to differentiate between encrypted data and utf-8
data however the use case evaporated and even then, isinstance(data, bytes / nacl.utils.EncryptedMessage) can be used for this purpose.
'''

import cchardet
import mukkava_encryption
import mukkava_audio

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
test1 = b"test"
test2 = "test".encode()

print(cchardet.detect(test1))
print(cchardet.detect(test2))

audioinput = mukkava_audio.AudioInput()
audioinput.instream.start()
while True:
    data = audioinput.data_buffer.get()
    print(data)
    print(cchardet.detect(data))

#if cchardet.detect(data)[encoding]