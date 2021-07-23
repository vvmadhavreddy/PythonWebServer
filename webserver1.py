# Import the socket module.
import socket

# Declare the required constants.
HOST, PORT = '', 8888

# Create a socket instance passing two parameters, AddressFamily and SocketKind :-
# 1) AF_INET - refers to the address family ipv4 and
# 2) SOCK_STREAM - means using the TCP protocol.
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set options associated with the created socket.
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the particular port and as no host address is entered
# this starts listening to requests coming from other computers too.
listen_socket.bind((HOST, PORT))

# Start listening on the network and 1 here means only 1 other connection
# is kept waiting and the rest would be refused.
listen_socket.listen(1)
print(f'Serving HTTP on port {PORT}...')
while True:
    # Connection is established returning a tuple of the connected socket obejct
    # and the client address.
    client_connection, client_address = listen_socket.accept()

    # Request data from the client is received.
    request_data = client_connection.recv(1024)
    print(request_data.decode('utf-8'))

    # A static response is created.
    http_response = """\
HTTP/1.1 200 OK

Hello, World from Server!
"""
    # The response is encoded and sent to the client.
    client_connection.sendall(bytes(http_response, 'utf-8'))

    # The socket connection is closed.
    client_connection.close()