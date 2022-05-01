#Packing sockets

import socket
import mukkava_encryption

class PackedSocket:
    def __init__(self, socketobj):
        self.socket = socketobj
        self.address = socketobj.getpeername()[0]
        self.encryption = mukkava_encryption.Asymetric()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 9997))
s.listen(5) #listen accepts a number specifying queue length
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(("127.0.0.1", 9997))
clientsock = PackedSocket(s.accept()[0])

print(clientsock.socket)
print(clientsock.address)
print(clientsock.encryption)








