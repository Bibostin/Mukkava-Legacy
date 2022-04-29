"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    TCP Stack - for sending mukkava aplication data, and text chat securely.
        produce outbound sockets to fetch text data from other mukkava client server sockets
        produce inbound sockets from own server socket to send text data to connecting outbound sockets
        maintain synchronisation between inbound and outbound sockets in terms of expected encryption / total amount
    
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


def socket_recieve(clientsocket, encryption):  # Recieve data from supplied socket decrypting with supplied encryption method
    message_length = int(encryption.decrypt(clientsocket.recv(encryption.encrypted_hsize)))
    return encryption.decrypt(clientsocket.recv(message_length))


class TCPStack:  # IPv4 TCP Socket stack for receiving text and command packets
    def __init__(self, port, symetricphrase, username):
        self.sockets_info = {"inbound_sockets": {}, "outbound_sockets": {}}  # A dictionary, containing keys tied to individual socket objects, which in turn have their address and encryption box tied to that.
        self.port = port  # port supplied in main.py
        self.username = username  # name supplied in main.py, appended to text messages as part of the message string
        self.symetric = mukkava_encryption.Symetric(symetricphrase)  # A symetric object used for inital handshake TODO: consider moving this out so udp can use it too
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #The TCP Stack "bound" socket, accepts connections from inbound sockets and sends out its own outbound sockets to the other clients server_socket if required
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostbyname(socket.gethostname()), self.port))

    #SOCKET HANDLERS
    def inbound_socket_handler(self):  # A handler for generating INBOUND  (server -> client) socket data streams
        while True:
            inbound_socket, address = self.server_socket.accept()
            address = address[0]  # strip client side port from the address as we dont need it
            print(f"<:connection from {address}")

            if not (existing_socket := self.check_for_existing_socket("outbound_sockets", address)):  # check if we have an existing outbound socket key for this given address, if we do, return it and bind its asymetric instance to our inbound socket. if we don't we need to setup our own client connection AND asymetric encryption
                self.sockets_info["inbound_sockets"][inbound_socket] = {}  # setup a dictionary we can append information on the specific client to tied to the socket object.
                self.sockets_info["inbound_sockets"][inbound_socket]["address"] = address

                asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance for this specific  quad pair of sockets
                socket_send(inbound_socket, self.symetric, asymetric_instance.public_encryption_key_bytes)
                socket_send(inbound_socket, self.symetric, asymetric_instance.public_verify_key_bytes)
                asymetric_instance.setup(socket_recieve(inbound_socket, self.symetric), socket_recieve(inbound_socket, self.symetric))

                self.sockets_info["inbound_sockets"][inbound_socket]["encryption"] = asymetric_instance
                self.outbound_socket_handler(address)  # if address isn't in self.sockets_info["outbound_sockets] we do not have a client going to the opposing server and must create one.
            else:
                self.sockets_info["inbound_sockets"][inbound_socket]["encryption"] = existing_socket["encryption"]

    def outbound_socket_handler(self, address):  # A handler for generating OUTBOUND  (client -> server) socket data streams
        outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        outbound_socket.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation. #TODO change this lower once working
        try:
            print(f"<:connecting to {address}:{self.port}")
            outbound_socket.connect((address, self.port))  # connect the supplied address
        except TimeoutError:
            print(f"<:failed to connect to {address}:{self.port}")
            outbound_socket.close()
            return
        except OSError:
            print(f"<:no route availible to {address}:{self.port}")
            outbound_socket.close()
            return

        if not (existing_socket := self.check_for_existing_socket("inbound_sockets", address)):  # Check if we have an existing inbound socket key for this given adddress, if we don't we need to setup asymetric encryption
            self.sockets_info["outbound_sockets"][outbound_socket] = {}  # setup an dictionary we can append information on the specific client to.
            self.sockets_info["outbound_sockets"][outbound_socket]["address"] = address

            asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance
            asymetric_instance.setup(socket_recieve(outbound_socket, self.symetric), socket_recieve(outbound_socket, self.symetric))
            socket_send(outbound_socket, self.symetric, asymetric_instance.public_encryption_key_bytes)
            socket_send(outbound_socket, self.symetric, asymetric_instance.public_verify_key_bytes)
            self.sockets_info["outbound_sockets"][outbound_socket]["encryption"] = asymetric_instance
        else:
            self.sockets_info["outbound_sockets"][outbound_socket]["encryption"] = existing_socket["encryption"]



    #PROCESSOR FUNCTIONS
    def inbound_socket_processor(self, data):
        if self.sockets_info["inbound_sockets"]:
            if data:
                data = self.username + ": " + data
            for socket in self.sockets_info["inbound_sockets"]:
                socket_send(socket, self.sockets_info[socket]["encryption"], data)
        else: print("<:currently not connected to any other clients. ")

    def outbound_socket_processor(self):  # TODO: How do we know when a socket has data? do we simply keep polling or do we use select???
        while True:
            if self.sockets_info["outbound_sockets"]:
                for socket in self.sockets_info["outbound_sockets"]:
                    data = socket_recieve(socket, self.sockets_info[socket]["encryption"])
                    if data: print(f"<:{self.sockets_info[socket]['address']}:{data}")


    #UTILITY FUNCTIONS
    def check_for_existing_socket(self, inbound_or_outbound, address):  # A Simple function for evaluating whether any existing sockets are connected to or originate from the specified address
        for sock in self.sockets_info[inbound_or_outbound]:  # for all of the socket dictionaries in whichever socket type dictionary was specified
            if address in self.sockets_info[inbound_or_outbound][sock].values():  #check if the address is present (aka we have an existing socket with that address)
                return self.sockets_info[inbound_or_outbound][sock]  # return the socket that has the address TODO: consider straight up passing the encryption object through to save on eff
        return False  #no socket with that address was present


    def start_stack(self, inital_address=None): # Start operation of the tcp stack.
        self.server_socket.listen(5)
        print(f"<:TCP server started on {socket.gethostbyname(socket.gethostname())}:{self.port} waiting for new connections")
        inbound_socket_handler_thread = threading.Thread(target=self.inbound_socket_handler)  # you call the function name NOT AN INSTANCE OF THE FUNCTION such as func()
        outbound_socket_processor_thread = threading.Thread(target=self.outbound_socket_processor)
        inbound_socket_handler_thread.start()
        outbound_socket_processor_thread.start()
        if inital_address:  # if an inital address was supplied, spin up an outbound socket connecting to that address
            self.outbound_socket_handler(inital_address)
        while True:
            usermsg = input("Chat:> ")
            self.inbound_socket_processor(usermsg)




class UDPStack:
    pass