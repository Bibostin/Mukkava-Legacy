#Third Party Libraries / Toolkits
import socket
import threading
import toml
import json

#Main-Vars
class Client_Class:
    def __init__(self, nickname, deafened, muted):
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False

config = toml.load('client_config.toml')  #This returns a dictionary, check server_config.toml for variables in use.
client_self = Client_Class(config['nickname'], config["deafened"], config["muted"])
client_objects = []


def text_unicast(message): #ensure proper encoding.
    text_client.send(message.encode('utf-8'))

def text_sender(): #provide the user a means to input messages to send to the server and other users.
    while True:
        text_unicast(f"{input()}")

def text_reciever():
    while True:
        message = text_client.recv(4096).decode("utf-8")
        if message == "REQ-CLIENT-STATUS":
            text_unicast(json.dumps(client_self))
        else:
            print(message)




# Client Initalization
text_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_sender_thread = threading.Thread(target=text_sender())
text_reciever_thread = threading.Thread(target=text_reciever())
text_client.connect("127.0.0.1")
text_reciever_thread.start()
text_sender_thread.start()
print("started")

#voip_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

