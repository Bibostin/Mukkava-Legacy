
import mukkava_audio
import mukkava_encryption
import socket

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
asymetric = mukkava_encryption.Asymetric()
audioinput = mukkava_audio.AudioInput()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # This sets an option that should let us reclaim dead sockets
s.bind((socket.gethostname(), 9997))
s.listen(5)

while True:
    audioinput.instream.stop()
    print("server waiting for new client")
    clientsocket, address = s.accept()  #take the return s.accept (a socket object and an ip address)
    address = address[0]
    print(f"{address} has connected")
    audioinput.instream.start()  # Now that we have a client, start the audioinput stream in order to start buffering voice data

    data = symetric.encrypt(asymetric.public_encryption_key_bytes)
    header = symetric.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
    clientsocket.send(header+data)

    data = symetric.encrypt(asymetric.public_verify_key_bytes)
    header = symetric.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
    clientsocket.send(header+data)

    message_length = int(symetric.decrypt(clientsocket.recv(symetric.encrypted_hsize)))
    npkb = symetric.decrypt(clientsocket.recv(message_length))

    message_length = int(symetric.decrypt(clientsocket.recv(symetric.encrypted_hsize)))
    nvkb = symetric.decrypt(clientsocket.recv(message_length))

    asymetric.setup(npkb, nvkb)
    while True:
        try:
            data = audioinput.data_buffer.get()
            data = asymetric.encrypt(data)  # fetch data from the audioinput stream, then symetrically encrypt it
            header = asymetric.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")  #ge tthe length of our encrypted voice data, pad it to four charecters, encode tu utf-8 and then encrypt symetrically, should produce a 44 byte long header.
            clientsocket.send(header+data)  # send the combined header and input voice data down the socket to the client
        except ConnectionResetError:  #if the client violently drops the socket
            audioinput.instream.stop() #stop our input stream in order to ensure we dont create artifical audio latency (in mukkava, this should only occur if all clients are dropped)
            print(f"{address} disconnected")
            clientsocket.close() # properly handle the client socket on our end
            break
