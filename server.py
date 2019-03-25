"""A server to store and retrieve key/value pairs using a socket interface.

Once it's running on your machine, you can test it by connecting to it
with a socket. "telent" is a unix program that allows unencrypted socket
communication from the command line. Localhost is the name of the IPv4 address
127.0.0.1. The second telnet command is the port.

% telnet localhost 7777
Trying ::1...
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
PUT Fred Office Hours are 12:30 on Tuesday.
Fred = Office Hours are 12:30 on Tuesday.
Connection closed by foreign host.

That command stores a string under the name "Fred". It can be retrieved in
a similar way:

% telnet localhost 7777
Trying ::1...
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
GET Fred
Office Hours are 12:30 on Tuesday.
Connection closed by foreign host.
"""

# This code uses Python 2.7. These imports make the 2.7 code feel a lot closer
# to Python 3. (They're also good changes to the language!)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# A few commands are used by both the server and the proxy server. Those
# functions are in library.py.
import library

import proxy


# The port that we accept connections on. (A.k.a. "listen" on.)
LISTENING_PORT = 7777


def put_command(name, text, database):
  """Handle the PUT command for a server.

  PUT's first argument is the name of the key to store the value under.
  All remaining arguments are stitched together and used as the value.

  Args:
    name: The name of the value to store.
    text: The value to store.
    database: A KeyValueStore containing key/value pairs.
  Returns:
    A human readable string describing the result. If there is an error,
    then the string describes the error.
  """
  # Store the value in the database.
  ##########################################
  #TODO: Implement PUT function
  ##########################################

    #
    #   args = command.strip().split(' ')
    # command = None
    # if args:
    #   command = args[0]
    # arg1 = None
    # if len(args) > 1:
    #   arg1 = args[1]
    # remainder = None
    # if len(args) > 2:
    #   remainder = ' '.join(args[2:])
    # return command, arg1, remainder

  #name = key
  #text = value
  #PUT stores the key and a specified value in the database.
  database.d[name] = text
  return name + "=" + text

def get_command(name, database):
  """Handle the GET command for a server.

  GET takes a single argument: the name of the key to look up.

  Args:
    name: The name of the value to retrieve.
    database: A KeyValueStore containing key/value pairs.
  Returns:
    A human readable string describing the result. If there is an error,
    then the string describes the error.
  """
  ##########################################
  #TODO: Implement GET function
  ##########################################

  #implementation with sending the request through the proxy server
  proxy_variables_accessed = proxy.main()
  if name in proxy_variables_accessed.cache:
    return proxy_variables_accessed.cache.get(name, "Value not found in cache. Please try again.")
  else:
    return database.d.get(name, "Value not found in database. Please try again.")


def dump_command(database):
  """Creates a function to handle the DUMP command for a server.

  DUMP takes no arguments. It always returns a CSV containing all keys.

  Args:
    database: A KeyValueStore containing key/value pairs.
  Returns:
    A human readable string describing the result. If there is an error,
    then the string describes the error.
  """

  ##########################################
  #TODO: Implement DUMP function
  ##########################################

  pass


def send_text(sock, text):
  """Sends the result over the socket along with a newline."""
  sock.send('%s\n' % text)


def main():

  # Store all key/value pairs in here.
  database = library.KeyValueStore()

  # The server socket that will listen on the specified port. If you don't
  # have permission to listen on the port, try a higher numbered port.
  server_sock = library.create_server_socket(LISTENING_PORT)



  # Handle commands indefinitely. Use ^C to exit the program.
  while True:

    # Wait until a client connects and then get a socket that connects to the
    # client.
    client_sock, (address, port) = library.connect_client_to_server(server_sock)
    print('Received connection from %s:%d' % (address, port))

    # Read a command.
    command_line = library.read_command(client_sock)
    command, name, text = library.parse_command(command_line)

    # Execute the command based on the first word in the command line.
    if command == 'PUT':
      result = put_command(name, text, database)
    elif command == 'GET':
      result = get_command(name, database)
    elif command == 'DUMP':
      result = dump_command(database)
    else:
      send_text(client_sock, 'Unknown command %s' % command)

    send_text(client_sock, result)



    # We're done with the client, so clean up the socket.

    #################################
    #TODO: Close socket's connection
    #################################
    server_sock.close()

main()
