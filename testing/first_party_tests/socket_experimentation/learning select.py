'''Select expects any object that calles it to have a fileno() function that can return a kernel file descriptor, sockets implement this properly, however as we are using
our own, packed socket class we need to replicate this behaviour to get them to play nicely with the select and selector modules.

as written in selects documentation:
This is a straightforward interface to the Unix select() system call. The first three arguments are iterables of ‘waitable objects’: either integers representing file descriptors or objects with a parameterless method named fileno() returning such an integer:
    rlist: wait until ready for reading
    wlist: wait until ready for writing
    xlist: wait for an “exceptional condition” (see the manual page for what your system considers such a condition)

'''
import socket
import select
import mukkava_encryption

class PackedSocket:  # A class that takes a socket object, and packages addressing information and (eventually) a asymetric encryption stack into it
    def __init__(self, socket_object, symetric_encryption_object):
        self.socket = socket_object
        self.local_address = socket_object.getsockname()[0]
        self.peer_address = socket_object.getpeername()[0]
        self.encryption = symetric_encryption_object

    def send_data(self, data):  # Send supplied data down a packed socket with its current encryption scheme
        data = self.encryption.encrypt(data)
        header = self.encryption.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
        self.socket.send(header + data)

    def recieve_data(self):  # Recieve data from supplied packed socket with its current encryption scheme
        message_length = self.socket.recv(self.encryption.encrypted_hsize)
        message_length = int(self.encryption.decrypt(message_length))
        data = self.socket.recv(message_length)
        return self.encryption.decrypt(data)

# Its literally as simple as doing this! we just have to map the scoket fileno function to one in the packed socket.


