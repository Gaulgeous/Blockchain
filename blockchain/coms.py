from constants import *
import select
import errno


def send_data(message: bytes, message_type: int, sock: socket) -> None:
    timestamp = struct.pack("f", time.time())
    message_length = len(message)
    message_length = message_length.to_bytes(message_length.bit_length())
    message_type = message_type.to_bytes(1)

    header = MESSAGE_DELIMITER.join([message_length, message_type, timestamp])

    while len(header) < TOTAL_HEADER_LENGTH:
        header = b"".join([b" ", header])

    non_blocking_send(header, sock)
    non_blocking_send(message, sock)


def non_blocking_send(message: bytes, sock: socket) -> None:

        message_length = len(message)
        total_sent = 0
        while total_sent < message_length:
            try:
                sent = sock.send(message)
                total_sent += sent

                if total_sent < message_length:
                    message = message[sent]

            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                print(f'Blocking with {len(message)} remaining')
                select.select([], [sock], [])

            except IndexError as e:
                print(f"Remaining message {len(message)} Sent {sent} Total Sent {total_sent} Message Length {message_length}")


def receive_data(sock: socket) -> list[bytes | int]:

    # First, receive the length of the following message
    # This is going to be an issue when receiving blockchains - make special use case
    # Probs easiest to rewrite this entire thing to accommodate new architecture. Handle once you figure out server side
    message = sock.recv(TOTAL_HEADER_LENGTH)
    message = message.strip()

    message_length, message_type, timestamp = message.split(MESSAGE_DELIMITER)

    message_length = int.from_bytes(message_length)
    message_type = int.from_bytes(message_type)
    timestamp = struct.unpack('f', timestamp)[0]

    chunks = []
    characters_received = 0

    while characters_received < message_length:
        chunk = sock.recv(min(message_length-characters_received, BUFFER_SIZE))

        if not chunk:
            raise socket.error

        chunks.append(chunk)
        characters_received += len(chunk)

    data = b"".join(chunks)
    message = data.strip()

    return message, message_type, timestamp
