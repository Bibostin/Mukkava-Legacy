"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    TCP Stack - for sending mukkava aplication data, and text chat securely.
    
    UDP Stack - for sending VOIP data securely.
        TBR
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import socket
import threading
import mukkava_encryption


def socket_send(clientsocket, encryption, data):  # Send supplied data down supplied socket encrypting with supplied encryption method
    data = encryption.encrypt(data)
    header = encryption.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
    clientsocket.send(header + data)
    #except: TypeError:
    #ConnectionResetError:


def socket_recieve(clientsocket, encryption):  # Recieve data from supplied socket decrypting with supplied encryption method
    message_length = int(encryption.decrypt(clientsocket.recv(encryption.encrypted_hsize)))
    return encryption.decrypt(clientsocket.recv(message_length))



class TCPStack:  # IPv4 TCP Socket stack for receiving text and command packets
    def __init__(self, port, symetricphrase, username):
        self.sockets_info = {"inbound_sockets": {}, "outbound_sockets": {}}
        self.port = port
        self.username = username
        self.symetric = mukkava_encryption.Symetric(symetricphrase)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostbyname(socket.gethostname()), self.port))

    def outbound_socket_handler(self, address):  # A handler for generating OUTBOUND  (client -> server) socket data streams
        outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        outbound_socket.settimeout(3)  # set the maximum ttl for a socket read, write or connect operation.
        try:
            print(f"\<:connecting outbound_socket on {address}:{self.port}")
            outbound_socket.connect((address, self.port))  # connect the supplied address
        except TimeoutError:
            print(f"\n<:failed to connect to {address}:{self.port} closing outbound socket")
            outbound_socket.close()
            return


        if address not in self.sockets_info["inbound_sockets"].values():  # Check if we have an existing inbound socket key for this given adddress, if we don't we need to setup asymetric encryption
            self.sockets_info["outbound_sockets"][outbound_socket] = {}  # setup an dictionary we can append information on the specific client to.
            self.sockets_info["outbound_sockets"][outbound_socket]["address"] = address

            asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance
            asymetric_instance.setup(socket_recieve(outbound_socket, self.symetric), socket_recieve(outbound_socket, self.symetric))
            socket_send(outbound_socket, self.symetric, asymetric_instance.public_encryption_key_bytes)
            socket_send(outbound_socket, self.symetric, asymetric_instance.public_verify_key_bytes)
            self.sockets_info["outbound_sockets"][outbound_socket]["encryption"] = asymetric_instance
        else:
            self.sockets_info["outbound_sockets"][outbound_socket]["encryption"] = self.sockets_info["inbound_sockets"][address]

    def inbound_socket_handler(self):  # A handler for generating INBOUND  (server -> client) socket data streams
        while True:
            inbound_socket, address = self.server_socket.accept()
            address = address[0]  # strip client side port from the address as we dont need it
            print(f"\n<:recieving inbound socket connection from {address}")

            if address not in self.sockets_info["outbound_sockets"]:  # check if we have an existing outbound socket key for this given address, if we don't we need to setup our own client connection AND asymetric encryption
                self.sockets_info["inbound_sockets"][inbound_socket] = {}  # setup a dictionary we can append information on the specific client to tied to the socket object.
                self.sockets_info["inbound_sockets"][inbound_socket]["address"] = address

                asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance for this specific pair of quad pair of sockets
                socket_send(inbound_socket, self.symetric, asymetric_instance.public_encryption_key_bytes)
                socket_send(inbound_socket, self.symetric, asymetric_instance.public_verify_key_bytes)
                asymetric_instance.setup(socket_recieve(inbound_socket, self.symetric), socket_recieve(inbound_socket, self.symetric))

                self.sockets_info["inbound_sockets"][inbound_socket]["encryption"] = asymetric_instance
                self.outbound_socket_handler(address)  # if address isn't in self.sockets_info["outbound_sockets] we do not have a client going to the opposing server and must create one.
                print(f"\n<:Starting own outbound socket instance to {address} ")
            else:
                self.sockets_info["inbound_sockets"][inbound_socket]["encryption"] = self.sockets_info["outbound_sockets"][address]["asymetric"]

    def inbound_socket_processor(self, data):
        if self.sockets_info["inbound_sockets"]:
            if data:
                data = self.username + ":" + data
            for socket in self.sockets_info["inbound_sockets"]:
                socket_send(socket, self.sockets_info[socket]["encryption"], data)
        else: print("<:currently not connected to any other clients. ")

    def outbound_socket_processor(self):  # TODO: How do we know when a socket has data? do we simply keep polling or do we use select???
        while True:
            for socket in self.sockets_info["outbound_sockets"]:
                data = socket_recieve(socket, self.sockets_info[socket]["encryption"])
                if data:
                    print(f"<:{self.sockets_info[socket]['address']}:{data}")
        pass

    def start(self, inital_address=None):
        self.server_socket.listen(5)
        print(f"\n<:TCP server started on {socket.gethostbyname(socket.gethostname())}:{self.port} waiting for new connections")
        inbound_socket_handler_thread = threading.Thread(target=self.inbound_socket_handler)  # you call the function name NOT AN INSTANCE OF THE FUNCTION such as func()
        outbound_socket_processor_thread = threading.Thread(target=self.outbound_socket_processor)
        #inbound_socket_handler_thread.daemon = True
        #outbound_socket_processor_thread.daemon = True
        inbound_socket_handler_thread.start()
        outbound_socket_processor_thread.start()
        if inital_address:
            self.outbound_socket_handler(inital_address)
        while True:
            usermsg = input("Chat:> ")
            self.inbound_socket_processor(usermsg)

class UDPStack:
    pass