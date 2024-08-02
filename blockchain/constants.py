import socket
import time
import struct
from typing import Self

# Specifies the number of connections that can be backlogged by the server prior to accept()
# Note that this does not specify the number of clients within the server
CONNECTIONS = 5

# Specifies the length of send and recv messages
HEADER_LENGTH = 4
TOTAL_HEADER_LENGTH = 1024

# Maximum size of message allowed to be transmitted at once
BUFFER_SIZE = 1024

# Maximum number of transactions to be stored within the buffer before it's emptied into a chain
TRANSACTION_BUFFER_LIMIT = 5

# Specifies the number of zeros that need to be present at the start of the proof of work hash
NUM_ZEROS = 10

# Specifies the length of time to wait prior to timing the client or server out
TIMEOUT = 1

# Specifies the host we want to connect to
HOST = socket.gethostname()

# Specify the waiting time between sending messages during automated testing
TEST_INTERVAL = 2

# Delimiter for sending messages over the client / server architecture
MESSAGE_DELIMITER = b"    "

# Scrap all this. It's getting pointlessly confusing
BLOCKCHAIN_DELIMITER = b"\n\n\n\n"
BLOCK_DELIMITER = b"\t\t\t\t"

# Specify values for message type
HANDSHAKE = 1
TRANSACTION = 2
BLOCK = 3
ADD_ADDRESS = 4
REMOVE_ADDRESS = 5
RECEIVED = 6
