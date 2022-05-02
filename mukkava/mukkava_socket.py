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


class PackedSocket:  # A class that takes a socket object, and packages addressing information and aa asymetric encryption stack into it
    def __init__(self, socket_object, symetric_encryption_object):
        self.socket = socket_object
        self.local_address = socket_object.getsockname()[0]
        self.peer_address = socket_object.getpeername()[0]
        self.encryption = symetric_encryption_object

    def send_data(self, data):  # Send supplied data down supplied packed socket socket
        data = self.encryption.encrypt(data)
        header = self.encryption.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
        self.socket.send(header + data)

    def recieve_data(self):  # Recieve data from supplied packed socket
        message_length = self.socket.recv(self.encryption.encrypted_hsize)
        message_length = int(self.encryption.decrypt(message_length))
        data = self.socket.recv(message_length)
        return self.encryption.decrypt(data)


class TCPStack:  # IPv4 TCP Socket stack for receiving text and command packets
    def __init__(self, port, symetricphrase, username, initial_address=None):
        self.sockets_info = {"inbound_sockets": [], "outbound_sockets": []}
        self.port = port  # port supplied in main.py for the server socket to listen on / outbound sockets to connect via
        self.symetric = mukkava_encryption.Symetric(symetricphrase)  # A symetric object used for inital handshake TODO: consider moving this out so udp can use it too
        self.username = username  # name supplied in main.py, appended to text messages as part of the message string

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The TCP Stack "bound" socket, accepts connections from inbound sockets and sends out its own outbound sockets to the other clients server_socket if required
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Force the OS of the system to allow the reuse of the port via socket binding without a delay
        self.server_socket.bind((socket.gethostbyname(socket.gethostname()), self.port))
        self.server_socket.listen(5)
        print(f"<:TCP server started on {socket.gethostbyname(socket.gethostname())}:{self.port} waiting for new connections")

        inbound_socket_handler_thread = threading.Thread(target=self.inbound_socket_handler)  # you call the function name NOT AN INSTANCE OF THE FUNCTION such as func()
        inbound_socket_handler_thread.daemon = True
        inbound_socket_handler_thread.start()

        if initial_address:
            self.outbound_socket_handler(initial_address)  # if an initial address was supplied, spin up an outbound socket connecting to that address
        while True:
            usermsg = input("Chat:> ")

    def inbound_socket_handler(self):  # A handler for generating INBOUND  (server -> client) socket data streams
        while True:
            inbound_socket = PackedSocket(self.server_socket.accept()[0], self.symetric)
            print(f"<:recieved connection to server from {inbound_socket.peer_address}")

            if not (existing_socket := self.check_for_existing_socket("outbound_sockets", inbound_socket.peer_address)):
                asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance for this specific  quad pair of sockets
                inbound_socket.send_data(asymetric_instance.public_encryption_key_bytes)
                inbound_socket.send_data(asymetric_instance.public_verify_key_bytes)
                asymetric_instance.setup(inbound_socket.recieve_data(), inbound_socket.recieve_data())
                inbound_socket.encryption = asymetric_instance
                self.outbound_socket_handler(inbound_socket.peer_address)  # if address isn't in self.sockets_info["outbound_sockets] we do not have a client going to the opposing server and must create one.
            else:
                inbound_socket.encryption = existing_socket.encryption
            self.sockets_info["inbound_sockets"].append(inbound_socket)

    def outbound_socket_handler(self, address):  # A handler for generating OUTBOUND  (client -> server) socket data streams
        outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        outbound_socket.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation. #TODO change this lower once working
        outbound_socket.connect((address, self.port))  # connect to the supplied address
        print(f"<:connected to server at {address}:{self.port}")
        outbound_socket = PackedSocket(outbound_socket, self.symetric) #With a outbound socket, we cant generate our packed socket untill the connection has been established

        if not (existing_socket := self.check_for_existing_socket("inbound_sockets", address)):  # Check if we have an existing inbound socket key for this given adddress, if we dont this is the first step of the handshake)and we need to setup asymetric encryption
            asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance
            asymetric_instance.setup(outbound_socket.recieve_data(), outbound_socket.recieve_data())
            outbound_socket.send_data(asymetric_instance.public_encryption_key_bytes)
            outbound_socket.send_data(asymetric_instance.public_verify_key_bytes)
            outbound_socket.encryption = asymetric_instance
        else:
            print(f"<:found existing encryption object for {address}")
            outbound_socket.encryption = existing_socket.encryption
        self.sockets_info["outbound_sockets"].append(outbound_socket)

    def check_for_existing_socket(self, inbound_or_outbound, address):  # A Simple function for evaluating whether any existing sockets are connected to or originate from the specified address
        for packed_socket in self.sockets_info[inbound_or_outbound]:  # for all the packed sockets in whichever socket type dictionary was specified
            if address == packed_socket.peer_address:  # check is equal
                return packed_socket  # return the socket that has the address TODO: consider straight up passing the encryption object through to save on eff
        return False  # no socket with that address was present
