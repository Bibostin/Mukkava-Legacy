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
import json
import queue
import select
import ipaddress
import socket
import threading
import mukkava_encryption
import mukkava_audio

audio_in = mukkava_audio.AudioInput()  # Set up our audio input (microphone-> peer) encoder and stream handler
audio_out = mukkava_audio.AudioOutput()  # Set up our audio output (peer -> speaker) decoder and stream handler


class PackedSocket:  # A class that takes a socket object, and packages information relating to its operation as part of NetStack.
    def __init__(self, socket_object, encryption_object):
        self.socket = socket_object  # pack the supplied socket
        self.encryption = encryption_object  # for a tcp socket this will be a symetric object initally, then a asymetric after handshake.
        self.local_address = socket_object.getsockname()[0]  # store local address of the socket in a easer to reach location
        self.peer_address = socket_object.getpeername()[0]  # if the socket is a tcp socket, we allready have the address when we set it up, can just fetch it.
        self.audio_out_buffer_instance = audio_out.add_queue()
        self.operation_flag = False  # A flag for stopping race conditions that create issues between the TCP handlers and active TCP processors, set to True when a socket is ready for processing.


    def fileno(self):  # Select and Selector both require this behaviour from objects to function properly, look at learning_select.py for reasoning.
        return self.socket.fileno()

    def send_data(self, data, message_type):  # Send supplied data down a packed socket with its current encryption scheme
        data = self.encryption.encrypt(data)
        message_type = self.encryption.encrypt(message_type)
        header = self.encryption.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
        self.socket.send(header + message_type + data)

    def recieve_data(self):  # Recieve data from supplied packed socket with its current encryption scheme
        message_length = self.socket.recv(self.encryption.encrypted_hsize)
        message_length = int(self.encryption.decrypt(message_length))
        message_type = self.socket.recv(self.encryption.encrypted_hsize)
        message_type = self.encryption.decrypt(message_type)
        data = self.socket.recv(message_length)
        return self.encryption.decrypt(data), message_type


