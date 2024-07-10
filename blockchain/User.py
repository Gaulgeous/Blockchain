from BlockchainClass import *
from Encryptions import *

class User:

    def __init__(self, cash, name, chain=None):
        self.cash = cash
        self.public_key, self.private_key = generate_keys()
        self.chain = chain
        self.name = name


    def get_public_key(self):
        return self.public_key


    def send_money(self, amount, receiver, index):
        if self.cash >= amount:
            self.cash -= amount
        else:
            amount = self.cash
            self.cash = 0
        
        message = f"{self.name} sent {amount} to {receiver} at index {index}"
        signature = sign(message, self.private_key)
        return amount, signature
        

    def receive_money(self, amount):
        self.cash += amount


    def add_chain(self, block):
        self.chain.add_block(block)


    def get_name(self):
        return self.name
    

    def get_details(self):
        print(f"name: {self.name}")
        print(f"cash: {self.cash}")
        print(f"public_key: {self.public_key}")
        print(f"private_key: {self.private_key}")
        print()