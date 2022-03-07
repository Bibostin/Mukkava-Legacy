# PROJECT METHODOLOGY
# Pep8/ others compliance (for the most part) helps with writing good code (my only personal exclusion is long lines as this triggers mostly on comments, this one case in point!)
# TODO: Code smelling process should be implemented

# DESIGN STRUCTURE
# utf-8 is better then ascii
# debated switching toml for json but json doesn't allow for comments and nor is it the intended design goal of json.
# TODO: debate Singleton classes and staticMethods VS __init__.py and modules (https://stackoverflow.com/questions/38758668/grouping-functions-by-using-classes-in-python)

# Library setup
import socket  # tcp / udp sockets used for data transfer between client and server
import sys
import threading  # Used for instancing functions (client_handlers, message_handlers.)
import toml  # Provides server config in a simple format. https://github.com/uiri/toml TODO: debate switching to json for simplicity.
import json  # Serialising control messages https://docs.python.org/3.4/library/json.html#json-to-py-table
import logging  # Logging server operation / streaming to stdout
import datetime  # used for appending exact date / start time to to log filenames


# Main vars
config = toml.load('server_config.toml')  # Dictionary pulled from server_config.toml
serveraddress = socket.gethostbyname(socket.gethostname())  # TODO: try fetch ip from config, then default to this
file_semaphore = threading.BoundedSemaphore(1)  # Semephores restrict usage of files by threads to 1 at a time.

voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4 UDP Socket for transmitting opus voice packets
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 TCP Socket for text and command packets

client_sockets = []  # TODO: decide if this is necessary or if a better approach can be used (NOTE MIGHT NEED TO GROUP OR SEPERATE VOIP SOCKETS!)
client_addresses = []  # TODO: decide if this is necessary or if a better approach can be used
client_objects = []  # A List used for macromanaging client_Class objects outside of the nominal client handler threads


# Setup our main logging handler which will "forward" log messages to file_logger and console_logger for processing.
log_handler = logging.getLogger('log_handler')
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(f'{datetime.datetime.now()}/%(levelname)s/%(threadName)s: %(message)s')  # Setup our log message format

file_logger = logging.FileHandler(f'logs/log-{datetime.datetime.now()}', mode='w', encoding='utf-8')  # Setup file logging to textfiles
file_logger.setLevel(logging.DEBUG)
file_logger.setFormatter(log_formatter)
log_handler.addHandler(file_logger)

console_logger = logging.StreamHandler()  # Setup logging output to stdout (screen)
console_logger.setLevel(logging.DEBUG)
console_logger.setFormatter(log_formatter)
log_handler.addHandler(console_logger)


# Object classes
class ClientClass:
    def __init__(self, nickname, deafened, muted):  # self "represents" the individual object instance of a class
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False


