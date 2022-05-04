"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    TCP Stack - for sending mukkava aplication data, and text chat securely.
        produce outbound sockets to fetch text data from other mukkava client server sockets
        produce inbound sockets from own server socket to send text data to connecting outbound sockets
        maintain synchronisation between inbound and outbound sockets in terms of expected encryption / total amount

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
to be handled by outbound
    ConnectionRefusedError:
    timeouterror
    connection terminated error
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import socket
import threading
import mukkava_encryption
import json


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


class TCPStack:  # IPv4 TCP Socket stack for receiving text and command packets
    def __init__(self, listen_port, connect_port, symetricphrase, username, initial_address=None):
        self.sockets_info = {"inbound_sockets": [], "outbound_sockets": []}
        self.listen_port = listen_port  # port supplied in main.py for the server socket to listen on
        self.connect_port = connect_port  # port supplied in main.py for outbound sockets to connect via
        self.symetric = mukkava_encryption.Symetric(symetricphrase)  # A symetric object used for inital handshake TODO: consider moving this out so udp can use it too
        self.username = username  # name supplied in main.py, appended to text messages as part of the message string

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The TCP Stacks "bound" socket, accepts connections from peer outbound sockets and sends out its own outbound sockets to the other clients server_socket if required
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Force the OS of the system to allow the reuse of the port via socket binding without a delay
        self.server_socket.bind((socket.gethostbyname(socket.gethostname()), self.listen_port))
        self.server_socket.listen(5)
        print(f"<:TCP server started on {socket.gethostbyname(socket.gethostname())}:{self.listen_port} waiting for new connections")

        inbound_socket_handler_thread = threading.Thread(target=self.inbound_socket_handler)  # you call the function name NOT AN INSTANCE OF THE FUNCTION such as func()
        inbound_socket_handler_thread.daemon = True
        inbound_socket_handler_thread.start()

        if initial_address:
            self.outbound_socket_handler(initial_address, propagate_peers=True)  # if an initial address was supplied, spin up an outbound socket connecting to that address
        while True:
            usermsg = input("Chat:> ")

    def inbound_socket_handler(self):  # A handler for generating INBOUND  (server -> client) socket data streams
        while True:
            inbound_socket = PackedSocket(self.server_socket.accept()[0], self.symetric)
            print(f"<:IN:Connection to local server from {inbound_socket.peer_address}")

            if not (existing_socket := self.check_for_existing_socket("outbound_sockets", inbound_socket.peer_address)):
                print(f"<:IN:No asymetric encryption object found for {inbound_socket.peer_address}, creating.")
                asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance for this specific  quad pair of sockets
                inbound_socket.send_data(asymetric_instance.public_encryption_key_bytes)
                inbound_socket.send_data(asymetric_instance.public_verify_key_bytes)
                asymetric_instance.setup(inbound_socket.recieve_data(), inbound_socket.recieve_data())
                inbound_socket.encryption = asymetric_instance
                self.sockets_info['inbound_sockets'].append(inbound_socket)  #unlike the outbound_handler, we cant handle for appending the packedsocket object to sock_info as a statement after the if else check for an existing socket as the inbound check calls a instance of outbound handler that NEEDS to know about this socket
                self.outbound_socket_handler(inbound_socket.peer_address)  # if address isn't in self.sockets_info["outbound_sockets] we do not have a client going to the opposing server and must create one.
            else:
                print(f"<:IN:Found asymetric encryption object for {inbound_socket.peer_address}")
                inbound_socket.encryption = existing_socket.encryption
                self.sockets_info['inbound_sockets'].append(inbound_socket) #this should only happen when a socket is ready to be used by the processor

            address_list = self.return_peer_address_list(inbound_socket.peer_address)
            print(f"<:IN:Sent current peer address list to {inbound_socket.peer_address}")
            inbound_socket.send_data(address_list)

    def outbound_socket_handler(self, address, propagate_peers=False):  # A handler for generating OUTBOUND  (client -> server) socket data streams
        outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        outbound_socket.settimeout(120)  # set the maximum ttl for a socket read, write or connect operation. #TODO change this lower once working
        outbound_socket.connect((address, self.connect_port))  # connect to the supplied address
        print(f"<:OUT:Connected to remote server at {address}:{self.connect_port}")
        outbound_socket = PackedSocket(outbound_socket, self.symetric) #With a outbound socket, we cant generate our packed socket untill the connection has been established

        if not (existing_socket := self.check_for_existing_socket("inbound_sockets", outbound_socket.peer_address)):  # Check if we have an existing inbound socket key for this given adddress, if we dont this is the first step of the handshake)and we need to setup asymetric encryption
            print(f"<:OUT:No asymetric encryption object found for {outbound_socket.peer_address}, creating.")
            asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance
            asymetric_instance.setup(outbound_socket.recieve_data(), outbound_socket.recieve_data())
            outbound_socket.send_data(asymetric_instance.public_encryption_key_bytes)
            outbound_socket.send_data(asymetric_instance.public_verify_key_bytes)
            outbound_socket.encryption = asymetric_instance
        else:
            print(f"<:OUT:found asymetric encryption object for {outbound_socket.peer_address}")
            outbound_socket.encryption = existing_socket.encryption

        self.sockets_info['outbound_sockets'].append(outbound_socket)  #this should only happen when a socket is ready to be used by the processor
        peer_address_list = json.loads(outbound_socket.recieve_data())
        print(f"<:OUT:Recieved current peer address list from {outbound_socket.peer_address}")

        if propagate_peers:  # If propagate_peers is true, this our inital outbound connection to an inital peer, so we need to act on the peer address list
            if peer_address_list[0] == "no-other-peers": print(f"<:OUT:No other peers from {outbound_socket.peer_address}") #if
            else:
                if outbound_socket.local_address in peer_address_list:  # double check that the remote server hasn't sent us our own local address
                    try:peer_address_list.remove(outbound_socket.local_address)
                    except ValueError: pass  # The server did its job correctly and the address wasn't present.
                for peer_address in peer_address_list:
                    self.outbound_socket_handler(peer_address) #initiate a non peer propagating outbound handler for each supplied address, connecting us to all the peers in the voip session.



    def check_for_existing_socket(self, inbound_or_outbound, peer_address):  # A Simple function for evaluating whether any existing sockets are connected to or originate from the specified address
        for packed_socket in self.sockets_info[inbound_or_outbound]:  # for all the packed sockets in whichever socket type dictionary was specified
            if peer_address == packed_socket.peer_address:  # check is equal
                return packed_socket  # return the socket that has the address
        return False  # no socket with that address was present

    def return_peer_address_list(self, peer_address):  # A simple function for generating a list of peer addresses to send to a new peer, exluding the peers own address
        address_list = []
        if len(self.sockets_info["inbound_sockets"]) > 1:  # as we only call rpal after the peer is setup in sock_info, if theres only one entry, its the peer we are calling rpal for.
            for packed_socket in self.sockets_info["inbound_sockets"]:
                address_list.append(packed_socket.peer_address)
            address_list.remove(peer_address)  # Ensure the address of the peer is not in the sent list (this is checked client side too)
        else: address_list.append("no-other-peers")  # The peer is currently our only connection
        return json.dumps(address_list)  #serialise the list in  quick and secure format for interpritation by the other client.
