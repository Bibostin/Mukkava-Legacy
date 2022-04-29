#Dictionary structures are a powerful method of grouping objects together / making iterable code based off a socket object, my aim here is to show how you can
#group a socket with an address value and a encryption box object 

import socket
socket_info = {"inbound_sockets": {}, "outbound_sockets": {}}
placebo_address = "192.168.2.4"
placebo_encryption ="empty1"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 9987))
server_socket.listen()

placebo_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
placebo_socket1.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
placebo_socket1.connect((socket.gethostbyname(socket.gethostname()), 9987))  # connect the supplied address

client_socket, address = server_socket.accept()
socket_info["outbound_sockets"][client_socket] = {}
socket_info["outbound_sockets"][client_socket]["address"] = placebo_address
socket_info["outbound_sockets"][client_socket]["encryption"] = placebo_encryption
print(socket_info)

#Assert that you can use a socket object key to send and recieve data
for socket in socket_info["outbound_sockets"]:
    socket.send(bytes("test", "utf-8"))
    print(placebo_socket1.recv(4).decode())

#assert that we can look up a specific address in a dictionary structure
if placebo_address in  tuple(socket_info["outbound_sockets"].values()): # this wont work as it doesn't tunnel down into the lower dict
    print("true1")
if placebo_address in  tuple(socket_info["outbound_sockets"][client_socket].values()): #this does, but raises the problem of how do we access it?
    print("true2")

for sock in socket_info["outbound_sockets"]: #therefore we can do this, which works fine but feels innefcient
    if placebo_address in socket_info["outbound_sockets"][sock].values():
        print("true3")

#then as a less wasteful catcher
catch = False
for sock in socket_info["outbound_sockets"]: #And then as a catcher
    if placebo_address in socket_info["outbound_sockets"][sock].values():
        catch = True
        break

#or as a function which makes other code more readable
def check_for_existing_socket(sock_dict, address):
    for sock in socket_info[f"{sock_dict}"]:
        if address in socket_info[sock_dict][sock].values():
            return socket_info[sock_dict][sock]
    return False
print(check_for_existing_socket("outbound_sockets", placebo_address))

# and now finally, we can use this to our advantage!
if (test := check_for_existing_socket("outbound_sockets", placebo_address)):
    print(test["encryption"])
else:
    print("false")