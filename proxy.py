"""A proxy server that forwards requests from one port to another server.

To run this using Python 2.7:

% python proxy.py

It listens on a port (`LISTENING_PORT`, below) and forwards commands to the
server. The server is at `SERVER_ADDRESS`:`SERVER_PORT` below.
"""

# This code uses Python 2.7. These imports make the 2.7 code feel a lot closer
# to Python 3. (They're also good changes to the language!)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import library

# Where to find the server. This assumes it's running on the same machine
# as the proxy, but on a different port.
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 7777

# The port that the proxy server is going to occupy. This could be the same
# as SERVER_PORT, but then you couldn't run the proxy and the server on the
# same machine.
LISTENING_PORT = 8888

# Cache values retrieved from the server for this long.
MAX_CACHE_AGE_SEC = 60.0  # 1 minute


def forward_command_to_server(command, server_addr, server_port):

  """Opens a TCP socket to the server, sends a command, and returns response.

  Args:
    command: A single line string command with no newlines in it.
    server_addr: A string with the name of the server to forward requests to.
    server_port: An int from 0 to 2^16 with the port the server is listening on.
  Returns:
    A single line string response with no newlines.
  """


  # Opens TCP socket to server
  client_socket = library.create_client_socket(server_addr, server_port)

  client_socket.send(command + '\n')

  response_from_server = library.read_command(client_socket)

  client_socket.close()

  return response_from_server + '\n'


def check_cached_response(command_line, cache):

  cmd, name, text = library.parse_command(command_line)

  # Update the cache for PUT commands but also pass the traffic to the server.
  if cmd == "PUT":
    # Updates the cache
    cache.store_value(name,text)

    # Passes the traffic to the server
    forward_command_to_server(command_line, SERVER_ADDRESS, SERVER_PORT)
    return None

  # Stores the key/value information for all GET requests in cache
  elif cmd == "GET":
    if name in cache:
      return cache[name]
    else:
      forward_command_to_server(command_line, SERVER_ADDRESS, SERVER_PORT)


def proxy_client_command(sock, server_addr, server_port, cache):

  """Receives a command from a client and forwards it to a server:port.

  A single command is read from `sock`. That command is passed to the specified
  `server`:`port`. The response from the server is then passed back through
  `sock`.

  Args:
    sock: A TCP socket that connects to the client.
    server_addr: A string with the name of the server to forward requests to.
    server_port: An int from 0 to 2^16 with the port the server is listening on.
    cache: A KeyValueStore object that maintains a temorary cache.
    max_age_in_sec: float. Cached values older than this are re-retrieved from
      the server.
  """


  # Read and parses the command line
  command_line = library.read_command(sock)
  cmd, name, value = library.parse_command(command_line)

  # Forwards command straight to server if the command is "PUT"
  if cmd == 'PUT':
    response_from_server = forward_command_to_server(command_line, server_addr, server_port)
    cache.store_value(name, response_from_server)

  # Returns the response from the cache, if the GET request has been previously requested
  # Otherwise, store the request in the cache and forward the request to the server
  elif (cmd == 'GET'):
    response_from_server = cache.get_value(name)
    if response_from_server == None:
      response_from_server = forward_command_to_server(command_line, server_addr, server_port)

  else:
    response_from_server = forward_command_to_server(command_line, server_addr, server_port)

  sock.send(response_from_server)


def main():

  # Listen on a specified port
  server_socket = library.create_server_socket(LISTENING_PORT)
  cache = library.KeyValueStore()

  # Accept incoming commands indefinitely
  while True:
    # Wait until a client connects and then get a socket that connects to the
    # client.


    # Establish the connection
    client_socket, (address, port) = library.connect_client_to_server(server_socket)
    print('Received connection from %s:%d' % (address, port))

    # Redirect traffic
    proxy_client_command(client_socket, SERVER_ADDRESS, SERVER_PORT,
                       cache)


    client_socket.close()


main()
