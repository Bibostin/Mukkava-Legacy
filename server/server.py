# Library-Setup
import socket
import threading
import toml
import datetime
import logging

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%m-%d %H:%M',
    filename=f'logs/log-{datetime.datetime.now()}',
    level='DEBUG',
)

# Main-Vars
config = toml.load('config.toml')  #This returns a dictionary, check config.toml for variables in use.
serveraddress = socket.gethostbyname(socket.gethostname())
client_sockets = []
client_addresses = []
client_objects = []

class Client_Class:
    def __init__(self, nickname, deafened, muted):  # self "represents" the individual object instance of a class
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False


# Server Initialisation
logging.info(f' Starting a server with name {config["servername"]} on {serveraddress} Server password is {config["password"]}')

text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.bind((serveraddress, config['control_port']))
text_server.listen()
logging.info(f' TCP Text and control socket started, listening on port {config["control_port"]}')

voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voip_server.bind((serveraddress, config["voip_port"]))
logging.info(f' UDP VOIP socket started, listening on port {config["voip_port"]}')

#FILE IO //TO DO: INCLUDE LIMITS ON ACCESS TO FILES
def file_operation(list, operation, ip): #Handles the required file IO for the whitelist and blacklist (and hopefully greylist!)
    if operation == "check": #check if there is an occurance of a given IP in whitelist or blacklist and give feedback of this.
        input_file = open(f'{list}.txt', 'r')
        if ip in input_file.readlines():
            input_file.close()
            return True
        else:
            input_file.close()
            return False

    elif operation == "append": #append a given IP to the whitelist or blacklist
        if file_operation(list, "check", ip) is False:
            input_file = open(f'{list}.txt', 'a')
            input_file.write('\n')
            input_file.write(f'{ip}')
            input_file.close()
        else: logging.debug('attempted to add an allready present IP.')

    elif operation == "remove": #Remove a given IP from the whitelist or blacklist by checking
        if file_operation(list, "check", ip) is True:
            input_file = open(f'{list}.txt', 'r')
            line_list = input_file.readlines()
            input_file.close()
            del line_list[line_list.index(ip)]
            output_file = open(f'{list}.txt', 'w+')
            for lines in line_list:
                output_file.write(lines)
            output_file.close()
        else: logging.debug('attempted to remove a non present IP.')
    else: logging.debug(f'Invalid use of file_operation function, with params: {list} {operation} {ip}')

# VOIP

# TEXT AND CONTROL
def text_unicast(client_socket, message): #Send a message directly to a specific client (e.g. command feedback)
    client_socket.send(message)

def text_multicast(client_socket_list, message): #Send a message to a list of sockets not specified by the Client_sockets array.
    for client_socket in client_socket_list:
        client_socket.send(message)

def text_broadcast(message): #Broadcast message to all established sockets the server knows (I.E. for Chat messages)
    for client_socket in client_sockets:
        client_socket.send(message)

def text_client_handler():
    pass
    while True:
        client_socket, address = text_server.accept()
        logging.info(f"client connected from {address}")

        client_socket.send("REQ-CLIENT-STATUS".encode('utf-8')) #UTR-8 offers support for far more charectertypes / Unicode
        client_socket_return = client_socket.recv(1024).decode('utf-8')
        client_object = Client_Class(client_socket_return.nickname, client_socket_return.deafened, client_socket_return.muted)

        client_objects.append(client_object)
        client_addresses.append(address)
        client_sockets.append(socket)

def text_server_receiver():
    pass

# Encryption

# Administration
