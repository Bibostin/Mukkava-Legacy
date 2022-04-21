'''
if [headersize:] or [:headersize] are confusing you, look at string slice notation
the tldr is that its used to split a string into sections based on explicit ranges
'''

import socket

headersize = 10 #Set our headersize to 10 charecters
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 9997))

new_msg = True #new msg will be used to control whether we are working with the first section of a new message, and thus if we need to strip the msg length  from the inital header
full_msg = "" #string that the final buffered msg will be taken from

while True:
    msg = s.recv(16) # note, recv's value must be larger then the headersize, otherwise you may encounter issues
    if new_msg:  #if new msg is set to true
        msglen = int(msg[:headersize].decode("utf-8")) #msglen = the integer value of msg sliced ending after our header length, which should corospond to our msgs length
        print("new message length:", msglen) 
        new_msg = False #set newmsg to false, as we have our current msg's length
        
    full_msg += msg.decode("utf-8") # add the next recieved set of buffered byte data to our full msg
        
    if len(full_msg) - headersize == msglen: # if the len of full message - the size of our header is equal to the sent msglen
        print(full_msg[headersize:]) #print the full message, with the header stripped
        new_msg = True #Set new msg back to true, as we need to fetch our next messages length           
        full_msg = "" #reset the value of full msg
