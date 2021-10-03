#Third Party Libraries / Toolkits
import socket
import threading
import configparser
import toml

#Main-Vars
class Client_Class:
    def __init__(self, nickname, deafened, muted):  # self "represents" the individual object instance of a class
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False

config = toml.load('server_config.toml')  #This returns a dictionary, check server_config.toml for variables in use.
client_objects = []
client_self = Client_Class(config['nickname'], False, False) #equivlient to the individual client_


