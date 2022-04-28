#Dictionary structures are a powerful method of grouping objects together / making iterable code based off a socket object, my aim here is to show how you can
#group a socket with an address value and a encryption box object 

import socket
socket_info = {"inbound_sockets": {}, "outbound_sockets": {}}
placebo_address = ["empty1", "empty2", "empty3"]
placebo_encryption =["empty1", "empty2", "empty3"]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 9987))
server_socket.listen()

placebo_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
placebo_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
placebo_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

placebo_socket1, placebo_socket2, placebo_socket3 .settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
placebo_socket1.connect((socket.gethostbyname(socket.gethostname()), 9987))
placebo_socket2.connect((socket.gethostbyname(socket.gethostname()), 9987))
placebo_socket3.connect((socket.gethostbyname(socket.gethostname()), 9987))  # connect the supplied address

for i in range(3):
    client_socket, address = server_socket.accept()
    socket_info["outbound_sockets"][client_socket] = {}
    socket_info["outbound_sockets"][client_socket]["address"] = placebo_address[i]
    socket_info["outbound_sockets"][client_socket]["encryption"] = placebo_encryption[i]
    print(address)

for socket in socket_info["outbound_sockets"]:
    print(socket_info["outbound_sockets"][socket])