class NetStack:  # IPv4 TCP Socket stack for receiving text and command packets
    def __init__(self, port, symetricphrase, username, initial_address=None):
        self.sockets_info = {"inbound_sockets": [], "outbound_sockets": []}
        self.port = port  # port supplied in main.py for the server socket to listen on
        self.symetric = mukkava_encryption.Symetric(symetricphrase)  # A symetric object used for inital handshake
        self.username = username  # name supplied in main.py, appended to text messages as part of the message string
        self.text_buffer = queue.SimpleQueue()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The TCP Stacks "bound" socket, accepts connections from peer outbound sockets and sends out its own outbound sockets to the other clients server_socket if required
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Force the OS of the system to allow the reuse of the port via socket binding without a delay
        self.server_socket.bind((socket.gethostbyname(socket.gethostname()), self.port))
        self.server_socket.listen(10)
        print(f"<:MAIN:TCP server started on {socket.gethostbyname(socket.gethostname())}:{self.port} waiting for new connections")

        inbound_socket_handler_thread = threading.Thread(target=self.inbound_socket_handler)  # you call the function name NOT AN INSTANCE OF THE FUNCTION such as func()
        inbound_processor_thread = threading.Thread(target=self.inbound_socket_processor)
        outbound_processor_thread = threading.Thread(target=self.outbound_socket_proccesor)
        inbound_socket_handler_thread.daemon = True
        inbound_processor_thread.daemon = True
        outbound_processor_thread.daemon = True
        inbound_socket_handler_thread.start()
        print(f"<:MAIN:TCP Inbound handler thread started")
        inbound_processor_thread.start()
        print(f"<:MAIN:TCP Inbound voice processor thread started")
        outbound_processor_thread.start()
        print(f"<:MAIN:TCP Outbound processor thread started")
        if initial_address: self.tcp_outbound_socket_handler(initial_address, propagate_peers=True)  # if an initial address was supplied, spin up an outbound socket connecting to that address
        while True: self.text_buffer.put(input())

    def inbound_socket_handler(self):  # A handler for generating INBOUND  (server -> client) socket data streams
        while True:
            inbound_socket = PackedSocket(self.server_socket.accept()[0], self.symetric)
            print(f"<:INh:Connection to local server from {inbound_socket.peer_address}")
            audio_in.instream.start()

            if not (existing_socket := self.check_for_existing_socket("outbound_sockets", inbound_socket.peer_address)):
                print(f"<:INh:No asymetric encryption object found for {inbound_socket.peer_address}, creating.")
                asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance for this specific  quad pair of sockets
                inbound_socket.send_data(asymetric_instance.public_encryption_key_bytes, "HDSK")
                inbound_socket.send_data(asymetric_instance.public_verify_key_bytes, "HDSK")
                asymetric_instance.setup(inbound_socket.recieve_data()[0], inbound_socket.recieve_data()[0])
                inbound_socket.encryption = asymetric_instance
                self.sockets_info['inbound_sockets'].append(inbound_socket)  # unlike the outbound_handler, we cant handle for appending the packedsocket object to sock_info as a statement after the if else check for an existing socket as the inbound check calls a instance of outbound handler that NEEDS to know about this socket
                self.tcp_outbound_socket_handler(inbound_socket.peer_address)  # if address isn't in self.sockets_info["outbound_sockets] we do not have a client going to the opposing server and must create one.
            else:
                inbound_socket.encryption = existing_socket.encryption
                print(f"<:INh:Found asymetric encryption object for {inbound_socket.peer_address}")
                self.sockets_info['inbound_sockets'].append(inbound_socket)  # this should only happen when a socket is ready to be used by the processor

            address_list = self.return_peer_address_list(inbound_socket.peer_address)
            inbound_socket.send_data(address_list, "HDSK")
            print(f"<:INh:Sent current peer address list to {inbound_socket.peer_address}")
            inbound_socket.operation_flag = True

    def tcp_outbound_socket_handler(self, address, propagate_peers=False):  # A handler for generating OUTBOUND  (client -> server) socket data streams
        outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        outbound_socket.settimeout(120)  # set the maximum ttl for a socket read, write or connect operation. #TODO change this lower once working
        outbound_socket.connect((address, self.port))  # connect to the supplied address
        audio_out.outstream.start()
        print(f"<:OUTh:Connected to remote server at {address}:{self.port}")
        outbound_socket = PackedSocket(outbound_socket, self.symetric)  # With a outbound socket, we cant generate our packed socket untill the connection has been established

        if not (existing_socket := self.check_for_existing_socket("inbound_sockets", outbound_socket.peer_address)):  # Check if we have an existing inbound socket key for this given adddress, if we dont this is the first step of the handshake)and we need to setup asymetric encryption
            print(f"<:OUTh:No asymetric encryption object found for {outbound_socket.peer_address}, creating.")
            asymetric_instance = mukkava_encryption.Asymetric()  # setup a new asymetric instance
            asymetric_instance.setup(outbound_socket.recieve_data()[0], outbound_socket.recieve_data()[0])  # Outbound clients allways recieve npkb and npvb first, then send after
            outbound_socket.send_data(asymetric_instance.public_encryption_key_bytes, "HDSK")
            outbound_socket.send_data(asymetric_instance.public_verify_key_bytes, "HDSK")
            outbound_socket.encryption = asymetric_instance
        else:
            print(f"<:OUTh:found asymetric encryption object for {outbound_socket.peer_address}")  # we allready have a inbound connection to our server from this address, use the same encryption object as that conenction.
            outbound_socket.encryption = existing_socket.encryption

        self.sockets_info['outbound_sockets'].append(outbound_socket)  # Socket setup is complete, but not ready for processor operation just yet
        peer_address_list = json.loads(outbound_socket.recieve_data()[0])

        if propagate_peers:  # If propagate_peers is true, this our inital outbound connection to an inital peer, so we need to act on the recieved peer address list
            print(f"<:OUTh:Recieved current peer address list from {outbound_socket.peer_address}, propagating now.")
            if peer_address_list[0] == "no-other-peers": print(f"<:OUTh:No other peers from {outbound_socket.peer_address}")  # if
            else:
                if outbound_socket.local_address in peer_address_list:  # double check that the remote server hasn't sent us our own local address
                    try: peer_address_list.remove(outbound_socket.local_address)
                    except ValueError: pass  # The server did its job correctly and the address wasn't present.
                print(f"<:OUTh:New peer/s recieved: {peer_address_list}")
                for peer_address in peer_address_list:
                    try:
                        ipaddress.ip_address(peer_address)
                        self.tcp_outbound_socket_handler(peer_address)  # initiate a non peer propagating outbound handler for each supplied address, connecting us to all the peers in the voip session.
                    except ValueError: print(f"<:OUT: Bad address \"{peer_address}\" in address list, malicious peer?")

        else: print(f"<:OUTh:Recieved current peer address list from {outbound_socket.peer_address}, but not propagating.")
        outbound_socket.operation_flag = True # The socket is ready for operation.

    def inbound_socket_processor(self):  # A function for taking input text data and sending it to all peers in the session.
        while True:
            if self.sockets_info["inbound_sockets"]:  # if inbound sockets are present,
                if not audio_in.data_buffer.empty(): voice_data = audio_in.data_buffer.get()
                else: voice_data = False

                if not self.text_buffer.empty(): text_data =  self.username+": " + self.text_buffer.get()  # append username to the text data
                else: text_data = False

                _, writable_sockets, _ = select.select([], self.sockets_info["inbound_sockets"], [])
                for inbound_socket in writable_sockets:
                    if inbound_socket.operation_flag:  # if the handler has finished setting up the socket (and its not still in handshake)
                        if voice_data: inbound_socket.send_data(voice_data, "VOIP")  # if we have voice data, send it
                        if text_data: inbound_socket.send_data(text_data, "TEXT")  # if we have text data, send it


    def outbound_socket_proccesor(self):  # consider switching out select, epoll, kqueues, SELECTOR?
        while True:
            if self.sockets_info["outbound_sockets"]: # if there are
                readable_sockets, _, errored_sockets = select.select(self.sockets_info["outbound_sockets"], [], self.sockets_info["outbound_sockets"], 5)
                for outbound_socket in readable_sockets:
                    if outbound_socket.operation_flag:
                        data, message_type = outbound_socket.recieve_data()
                        if message_type == "TEXT": print(f"<:OUTp:{outbound_socket.peer_address}:{data}")
                        elif message_type == "VOIP":
                            outbound_socket.audio_out_buffer_instance.put(data)
                            print("recieved voice data")
                        else: print(f"<:OUT recieved a message from {outbound_socket.peer_address} with bad message type tagging")
                audio_out.process_input()

                for outbound_socket in errored_sockets:
                    outbound_socket.socket.close()
                    print(f"<:OUTp: outbound socket to {outbound_socket.peer_address} encountered an error, closing connection.")

    def check_for_existing_socket(self, inbound_or_outbound, peer_address):  # A Simple function for evaluating whether any existing sockets are connected to or originate from the specified address
        for packed_socket in self.sockets_info[inbound_or_outbound]:  # for all the packed sockets in whichever socket type dictionary was specified
            if peer_address == packed_socket.peer_address:  # check is equal
                return packed_socket  # return the socket that has the address
        return False  # no socket with that address was present

    def return_peer_address_list(self, receiving_peer_address):  # A simple function for generating a list of peer addresses to send to a new peer, exluding the peers own address
        address_list = []
        if len(self.sockets_info["inbound_sockets"]) > 1:  # as we only call rpal after the peer is setup in sock_info, if theres only one entry, its the peer we are calling rpal for.
            for packed_socket in self.sockets_info["inbound_sockets"]:
                address_list.append(packed_socket.peer_address)
            address_list.remove(receiving_peer_address)  # Ensure the address of the peer is not in the sent list (this is checked client side too)
        else: address_list.append("no-other-peers")  # The peer is currently our only connection
        return json.dumps(address_list)  # serialise the list in  quick and secure format for interpritation by the other client.