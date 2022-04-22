
import mukkava_audio
import mukkava_encryption
import socket

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
audioinput = mukkava_audio.AudioInput()

length_headersize = 4 # constant variable for the size of the message length header in bytes. must be the same value between all clients


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # This sets an option that should let us reclaim dead sockets
s.bind((socket.gethostname(), 9997))
s.listen(5)

while True:
    print("server waiting for new client")
    clientsocket, address = s.accept()  #take the return s.accept (a socket object and an ip address)
    print(f"{address} has connected")
    audioinput.instream.start()  # Now that we have a client, start the audioinput stream in order to start buffering voice data
    while True:
        try:
            data = symetric.encrypt(audioinput.data_buffer.get())  # fetch data from the audioinput stream, then symetrically encrypt it
            header = bytes(f"{len(data):<{length_headersize}}", "utf-8")
            print(header+data)
            clientsocket.send(header+data)  # send the combined header and input voice data down the socket to the client

        except ConnectionResetError:  #if the client violently drops the socket
            audioinput.instream.stop() #stop our input stream in order to ensure we do create artifical audio latency (in mukkava, this should only occur if all clients are dropped)
            print(f"{address} disconnected")
            clientsocket.close() # properly handle the client socket on our end
            break
