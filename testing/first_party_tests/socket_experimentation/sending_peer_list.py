import socket
import ast
import json

#part of the job of a peer to peer network is to disseminate the addressing of other peers to nodes that connect, this test file aims to show a few ways we could send addressing
#information to a remote node, and explains the pitfalls of each method. https://stackoverflow.com/questions/66480073/fastest-implementation-of-ast-literal-eval

local_address_list = ["192.168.2.1", "192.168.2.2", "192.168.2.3", "192.168.2.4"]
remote_address_list1 = []


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 9987))
server_socket.listen()

placebo_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
placebo_socket1.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
placebo_socket1.connect((socket.gethostbyname(socket.gethostname()), 9987))  # connect the supplied address

client_socket, address = server_socket.accept()

#THIS IS CRUDE BUT EFFECTIVE AS WE HAVE TO PROCESS EACH ADDRESS INDIVIDUALLY (low efficency, unideal, but not insecure)
for address in local_address_list:
    data = bytes(address, "utf-8")
    client_socket.send(data)
    remote_address_list1.append(placebo_socket1.recv(len(data)).decode())
print(remote_address_list1)



#THIS IS quickerish, but it has vulnerabilities, while it doesn't open up the program to arbitrary execution like straight eval() does, it can still be used to crash a client, not ideal.
data = bytes(str(local_address_list),"utf-8")
datalen = len(data)

client_socket.send(data)
remote_address_list2 = placebo_socket1.recv(datalen)
print(remote_address_list2)

remote_address_list2 = remote_address_list2.decode()
print(remote_address_list2)

remote_address_list2 = ast.literal_eval(remote_address_list2)
print(remote_address_list2)

#This is quicker then the previous two methods, AND safer as we dont evaluate any python code, we simply treat what we are sent as JSON and translate it into a list, which is harder to manipulate!
remote_address_list3 = json.dumps(remote_address_list1)
print(remote_address_list3, type(remote_address_list3))
remote_address_list3 = json.loads(remote_address_list3)
print(remote_address_list3, type(remote_address_list3))