'''
headers! headers are a way of informing a reciever of the length of an incoming message
however, if a dynamic or pattern based approach is used, users might mimic this to cause havoc!
fixed length headers are  a better solution.

to do this, we need to decide a header length, and add padding to delimit it from the start of our actual message

:< :^ :> are string allignment tools, we can use them to add padding to strings, for example f"{len(this is a test!):<10}" will produce:
    "15********"
then, if we convert the first ten charecters of a NEW message we can get the messages total length and continue decoding a bytestream into a full message, knowing exactly where to stop.

theres nothing to say that you couldn't append message types into this header section,  for example:
    headersize = 10 #this isn't used, but its helpful to note, you could do this as a comment rather then a variable but both forms might be useful
    length_field = 5
    type_field = 5

    msg = input("input your msg here")
    msg_type = "TEXT"
    msg = f"{len(msg):<{length_field}}{len(msg_type):<{type_field}}" + msg 
'''

import socket
import time

headersize = 3
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 9987))
s.listen(5) #listen accepts a number specifying queue length

while True:     
    clientsocket, address = s.accept()
    print(f"{address} has connected")
    
    msg = "this is a test message"
    header_and_msg = f"{len(msg):<{headersize}}" + msg #pack the length of our msg to 10 charecters then append our msg string 
    
    clientsocket.send(bytes(header_and_msg, "utf-8")) #send the combined header/msg encoded as bytes to the client

    while True:
        time.sleep(3)
        msg = f"the time is: {time.time()}"
        header_and_msg = f"{len(msg):<{headersize}}" + msg
        print(msg)
        clientsocket.send(bytes(header_and_msg, "utf-8"))
