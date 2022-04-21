'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:

    TCP sockets are blocking by default
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
'''
import socket
import threading
import sys

class Stack:
    def __init__(self, port):
        self.port = port
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 TCP Socket for receiving text and command packets
        self.tcp_server.bind(socket.gethostname(socket.gethostname), self.port)
        self.tcp_client_socket_dict = {}

        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4 TCP Socket for recieving audio data
        self.udp_server.bind(socket.gethostname(socket.gethostname), self.port)
        self.udp_client_socket_dict = {}

    def add_socket(self, type):
        if type is "tcp" or type is "TCP":
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif type is "udp" or type is "UDP":
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else :
            raise ValueError("attempted to add a non tcp or udp socket")
        return temp_socket



