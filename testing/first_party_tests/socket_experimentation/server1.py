import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 9997))
s.listen(5) #listen accepts a number specifying queue length

while True:
    clientsocket, address = s.accept()
    print(f"{address} has connected")
    clientsocket.send(bytes("welcome to the server", "utf-8"))
    clientsocket.close()
