#Third Party Libraries / Toolkits
import socket
import threading
import configparser
import logging
import datetime
#first party modules
import error_checking


#sanity checks prior to starting server


#Main Variables
logging.basicConfig(
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',filename='logs/log-{}'.encoding(datetime.datetime.now()),
    encoding='utf-8', level='logging.DEBUG'
)

config = configparser.ConfigParser()
config.read('server_conf.ini')

server_address = socket.gethostbyname(socket.gethostname())
port = ""
password = ""

Client_sockets = []
Client_addresses = []
Client_objects = []

class Client_class:
    def __init__(self, nickname, deafened, muted): #self "represents" the individual object instance of a class
            self.nickname = nickname
            self.deafened = deafened
            self.muted = muted
            self.priority_speaker = False


#--------------------------------------------------------------
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.bind((server_address, port))
text_server.listen()

voip_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voip_server.bind((server_address, port))
voip_server.listen()


#Logging

#Server Initialisation

#VOIP

#Text
def text_broadcast():
    pass

def text_client_handler():
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