# utf-8 is better then ascii
# toml used initially but switched to json

# Library setup
import socket  # tcp / udp sockets used for data transfer between client and server
import threading  # Used for instancing functions (client_handlers, message_handlers.)
import toml  # Provides server config in a simple format. TODO: potentially replace with JSON
import json  # Serialising control messages
import logging  # Logging server operation / streaming to stdout
import datetime  # used for appending exact date / start time to to log filenames

# Main vars
config = toml.load('server_config.toml')  # Dictionary pulled from server_config.toml
config_json = json.dumps('server_config.json')  # dictionary pulled from server config.json
voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4 UDP Socket for transmitting opus voice packets
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 TCP Socket for text and command packets
serveraddress = socket.gethostbyname(socket.gethostname())  # TODO: try fetch ip from config, then default to this
file_semaphore = threading.BoundedSemaphore(1)  # These restrict usage of files by threads to 1 at a time.
client_sockets = []  # TODO: decide if this is necessary or if a better approach can be used
client_addresses = []  # TODO: decide if this is necessary or if a better approach can be used
client_objects = []  # A List used for macromanaging client_Class objects outside of

# Setup file logging
# TODO: add separate stream output to stdout to provide logging output on server terminal.
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:  %(message)s', datefmt='%m-%d %H:%M',
    filename=f'logs/log-{datetime.datetime.now()}', level='DEBUG', )

#Object classes
class ClientClass:
    def __init__(self, nickname, deafened, muted):  # self "represents" the individual object instance of a class
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False


#Method Classes
class Generic:

    # TODO: file presence / perm checks, address input validation
    @staticmethod
    def file_operation(listname, operation, ip):  # Handles the required file IO for the whitelist and blacklist

        if operation == "check":  # check for occurrence of an IP in whitelist or blacklist.
            file_semaphore.acquire()
            input_file = open(f'{listname}.txt', 'r')
            parsed_file = (input_file.read().splitlines())
            if ip in parsed_file:
                input_file.close()
                file_semaphore.release()
                return True
            else:
                input_file.close()
                file_semaphore.release()
                return False

        elif operation == "append":  # append a given IP to the whitelist or blacklist
            if Generic.file_operation(listname, "check", ip) is False:
                file_semaphore.acquire()
                input_file = open(f'{listname}.txt', 'a')
                input_file.write('\n')
                input_file.write(f'{ip}')
                input_file.close()
                file_semaphore.release()
                logging.debug(f'Successfully added {ip} to {listname}.')
            else:
                logging.error(f'attempted to add an already present IP, {ip} to {listname}.')

        elif operation == "remove":  # Remove a given IP from the whitelist or blacklist by checking
            if Generic.file_operation(listname, "check", ip) is True:
                file_semaphore.acquire()
                input_file = open(f'{listname}.txt', 'r')
                parsed_file = input_file.read().splitlines()
                input_file.close()
                parsed_file.remove(ip)
                output_file = open(f'{listname}.txt', 'w+')
                for lines in parsed_file:
                    output_file.write(lines)
                output_file.close()
                file_semaphore.release()
                logging.debug(f'Successfully removed {ip} from {listname}.')
            else:
                logging.error(f'Attempted to remove a non present IP, {ip} from {listname}.')
        else:
            logging.error(f'Invalid use of file_operation function, with params: {listname} {operation} {ip}')

    # TODO: Look into encryption methods, protocols and modules /their speeds. (SRTP? AES-256? TLS 1.3? ChaCha20!)
    @staticmethod
    def encryption():
        pass


