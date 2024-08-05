import socket
import ssl
import sys
import time
from random import randint, choice

from constants import *
from encryptions import *
from coms import *
from blocks import *

### How do we communicate over TLS to make it secure?
# Specify paths to keyfile and certfile, then we're in business



class Client:

    def __init__(self, port: int, name: str, wallet: int) -> Self:
        self.port = port
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.client = ssl.wrap_socket(self.client, keyfile="path/to/keyfile", certfile="path/to/certfile")
        self.address_book = {}
        self.chains = [Chain()]
        self.name = name
        self.wallet = wallet
        self.private_key, self.public_key = generate_key_pair()

        self.socket.connect((HOST, port))
        self.send_handshake()
        self.mainloop()


    def mainloop(self) -> None:

        start = time.time()

        while True:
            now = time.time()

            try:
                read_ready, write_ready, error_ready = select.select([self.socket], [self.socket], [])
            except select.error:
                print("Error in select function from the select package")
                break
            except socket.error:
                print("Error in select function from socket package")
                break

            if len(read_ready) > 0:
                self.receive_message()

            if now - start >= TEST_INTERVAL and len(write_ready) > 0 and len(self.address_book) > 0:
                recipient, _ = choice(list(self.address_book.items()))
                amount = min(self.wallet, randint(1, 100))
                self.send_transaction(recipient, amount)
                start = now


    def update_chain(self, chain: Chain) -> None:

        new_length = chain.return_length()
        existing_length = self.chains[0].return_length()

        if new_length > existing_length:
            self.chains = [chain]
        elif new_length == existing_length:
            self.chains.append(chain)


    def add_address(self, message: bytes) -> None:

        name, public_key = message.split(MESSAGE_DELIMITER)
        if name not in self.address_book:
            self.address_book[name] = public_key


    def remove_address(self, address: str) -> None:

        if address in self.address_book:
            self.address_book.pop(address)


    def send_transaction(self, recipient: bytes, amount: int) -> None:

            self.wallet -= amount
            message = MESSAGE_DELIMITER.join([self.name.encode('utf-8'), recipient, int.to_bytes(amount)])
            signature = sign(message, self.private_key)

            message = MESSAGE_DELIMITER.join([self.name.encode('utf-8'), signature])

            send_data(message, TRANSACTION, self.socket)

            print("Sent transaction")


    def receive_message(self) -> None:

        message, message_type, sequence_number = receive_data(self.socket)

        if message_type == BLOCK:
            blockchain = blockchain_from_bytes(message)
            self.update_chain(blockchain)
        elif message_type == ADD_ADDRESS:
            self.add_address(message)
        elif message_type == REMOVE_ADDRESS:
            self.remove_address(message)
        elif message_type == RECEIVED:
            print("Message sent and received successfully")
        elif message_type == TRANSACTION:
            full = self.chains[0].add_transaction(message)
            if full:
                blockchain = self.chains[0].to_bytes()
                message = MESSAGE_DELIMITER.join([self.name.encode('utf-8'), blockchain])
                send_data(message, BLOCK, self.socket)


        if message_type != RECEIVED:
            send_data(b"RECEIVED", RECEIVED, self.socket)


    def send_handshake(self) -> None:
        
        key = self.public_key.export_key(format="DER")
        message = MESSAGE_DELIMITER.join([self.name.encode('utf-8'), key])
        send_data(message, HANDSHAKE, self.socket)

   
if __name__=="__main__":

    arguments = sys.argv
    name = arguments[1]

    client = Client(port=5000, name=name, wallet=randint(100, 1000))
    