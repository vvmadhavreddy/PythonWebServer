import io
import socket
import sys

class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # Create a listening socket on the WSGI server class object
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket
        listen_socket.bind(server_address)

        # Activate the socket and start listening for the requests
        listen_socket.listen(self.request_queue_size)

        # Get server hostname and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        # Return headers set by Web Framework/Web Application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()

            # Handle one request and close the client connection.
            # Then loop over to wait for another client connection
            self.handle_one_request()

    def handle_one_request(self):
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data = request_data.decode('utf-8')

        # Print formatted request data
        print(''.join(f'< {line}\n' for line in request_data.splitlines()))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # Time to call our application callable and get back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text: str):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')

        # Break down the request lines into components
        (
            self.request_method,
            self.path,
            self.request_version
        ) = request_line.split()

    def get_environ(self):
        env = {}

        # Required WSGI variables
        env['wsgi.version'] = (1,0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variables
        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = self.server_port

        return env

    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Sat, 24 Jul 2021 22:44:00 IST'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')

            # Print formatted response data
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))

            # Encode the response into byte format to send back to the client
            response_bytes = response.encode()

            # Send the encoded response to the client
            self.client_connection.sendall(response_bytes)

        finally:
            # Close the client connection
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()