# Method Classes
class Service:
    @staticmethod
    def start():  # Separately start the VOIP and Text-control sockets then start the previously setup handler thread for each.
        try:
            voip_server.bind((serveraddress, config["voip_port"]))
            text_server.bind((serveraddress, config["control_port"]))
            text_server.listen()
            log_handler.info(f'UDP VOIP socket bound, listening on port {config["voip_port"]}')
            log_handler.info(f'TCP  socket bound, listening on port {config["control_port"]}')
        except:
            log_handler.error(f'Failed to bind socket to\"{serveraddress}\" verify there isn\'t already a program running on that IP that uses :{config["control_port"]} or :{config["voip_port"]}. Exiting.')
            sys.exit(1)

        try:
            voip_handler_thread = threading.Thread(target=Voip.client_handler())
            text_handler_thread = threading.Thread(target=Text.client_handler())
            text_handler_thread.start()
            voip_handler_thread.start()
        except KeyboardInterrupt:
            log_handler.error('Keyboard interrupt occured!')
            Service.stop()
        except:
            log_handler.error('Program error! failed to start voip or text client handler! Exiting.')
            sys.exit(1)


    #TODO: At the moment, this and the keyboard interrupt exception in start merely conceals the fact that text handler crash and burns when the program stops, that needs to be remedied
    @staticmethod
    def stop():
        file_semaphore.acquire()  # Aquire the file lock PRIOR to shutting down to prevent corruption of whitelist or blacklist mid operation
        log_handler.info('Shutting down server safely.')
        Text.broadcast('Server shutting down!.')
        text_server.close()
        voip_server.close()
        sys.exit(0)


    # TODO: file presence / perm checks, input validation
    @staticmethod
    def file_operation(listname, operation, ip):  # Handles the required file IO for the whitelist and blacklist

        if operation == "check":  # check for occurrence of an IP in whitelist or blacklist.
            file_semaphore.acquire()
            input_file = open(f'{listname}.txt', 'r')
            parsed_file = (input_file.read().splitlines())
            input_file.close()
            file_semaphore.release()
            if ip in parsed_file:
                return True
            else:
                input_file.close()
                file_semaphore.release()
                return False

        elif operation == "append":  # append a given IP to the whitelist or blacklist
            if Service.file_operation(listname, "check", ip) is False:
                file_semaphore.acquire()
                input_file = open(f'{listname}.txt', 'a')
                input_file.write('\n')
                input_file.write(f'{ip}')
                input_file.close()
                file_semaphore.release()
                log_handler.info(f'Successfully added {ip} to {listname}.')
            else:
                log_handler.error(f'attempted to add an already present IP, {ip} to {listname}.')

        elif operation == "remove":  # Remove a given IP from the whitelist or blacklist by checking
            if Service.file_operation(listname, "check", ip) is True:
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
                log_handler.info(f'Successfully removed {ip} from {listname}.')
            else:
                log_handler.error(f'Attempted to remove a non present IP, {ip} from {listname}.')
        else:
            log_handler.error(f'Invalid use of file_operation function, with params: {listname} {operation} {ip}')

    # TODO: Look into encryption methods, protocols and modules /their speeds. (SRTP? AES-256? TLS 1.3? ChaCha20!)
    # Pycrypto, Pycryptdome, Pycryptdomex, PyNaCL
    @staticmethod
    def encryption():
        pass


    # TODO: Look into message integrity validation such as POLY1305 (this will tye into encryption
    @staticmethod
    def verification():
        pass


class Text:
    @staticmethod
    def unicast(client_socket, message):  # Send a message directly to a specific client (DM, Command feedback, etc.)
        client_socket.send(f'{message}'.encode('utf-8'))  # We ensure proper encoding of our message HERE rather then at client.


    @staticmethod
    def broadcast(message):  # Broadcast message to all established sockets the server knows (I.E. for public chat messages)
        for client_socket in client_sockets:
            client_socket.send(f'{message}'.encode('utf-8'))


    # TODO: Add password check
    @staticmethod
    def client_handler():  # Collects inbound text/control clients, and sets them up with a text.message_handler thread
        log_handler.info('Text client handler starting')
        while True:  # While thread is active, continuously check for new clients, check for presence in whitelist / blacklist, setup encryption, check password, then handoff to a Text.message_handler thread for input message processing.
            client_socket, address = text_server.accept()  # pulls next client in from a fifo buffer of inbound socket requests.
            if config['whitelist'] is True:
                if Service.file_operation('whitelist', 'check', address) is False:
                    Text.unicast(client_socket, "You are not whitelisted for this server.")
                    client_socket.close()
                    log_handler.info(f"Connection attempt from {address}, failed whitelist.")
                    continue

            if Service.file_operation('blacklist', 'check', address) is True:
                Text.unicast(client_socket, "You are banned from this server.")
                client_socket.close()
                log_handler.info(f"Connection attempt from {address}, failed blacklist.")
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
    def message_handler(client_socket):  # Parse inbound client messages and determines how to distribute it to other clients / Server actions to take.
        while True:
            try:
                message = client_socket.recv(4096)
                Text.broadcast(message)
            except:
                index = client_sockets.index(client_socket)
                client_socket.close()
                Text.broadcast(f'{client_objects[index].nickname} has disconnected.')
                log_handler.debug(f'{client_addresses[index]}  with nickname {client_objects[index].nickname} has disconnected')

                client_sockets.remove(client_socket)
                client_objects.remove((client_objects[index]))
                break


class Voip:

    @staticmethod
    def client_handler():  # Collects inbound VOIP clients, and sets them up with a Voip.message_handler thread
        log_handler.info('Voip client handler starting')
        pass

    @staticmethod
    def message_handler():  # collect client voip streams, and forward them onto other users based on the status of the ClientClass matrix
        pass


# Server Initialisation
log_handler.info(f'Attempting to start a server with name {config["servername"]} on {serveraddress} Server password is \"{config["password"]}\"')
Service.start()
