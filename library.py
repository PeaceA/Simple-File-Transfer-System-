"""A set of libraries that are useful to both the proxy and regular servers."""

# This code uses Python 2.7. These imports make the 2.7 code feel a lot closer
# to Python 3. (They're also good changes to the language!)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# THe Python socket API is based closely on the Berkeley sockets API which
# was originally written for the C programming language.
#
# https://en.wikipedia.org/wiki/Berkeley_sockets
#
# The API is more flexible than you need, and it does some quirky things to
# provide that flexibility. I recommend tutorials instead of complete
# descriptions because those can skip the archaic bits. (The API was released
# more than 35 years ago!)
import socket

import time

# Read this many bytes at a time of a command. Each socket holds a buffer of
# data that comes in. If the buffer fills up before you can read it then TCP
# will slow down transmission so you can keep up. We expect that most commands
# will be shorter than this.
COMMAND_BUFFER_SIZE = 256
HOST = '127.0.0.1'  # localhost address

def CreateServerSocket(port):
    """Creates a socket that listens on a specified port.

    Args:
      port: int from 0 to 2^16. Low numbered ports have defined purposes. Almost
          all predefined ports represent insecure protocols that have died out.
    Returns:
      An socket that implements TCP/IP.
    """

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST,port))
    return server_sock




def ConnectClientToServer(server_sock):
    """Connects client to server.


    Returns:
      A new socket representing the client connection, as well as a tuple holding
      the address of the client
    """

    # Wait until a client connects and then get a socket that connects to the
    # client.

    server_sock.listen()
    return server_sock.accept()


def CreateClientSocket(server_addr, port):
    """Creates a socket that connects to a port on a server."""

    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.connect((server_addr, port))
    return transfer_socket


def ReadCommand(sock):
    """Read a single command from a socket. The command must end in newline."""

    command_line = sock.recv(COMMAND_BUFFER_SIZE).decode() # ~~~adjust for commands bigger than buffer
    return command_line

def ParseCommand(command):
    """Parses a command and returns the command name, first arg, and remainder.

    All commands are of the form:
        COMMAND arg1 remaining text is called remainder
    Spaces separate the sections, but the remainder can contain additional spaces.
    The returned values are strings if the values are present or `None`. Trailing
    whitespace is removed.

    Args:
      command: string command.
    Returns:
      command, arg1, remainder. Each of these can be None.
    """

    args = command.strip().split(' ')
    command = None
    if args:
        command = args[0]
    arg1 = None
    if len(args) > 1:
        arg1 = args[1]
    remainder = None
    if len(args) > 2:
        remainder = ' '.join(args[2:])
    return command, arg1, remainder

class ValTimeStore(object):
    """A value-timestamp tuple."""

    def __init__(self,value):
        """Declares default, timestamped item"""
        self.value = value;
        self.timestamp = time.time();
        return


class KeyValueStore(object):
    """A dictionary of strings keyed by strings.

    The values can time out once they get sufficiently old. Otherwise, this
    acts much like a dictionary.
    """

    def __init__(self):
        """Declares default, empty state."""

        self.key_value_dict = {}
        self.has_been_set = False
        return

    def GetValue(self, key, max_age_in_sec=None):
        """Gets a cached value or `None`.

        Values older than `max_age_in_sec` seconds are not returned.

        Args:
          key: string. The name of the key to get.
          max_age_in_sec: float. Maximum time since the value was placed in the
            KeyValueStore. If not specified then values do not time out.
        Returns:
          None or the value.
        """
        # Check if we've ever put something in the cache.
        if self.has_been_set:
            if max_age_in_sec is None:
                if key in self.key_value_dict :
                    return (self.key_value_dict[key]).value
                else:
                    return None
            else:
                cur_time = time.time()
                if key in self.key_value_dict.keys():
                    candidate_pair = self.key_value_dict[key]
                    if (cur_time - candidate_pair.timestamp) <= max_age_in_sec:
                        return (self.key_value_dict[key]).value
                    else:
                        return None
                else:
                    return None
        else:
            return None

    def StoreValue(self, key, value):
        """Stores a value under a specific key.

        Args:
          key: string. The name of the value to store.
          value: string. A value to store.
        """
        if not(key is None) and not(value is None):
            self.key_value_dict[key] = ValTimeStore(value)
            self.has_been_set = True
            return 0  # no issues
        else:
            return 1  # invalid parameters

    def Keys(self):
        """Returns a list of all keys in the datastore."""

        return self.key_value_dict.keys()






