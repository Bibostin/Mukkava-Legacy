import mukkava_audio
import mukkava_encryption
import socket

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
output = mukkava_audio.AudioOutput()
output_buffer_instance1 = output.add_queue()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
client_socket.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
client_socket.connect((socket.gethostname(), 9997))  #connect the tcp socket to 127.0.0.1:9987
output.outstream.start() #Start up the mukkava audiooutput stream handler.

while True:  #infinite loop
    message_length = symetric.decrypt(client_socket.recv(mukkava_encryption.sencrypted_hsize))  #fetch a portion of data corosponding to the length of a encrypted headers length (in this example all headers are 44 bytes)
    if not len(message_length):  #If message length doesn't have a length, the server socket terminated softly and we should exit or handle for this.
        client_socket.close()
        break
    message_length = int(message_length)  #The length of the rest of the audio data is the value of the previously fetched header, decoded from utf-8, strpped of whitespace and converted to an integer value
    output_buffer_instance1.put(symetric.decrypt(client_socket.recv(message_length)))  # Fetch a portion of data corosponding to the length of the next portion of voice data, decrypt it symetrically, then put it in decode buffer 1
    output.process_input() # decode data from flac, mix it with the other buffers and then play it back.

