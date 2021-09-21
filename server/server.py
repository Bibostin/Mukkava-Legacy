#Library-Setup
import socket
import threading
import configparser
import datetime
import logging

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%m-%d %H:%M',
    filename=f'logs/log-{datetime.datetime.now()}',
    level='DEBUG',
)
config = configparser.ConfigParser(); 
config.server = config.read('serverconf.ini')  #Contains server configuration.
#config.blacklist = config.read('blacklist.txt')#File used to store banned IP's.
#config.greylist = config.read('greylist.txt')  #File used to tempoarily store IP's that spam connections.

#Main-Vars
serveraddress = socket.gethostbyname(socket.gethostname())
servername = config.get('basic', 'servername')
voip_port = int(config.get('basic', 'voip_port'))
control_port = int(config.get('basic', 'control_port'))
password = config.get('basic', 'password')
whitelist = config.get('basic', 'whitelist')

Client_sockets = []
Client_addresses = []
Client_objects = []
class Client_class:
    def __init__(self, nickname, deafened, muted): #self "represents" the individual object instance of a class
            self.nickname = nickname
            self.deafened = deafened
            self.muted = muted
            self.priority_speaker = False

#Server Initialisation

logging.info(f' Starting a server with name {servername} on {serveraddress}:{voip_port} Server password is {password}')

text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.bind((serveraddress, control_port))
text_server.listen()

voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voip_server.bind((serveraddress, voip_port))
voip_server.listen()  #UDP DOESNT "LISTEN" THIS NEEDS TO BE CHANGED FOR EITHER AN APPROPRIATE METHOD OR USERMADE FUNC CALL.




#VOIP

#Text
def text_broadcast():
    pass

def text_client_handler():
    pass
    while True:
        client_socket, address = text_server.accept()
        logging.debug("client connected from {}".format(address))

        client_socket.send("REQ-CLIENT-STATUS".encode('ascii'))
        client_socket_return = socket.recv(1024).decode('ascii')
        client_object = Client_class(client_socket_return.nickname, client_socket_return.deafened, client_socket_return.muted)

        Client_objects.append(client_object)
        Client_addresses.append(address)
        Client_sockets.append(socket)

def text_server_reciever():
    pass
#Encryption

#Administration