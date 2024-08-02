import socket
import ssl
import signal
import select
import sys

from Crypto.PublicKey import RSA
from Crypto.Cipher import Salsa20

from constants import *
from encryptions import *
from blocks import *
from coms import *

# Once again, link to certfile and keyfile to enable tls transmission


"""
This code works as a basis of blockchain, but it has the following weaknesses:
    data is not encrypted during sending (Need to learn a bit about cryptography and secure communications)
    the transactions are being encrypted on the server side, using the client's private key. This is unsafe and should
        be conducted on the client end
    This could be set up to use real IP addresses (Although it makes little difference)
    This is an example of centralised servers, although blockchains tend to use decentralised architectures
"""

    
class Server:

    def __init__(self, port, backlog=5) -> Self:

        self.clients = 0
        self.transaction_number = 0
        self.client_map = {}
        # Output socket list for clients to write to
        self.write_clients = []

        # AF = Address family, SOCK_STREAM = stream type socket (Datagram being the other option)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # This allows you to reuse an address that is already in use. Comes in handy in the case that a server crashes
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.server = ssl.wrap_socket(self.server, server_side=True, keyfile="path/to/keyfile", certfile="path/to/certfile")

        # Binds to the given internet host
        # If you had used localhost, it would bind locally to the machine
        # Using '' makes the socket connect to any address the machine happens to have (So it becomes unspecified)
        # Then you just specify whichever port (3000 is commonly used in web dev, 80 is the specified internet port (Don't use it))
        # Always use port > 1024
        # 8000 corresponds to localhost
        # Note that client and server don't need to bind to the same port (And really shouldn't)
        self.server.bind((HOST, port))

        # Allows the server to accept connections. CONNECTIONS specifies the maximum number of connections that can be queued, not the number of connections in
        # the server
        self.server.listen(backlog)

        # Signal handler for sigkill, which closes all client connections and the server itself
        signal.signal(signal.SIGINT, self.sighandler)


    def sighandler(self, signum: int, frame: any) -> None:

        print("Encountered kill signal. Closing server")

        for output in self.write_clients:
            output.shutdown(socket.SHUT_RDWR)
            output.close()

        self.server.close()
        sys.exit()


    def serve(self) -> None:

        read_clients = [self.server]

        while True:

            try:
                read_ready, write_ready, error_ready = select.select(read_clients, self.write_clients, [], TIMEOUT)
            except select.error:
                print("Error in select function from the select package")
                break
            except socket.error:
                print("Error in select function from socket package")
                break

            for read_client in read_ready:

                if read_client == self.server:

                    # When there is a new client ready to join the server
                    # Connection represents the socket connecting to the client -> you can send and receive over that
                    # Address is the address that's bound to the socket on the other end (the client's address)
                    # Note that this is all the server does - just create socket connections to clients. It doesn't send or receive any data.
                    # This created 'client' socket is an equal beast to its true connected client socket -> this is p2p communication
                    client, address = self.server.accept()
                    print(f"Received connection from {address}")

                    self.clients += 1
                    read_clients.append(client)
                    self.write_clients.append(client)
                    
                else:

                    self.receive_message(read_client, read_ready, read_clients)

                    
    def receive_message(self, read_client: socket, read_ready: list[any], read_clients: list[any]) -> None:

        try:
            message, message_type, timestamp = receive_data(read_client)

            if message_type == HANDSHAKE:
                name, public_key = message.split(MESSAGE_DELIMITER)
                client_details = {"socket": read_client, "public_key": public_key}
                self.client_map[name] = client_details

                for client_name, dic in self.client_map.items():
                    if client_name != name:
                        message = MESSAGE_DELIMITER.join([name, public_key])
                        send_data(message, ADD_ADDRESS, self.client_map[client_name]["socket"])

                        message = MESSAGE_DELIMITER.join([client_name, self.client_map[client_name]["public_key"]])
                        send_data(client_name, ADD_ADDRESS, read_client)

            elif message_type == TRANSACTION:

                # This needs to be rejigged

                sender, recipient, amount = message.split(',')
                message += f",{str(self.transaction_number)}"
                encoded_transaction = sign(message, self.client_map[sender]["private_key"])
                transaction_entry = {"sender": sender, "recipient": recipient, "amount": amount, "encoded_transaction": encoded_transaction}
                self.transaction_buffer.append(transaction_entry)
                self.transaction_number += 1

            if message_type != RECEIVED:
                send_data(b"RECEIVED", RECEIVED, read_client)

        except socket.error as e:

            name = None

            for client_name, dic in self.client_map.items():
                if dic["client"] == read_client:
                    name = client_name

            if name is not None:

                print(f"Client {read_client} disconnected")
                self.clients -= 1
                read_client.shutdown(socket.SHUT_RDWR)
                read_client.close()
                read_clients.remove(read_client)
                self.write_clients.remove(read_client)
                read_ready.remove(read_client)

                for write_client in self.write_clients:

                    send_data(name, REMOVE_ADDRESS, write_client)



    # def check_transaction_buffer(self, write_ready: list[any]) -> None:
    #     # This has to be ported over to the client side once we have basic communications working

    #     if len(self.transaction_buffer) >= TRANSACTION_BUFFER_LIMIT:

    #         transactions = [entry["encoded_transaction"] for entry in self.transaction_buffer]
    #         message = TRANSACTION_DELIMITER.join(transactions)
    #         pow, hash = return_proof_of_work(message, NUM_ZEROS)
    #         block = Block(pow=pow.to_bytes(pow.bit_length()), message=message, next_hash=hash)
    #         self.blockchain.add_block(block)

    #         transcript = open("./transcript.txt", "a")
    #         for entry in self.transaction_buffer:
    #             transcript.write(f"{entry["sender"]}->{entry["recipient"]} ${entry["amount"]} Transaction ID: {entry["encoded_transaction"]}")

    #         block_chain_message = self.blockchain.to_text()

    #         for write_client in write_ready:
    #             client_name = None
    #             for name, dic in self.client_map.items():
    #                 if dic["socket"] == write_client:
    #                     client_name = name
    #             send_data(block_chain_message, BLOCK, self.client_map[client_name]["sequence_number"], write_client)
    #             self.client_map[client_name]["sequence_number"] += 1

    #         self.transaction_buffer = []



if __name__=="__main__":

    server = Server(port=5000)
    server.serve()