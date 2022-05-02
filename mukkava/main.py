'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    Simple program main menu
    taking user input for items required to setup connection
    ensuring user input is clean and fits the application
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
N/A
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
Simply run main.py :)
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
Ncurses - Ncurses was considered but dropped due to me not seeing any percievable benefit of a terminal text client, over a slightly more fancy terminal text client, that would ineviitably
          have to be rewritten to accomadate a GUI library.
pysimpleGUI - pysimpleGUI was tested and seemed promisng but was dropped due to time constraints.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

import ipaddress
from mukkava_audio import audiosetup
import mukkava_socket

print(".___  ___.  __    __   __  ___  __  ___      ___   ____    ____  ___ \n"
      "|   \/   | |  |  |  | |  |/  / |  |/  /     /   \  \   \  /   / /   \  A Simple, E2E encrypted, direct P2P voip client\n"
      "|  \  /  | |  |  |  | |  '  /  |  '  /     /  ^  \  \   \/   / /  ^  \ Made by Zachary SC Goggin, UP893303\n"
      "|  |\/|  | |  |  |  | |    <   |    <     /  /_\  \  \      / /  /_\  \ ver 0.1 - 25/04/2022\n"
      "|  |  |  | |  `--'  | |  .  \  |  .  \   /  _____  \  \    / /  _____  \ \n"
      "|__|  |__|  \______/  |__|\__\ |__|\__\ /__/     \__\  \__/ /__/     \__\ ")

while True:
    choice = input("would you like to set and test your audio devices? (system defaults will be used otherwise) y/n: ")
    if choice == "y" or choice == "Y": audiosetup(); break
    elif choice == "n" or choice == "N": break
    else: print("Invalid choice input")


while True:
    username = input("Please enter a username to use for text chat: ")
    if len(username) >= 2: break
    print("Username must have atleast two chareters")


while True:
    symetricphrase = input("Please enter the preagreed phrase to use as a symetric key (min length of 12 charecters): ")
    if not symetricphrase:
        print("no key supplied, defaulting to testing key \"lorumipsumdoremifarquad\"")
        symetricphrase = "lorumipsumdoremifarquad"
        break
    elif len(symetricphrase) > 12: break
    else: print("supplied phrase is not 12 charecters long")


while True:
    listen_port = (input("Please enter the port you want your mukkava client to listen on  (1024 - 65535): "))
    if not listen_port:
        print("no port supplied, defaulting to testing port, 9987")
        listen_port = 9987
        break
    try: listen_port = int(listen_port)
    except ValueError: print("You have entered a floating point or charecter value, use an integer"); continue
    if listen_port in range(1024, 65535): break
    elif listen_port in range(1,1023): print(f"{listen_port} is a typically reserved port number, supply a number between 1024 - 65535")
    else: print(f"{listen_port} is  a invalid port number, supply a number between 1024 - 65535")


while True:
    connect_port = (input("Please enter the port you want your mukkava client to connect over (1024 - 65535): "))
    if not connect_port:
        print("no port supplied, defaulting to testing port, 9987")
        connect_port = 9988
        break
    try: connect_port = int(connect_port)
    except ValueError: print("You have entered a floating point or charecter value, use an integer"); continue
    if connect_port in range(1024, 65535): break
    elif connect_port in range(1,1023): print(f"{connect_port} is a typically reserved port number, supply a number between 1024 - 65535")
    else: print(f"{connect_port} is  a invalid port number, supply a number between 1024 - 65535")


while True:
    choice = input("would you like to connect to an inital peer client directly? y/n: ")
    if choice == "y" or choice == "Y":
        while True:
            inital_peer_address = input("Please enter the IPv4 address for your inital peer for the VOIP session (dot-decimal notation): ")
            try: ipaddress.ip_address(inital_peer_address); break
            except ValueError: print(f"\"{inital_peer_address}\" is not a valid IPv4 address")
        tcpstack = mukkava_socket.TCPStack(listen_port, connect_port, symetricphrase, username, inital_peer_address)
        break
    elif choice == "n" or choice == "N":
        tcpstack = mukkava_socket.TCPStack(listen_port, connect_port, symetricphrase, username)
        break
    else: print("Invalid choice input")






