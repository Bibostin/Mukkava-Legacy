import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 9997))

full_msg = ""
msg =s.recv(1024)
print(msg.decode("utf-8"))

while True:
    msg = s.recv(8) #8 refers to 8 bytes
    if len(msg) <= 0:
        break
    else:
        full_msg = msg.decode("utf-8")

print(full_msg)
