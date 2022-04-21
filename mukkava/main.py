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
import mukkava_encryption
import mukkava_audio
import mukkava_socket

import ipaddress
import getpass

audioinput = mukkava_audio.AudioInput

username = input("Please enter a username to use for text chat: ")


while True:
    inital_peer_address = input("Please enter the IP for your inital peer for the VOIP session: ")
    try: ipaddress.ip_address(inital_peer_address); break
    except ValueError: print(f"{inital_peer_address} is not a valid IPv4 or IPv6 address")

while True:
    port = int(input("Please enter the port you wish to use: "))
    if port in range(1024,65535): break
    elif port in range(1,1023): print(f"{port} is a typically reserved port number, supply a number between 1024 - 65535")
    else: print(f"{port} is  a invalid port number, supply a number between 1024 - 65535")

while True:
    try: symetric = mukkava_encryption.Symetric(input("Please enter the preagreed phrase to use as a symetric key (min length of 12 charecters): ")); break
    except ValueError: print("supplied phrase is not 12 charecters long")

while True:
    choice = input("would you like set and test your audio devices? (system defaults will be used otherwise) y/n: ")
    if choice == "y" or choice == "Y": mukkava_audio.audiosetup(); break
    elif choice == "n" or choice == "N": break
    else: print("Invalid input")