class Text:

    @staticmethod
    def unicast(client_socket, message):  # Send a message directly to a specific client (DM, Command feedback, etc.)
        client_socket.send(message.encode('utf-8'))

    @staticmethod
    def broadcast(
            message):  # Broadcast message to all established sockets the server knows (I.E. for public chat messages)
        for client_socket in client_sockets:
            client_socket.send(message.encode('utf-8'))

    # TODO: Add password check
    @staticmethod
    def client_handler():  # Handles collecting inbound clients, and sets them up with a text_message_handler thread
        while True:  # While thread is active, continuously check for new clients, check for presence in whitelist / blacklist, setup encryption, check password, then handoff to a Text.message_handler thread for input message processing.
            client_socket, address = text_server.accept()  # pulls next client in from a fifo buffer of inbound socket requests.
            if config['whitelist'] is True:
                if Generic.file_operation('whitelist', 'check', address) is False:
                    Text.unicast(client_socket, "You are not whitelisted for this server.")
                    client_socket.close()
                    logging.debug(f"Connection attempt from {address}, failed whitelist.")
                    continue

            if Generic.file_operation('blacklist', 'check', address) is True:
                Text.unicast(client_socket, "You are banned from this server.")
                client_socket.close()
                logging.debug(f"Connection attempt from {address}, failed blacklist.")
                continue

            # E2E HANDSHAKE GOES HERE

            # PASSWORD CHECK GOES HERE

            # CLIENT OBJECT /STATE SETUP
            Text.unicast(client_socket, "REQ-CLIENT-STATUS")
            client_socket_return = json.loads(client_socket.recv(4096).decode('utf-8'))
            client_object = ClientClass(client_socket_return.nickname, client_socket_return.deafened,
                                        client_socket_return.muted)
            Text.broadcast(f'{client_object.nickname} connected. {config["greeting_message"]}')
            logging.info(f"client {client_object.nickname} connected from {address}. muted:{client_object.deafened}.")

            client_objects.append(client_object)
            client_sockets.append(client_socket)

            thread = threading.Thread(target=Text.message_handler(client_socket))
            thread.start()

    @staticmethod
    def message_handler(
            client_socket):  # Parse inbound client messages and determines how to distribute it to other clients / additional actions to take
        while True:
            try:
                message = client_socket.recv(4096)
                Text.broadcast(message)
            except:
                index = client_sockets.index(client_socket)
                client_socket.close()
                Text.broadcast(f'{client_objects[index].nickname} has disconnected.')
                logging.debug(
                    f'{client_addresses[index]}  with nickname {client_objects[index].nickname} has disconnected')

                client_sockets.remove(client_socket)
                client_objects.remove((client_objects[index]))
                break

    @staticmethod
    def start():
        try:
            text_server.bind((serveraddress, config['control_port']))
            text_server.listen()
            logging.info(f'TCP Text and control socket bound, listening on port {config["control_port"]}')
            try:
                text_client_handler_thread = threading.Thread(target=Text.client_handler())
                text_client_handler_thread.start()
            except:
                text_server.close()
                logging.error('Failed to start text handler! (PROGRAM ERROR!)')
                exit(1)
        except:
            text_server.close()
            logging.error(
                f'Failed to bind text socket to {config["control_port"]} on {serveraddress}. Check for existing / conflicting processes.')
            exit(1)


class Voip:

    @staticmethod
    def client_handler():
        pass

    @staticmethod
    def message_handler():
        pass

    @staticmethod
    def start():
        try:
            voip_server.bind((serveraddress, config["voip_port"]))
            logging.info(f'UDP VOIP socket bound, listening on port {config["voip_port"]}')
            try:
                voip_handler_thread = threading.Thread(target=Voip.client_handler())
                voip_handler_thread.start()
            except:
                voip_server.close()
                logging.error('Failed to start VOIP Handler! (PROGRAM ERROR!)')
                exit(1)
        except:
            voip_server.close()
            logging.error(f'Failed to bind VOIP Socket to {config["voip_port"]} on {serveraddress}. Check for existing / conflicting processes.')
            exit(1)


# Server Initialisation
logging.info(
    f'Starting a server with name {config["servername"]} on {serveraddress} Server password is {config["password"]}')
Text.start()
Voip.start()
