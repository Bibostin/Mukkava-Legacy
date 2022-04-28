'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:

TODO:
    #ENCRYPTION - EXCEPTION HANDLING
    #Consider moving back to .conf (not needed, look at toml sections)
    #peer address validation as ipv4 compliant
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

import ipaddress
from mukkava_audio import audiosetup
import mukkava_socket



print(".___  ___.  __    __   __  ___  __  ___      ___   ____    ____  ___ \n"
      "|   \/   | |  |  |  | |  |/  / |  |/  /     /   \  \   \  /   / /   \ Simple, direct P2P voip client\n"
      "|  \  /  | |  |  |  | |  '  /  |  '  /     /  ^  \  \   \/   / /  ^  \ Made by Zachary SC Goggin\n"
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
    if len(username) >= 2:
        break
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
    port = (input("Please enter the port you want your mukkava client to listen on / connect over (1024 - 65535): "))
    if not port:
        print("no port supplied, defaulting to testing port, 9987")
        port = 9987
        break
    try: port = int(port)
    except ValueError: print("You have entered a floating point value, use an integer"); continue
    if port in range(1024,65535): break
    elif port in range(1,1023): print(f"{port} is a typically reserved port number, supply a number between 1024 - 65535")
    else: print(f"{port} is  a invalid port number, supply a number between 1024 - 65535")


while True:
    choice = input("would you like to connect to an inital peer client directly? y/n: ")
    if choice == "y" or choice == "Y":
        while True:
            inital_peer_address = input("Please enter the IPv4 address for your inital peer for the VOIP session (dot-decimal notation): ")
            try: ipaddress.ip_address(inital_peer_address); break
            except ValueError: print(f"\"{inital_peer_address}\" is not a valid IPv4 address")
        tcpstack = mukkava_socket.TCPStack(port, symetricphrase, username)
        tcpstack.start(inital_peer_address)
        break
    elif choice == "n" or choice == "N":
        tcpstack = mukkava_socket.TCPStack(port, symetricphrase, username)
        tcpstack.start()
        break
    else: print("Invalid choice input")






