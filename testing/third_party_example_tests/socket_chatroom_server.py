import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]  # List of sockets for select.select()
clients = {}  # List of connected clients - socket as a key, user header and name as data
print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)  # Receive our "header" containing message length, it's size is defined and constant
        if not len(message_header):  # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            return False
        message_length = int(message_header.decode('utf-8').strip()) # Convert header to int value
        return {'header': message_header, 'data': client_socket.recv(message_length)} # Return an object of message header and message data
    except:
        return False  # If we are here, client closed connection violently, for example by pressing ctrl+c on his script or just lost his connection socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write) and that's also a cause when we receive an empty message

while True:
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:  # Iterate over notified sockets

        if notified_socket == server_socket:  # If notified socket is THE server socket - new connection, accept it
            client_socket, client_address = server_socket.accept() # Accept new connection that gives us new socket - client socket, connected to this given client only, it's unique for that client The other returned object is ip/port set
            user = receive_message(client_socket)  # Client should send his name right away, receive it

            if user is False:  # If False - client disconnected before he sent his name
                continue
            sockets_list.append(client_socket)  # Add accepted socket to select.select() list
            clients[client_socket] = user  # Also save username and username header
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:  # Else existing socket is sending a message
            message = receive_message(notified_socket)  # Receive message
            if message is False:  # If False, client disconnected, cleanup
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)  # Remove from list for socket.socket()
                del clients[notified_socket]  # Remove from our list of users
                continue
            user = clients[notified_socket]  # Get user by notified socket, so we will know who sent the message
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            for client_socket in clients:  # Iterate over connected clients and broadcast message
                if client_socket != notified_socket: # But don't sent it to sender
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])  # Send user and message (both with their headers) We are reusing here message header sent by sender, and saved username header send by user when he connected


    for notified_socket in exception_sockets: # It's not really necessary to have this, but will handle some socket exceptions just in case
        sockets_list.remove(notified_socket)  # Remove from list for socket.socket()
        del clients[notified_socket]  # Remove from our list of users