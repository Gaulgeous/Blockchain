class Block:

    def __init__(self, prev_hash=None, message=None, pow=None, next_hash=None):
        self.prev_hash = prev_hash
        self.message = message
        self.pow = pow
        self.next_hash = next_hash
        self.prev = None
        self.next = None


    def set_pow(self, pow):
        self.pow = pow


    def set_prev_hash(self, prev_hash):
        self.prev_hash = prev_hash


    def set_message(self, message):
        self.message = message


    def get_message(self):
        return self.message
    

    def get_pow(self):
        return self.pow
    

    def get_prev_hash(self):
        return self.prev_hash
    

    def get_next_hash(self):
        return self.next_hash
    

    def set_next(self, next):
        self.next = next


    def get_next(self):
        return self.next
    

    def set_prev(self, prev):
        self.prev = prev


    def get_prev(self):
        return self.prev
    

class Chain:

    def __init__(self):
        self.head = None


    def find_hash(self, hash):
        next = self.head
        while next.get_next() is not None:
            compare_hash = next.get_pow()
            if compare_hash == hash:
                return next
            next = next.get_next()
        raise ValueError("Could not find hash within Blockchain")


    def add_block(self, block):

        # Set the head if it's an empty blockchain
        if self.head is None:
            self.head = block
            block.set_prev(None)

        # Keep iterating through the blockchain until you can add the next spot in
        else:
            next = self.head
            while next.get_next() is not None:
                next = next.get_next()

            block.set_prev_hash(next.get_next_hash())
            block.set_prev(next)
            next.set_next(block)


if __name__=="__main__":
    chain = Chain()
    block_1 = Block()
    block_2 = Block()
    block_3 = Block()

    block_1.set_prev_hash("a")
    block_2.set_prev_hash("b")
    block_3.set_prev_hash("c")

    chain.add_block(block_1)
    chain.add_block(block_2)
    chain.add_block(block_3)

    block = chain.find_hash('b')
    block = chain.find_hash('c')
    block = chain.find_hash('d')
       