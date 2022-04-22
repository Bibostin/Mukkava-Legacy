import mukkava_audio
import mukkava_encryption
import socket

symetric = mukkava_encryption.Symetric("lorumipsumdoremifarquad")
output = mukkava_audio.AudioOutput()
output_buffer_instance1 = output.add_queue()

length_headersize = 4  # constant variable for the size of the message length header in bytes. must be the same value between all clients

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
client_socket.settimeout(30)  # set the maximum ttl for a socket read, write or connect operation.
client_socket.connect((socket.gethostname(), 9997))  #connect the tcp socket to 127.0.0.1:9987
output.outstream.start() #Start up the mukkava audiooutput stream handler.

while True:  #infinite loop
    message_length = client_socket.recv(length_headersize)  #fetch a portion of data corosponding to the length of our length headersize (in this example, the first 10 charecters of sent data)
    if not len(message_length):  #If message length doesn't have a length, the server socket terminated softly and we should exit or handle for this.
        break
    message_length = int(message_length.decode("utf-8").strip())  #The length of the audio data to come is the previously fetched portion of data, decoded from utf-8, strpped of whitespace and converted to an integer value
    output_buffer_instance1.put(symetric.decrypt(client_socket.recv(message_length)))  # Fetch a portion of data corosponding to the length of the next portion of voice data, decrypt it symetrically, then put it in decode buffer 1
    output.process_input() # decode data from flac, mix it with the other buffers and then play it back.


#NOTE FOR ZA TOMORROW, LOOK MORE INTO SELECT MODULE, IT MAY BE THE WAY FORWARD RATHER THEN THREADING