#DESIGN CHOICE NOTES FOR SELF AND FURTHER UPTAKE
#UTF-8 offers support for far more charectertypes / Unicode options then ASCII
#Pickle and marshal are aweful and allow for remote execution, I've used JSON because its simple
#TOML was used for file IO simply because I dislike working with YAML and JSON, TOML is fine for somthing this basic.
#This code is monolithic by choice, Pythons user modules end up making sphagetti code where you have different references and cyclic dependencies

# Library-Setup
import socket #tcp / udp sockets used for data disperal
import threading #Used for instancing functions that need to run in background or be iterable.
import toml #Provides server config in a simple format.
import json #Serialising control messages
import datetime #used for appending date to logfilenames
import logging #what it says on the tin

#Setup file logging TODO: add seperate stream output to stdout logging output on console
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%m-%d %H:%M',
    filename=f'logs/log-{datetime.datetime.now()}',
    level='DEBUG',)

# Main-Vars
config = toml.load('server_config.toml')  #This returns a dictionary, check server_config.toml for variables in use.
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

#FILE IO TODO: INCLUDE LIMITS ON ACCESS TO FILES / CHECKS FOR FILE PRESENCE / VALID IP FORMAT
def file_operation(listname, operation, ip): #Handles the required file IO for the whitelist and blacklist (and hopefully greylist!)
    if operation == "check": #check if there is an occurance of a given IP in whitelist or blacklist and give feedback of this.
        input_file = open(f'{listname}.txt', 'r')
        parsed_file = (input_file.read().splitlines())
        if ip in parsed_file:
            input_file.close()
            return True
        else:
            input_file.close()
            return False

    elif operation == "append": #append a given IP to the whitelist or blacklist
        if file_operation(listname, "check", ip) is False:
            input_file = open(f'{listname}.txt', 'a')
            input_file.write('\n')
            input_file.write(f'{ip}')
            input_file.close()
            logging.debug(f'Successfully added {ip} to {listname}.')
        else: logging.error(f'attempted to add an allready present IP, {ip} to {listname}.')

    elif operation == "remove": #Remove a given IP from the whitelist or blacklist by checking
        if file_operation(listname, "check", ip) is True:
            input_file = open(f'{listname}.txt', 'r')
            parsed_file = input_file.read().splitlines()
            input_file.close()
            parsed_file.remove(ip)
            output_file = open(f'{listname}.txt', 'w+')
            for lines in parsed_file:
                output_file.write(lines)
            output_file.close()
            logging.debug(f'Successfully removed {ip} from {listname}.')
        else: logging.error(f'Attempted to remove a non present IP, {ip} from {listname}.')
    else: logging.error(f'Invalid use of file_operation function, with params: {listname} {operation} {ip}')

def io_protector (): #provides file locking for the whitelist, blacklist, client objects, addresses and socket arrays to stop threads corrupting them.
    pass

# TXT AND CONTROL
def text_unicast(client_socket, message): #Send a message directly to a specific client (e.g. command feedback, pokes.) used in place of straight socket.send to ensure encoding.
    client_socket.send(message.encode('utf-8'))

def text_broadcast(message): #Broadcast message to all established sockets the server knows (I.E. for public chat messages)
    for client_socket in client_sockets:
        client_socket.send(message.encode('utf-8'))

def text_client_handler(): #Handles collecting inbound clients, and sets them up with a text_message_handler thread
    while True:
        client_socket, address = text_server.accept() #accept basically pulls a client in from a fifo buffer of inbound socket requests.
        if config['whitelist'] is True:
            if file_operation('whitelist', 'check', address) is False :
                text_unicast(client_socket, "You are not whitelisted for this server.")
                client_socket.close()
                logging.debug(f"Connection attempt from {address}, failed whitelist.")
                continue

        if file_operation('blacklist', 'check', address) is True:
            text_unicast(client_socket, "You are banned from this server.")
            client_socket.close()
            logging.debug(f"Connection attempt from {address}, failed blacklist.")
            continue

        text_unicast(client_socket, "REQ-CLIENT-STATUS")
        client_socket_return = json.loads(client_socket.recv(4096).decode('utf-8')) #another fifo buffer of recieved data decoded from utf-8 then json.
        client_object = Client_Class(client_socket_return.nickname, client_socket_return.deafened, client_socket_return.muted)
        text_broadcast(f'{client_object.nickname} connected. {config["greeting_message"]}')
        logging.info(f"client {client_object.nickname} connected from {address}. muted:{client_object.deafened}.")

        client_objects.append(client_object)
        client_addresses.append(address)
        client_sockets.append(client_socket)

        thread = threading.Thread(target=text_message_handler(client_socket))
        thread.start()


def text_message_handler(client_socket): #Parse inbound client messages and determines how to distribute it to other clients / additional actions to take
    while True:
        try:
            message = client_socket.recv(4096)
            text_broadcast(message)
        except:
            index = client_sockets.index(client_socket)
            client_socket.close()
            text_broadcast(f'{client_objects[index].nickname} has disconnected.')
            logging.debug(f'{client_addresses[index]}  with nickname {client_objects[index].nickname} has disconnected')

            client_sockets.remove(client_socket)
            client_objects.remove((client_objects[index]))
            client_addresses.remove((client_addresses[index]))
            break


# VOIP
def voip_client_handler():
    pass

def voip_message_handler():
    pass

# Encryption



# Server Initialisation
logging.info(f' Starting a server with name {config["servername"]} on {serveraddress} Server password is {config["password"]}')

text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.bind((serveraddress, config['control_port']))
text_server.listen()
logging.info(f' TCP Text and control socket started, listening on port {config["control_port"]}')

voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voip_server.bind((serveraddress, config["voip_port"]))
logging.info(f' UDP VOIP socket started, listening on port {config["voip_port"]}')

text_client_handler_thread = threading.Thread(target=text_client_handler())
text_client_handler_thread.start()

voip_handler_thread = threading.Thread(target=voip_client_handler())
voip_handler_thread.start()
