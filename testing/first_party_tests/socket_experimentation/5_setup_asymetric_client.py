import mukkava_audio
import mukkava_encryption
import socket

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
asymetric = mukkava_encryption.Asymetric()
output = mukkava_audio.AudioOutput()
output_buffer_instance1 = output.add_queue()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
client_socket.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
client_socket.connect((socket.gethostname(), 9997))  #connect the tcp socket to 127.0.0.1:9987
output.outstream.start() #Start up the mukkava audiooutput stream handler.


message_length = int(symetric.decrypt(client_socket.recv(symetric.encrypted_hsize)))
npkb = symetric.decrypt(client_socket.recv(message_length))

message_length = int(symetric.decrypt(client_socket.recv(symetric.encrypted_hsize)))
nvkb = symetric.decrypt(client_socket.recv(message_length))

asymetric.setup(npkb, nvkb)

data = symetric.encrypt(asymetric.public_encryption_key_bytes)
header = symetric.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
client_socket.send(header + data)

data = symetric.encrypt(asymetric.public_verify_key_bytes)
header = symetric.encrypt(f"{len(data):<{mukkava_encryption.message_length_hsize}}")
client_socket.send(header + data)

while True:  #infinite loop
    message_length = int(asymetric.decrypt(client_socket.recv(asymetric.encrypted_hsize))) #fetch a portion of data corosponding to the length of a encrypted headers length asymetric headers are 108 bytes in this example)
    output_buffer_instance1.put(asymetric.decrypt(client_socket.recv(message_length)))  # Fetch a portion of data corosponding to the length of the next portion of voice data, decrypt it asymetrically, then put it in decode buffer 1
    output.process_input() # decode data from flac, mix it with the other buffers and then play it back.

