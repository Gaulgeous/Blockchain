from BlockchainClass import *
from Encryptions import *
from User import *

from random import randint
import time

users = 4
time_interval = 10
message_length = 5
zero_score = 10

class Server:

    def __init__(self):
        self.chain = Chain()
        self.users = []
        self.message = []


    def add_user(self, user):
        self.users.append(user)


    def return_chain(self):
        return self.chain
    

    def print_user_data(self, username):
        for user in self.users:
            if user.get_name() == username:
                print(user.get_details())


    def get_user(self, username):
        for user in self.users:
            if user.get_name() == username:
                return self.user
            

    def get_message_index(self):
        return len(self.message)
    

    def add_message(self, message):
        self.message.append(message)
        if len(self.message) >= message_length:
            message_string = " ".join(self.message)
            pow, hash = return_proof_of_work(message_string, zero_score)
            block = Block(prev_hash=None, message=message_string, pow=pow, next_hash=hash)
            self.chain.add_block(block)
            self.message = []


if __name__=="__main__":
    server = Server()

    start = time.time()

    for i in range(users):
        user = User(randint(100, 1000), f"User_{i}", server.return_chain())
        server.add_user(user)
        # server.print_user_data("User_" + str(i))

    while True:
        now = time.time()
        if now - start >= time_interval:
            sender = server.get_user(f"User_{randint(0, users-1)}")
            receiver = server.get_user(f"User_{randint(0, users-1)}")
            amount = randint(1, 100)

            amount, signature = sender.send_money(amount, receiver, server.get_message_index())
            receiver.receive_money(amount)

        start = now