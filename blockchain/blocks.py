from constants import *


class Block:

    def __init__(self, prev_hash: bytes=None, message: bytes=None, pow: bytes=None, next_hash: bytes=None) -> Self:
        self.prev_hash = prev_hash
        self.message = message
        self.pow = pow
        self.next_hash = next_hash
        self.prev = None
        self.next = None


    def print_values(self) -> None:
        print(f"prev_hash {self.prev_hash}")
        print(f"message {self.message}")
        print(f"pow {self.pow}")
        print(f"next_hash {self.next_hash}")
        print()


    def set_pow(self, pow: bytes) -> None:
        self.pow = pow


    def set_prev_hash(self, prev_hash: bytes) -> None:
        self.prev_hash = prev_hash


    def set_message(self, message: bytes) -> None:
        self.message = message


    def get_message(self) -> bytes:
        return self.message
    

    def get_pow(self) -> bytes:
        return self.pow
    

    def get_prev_hash(self) -> bytes:
        return self.prev_hash
    

    def get_next_hash(self) -> bytes:
        return self.next_hash
    

    def set_next(self, next: Self) -> None:
        self.next = next


    def get_next(self) -> Self:
        return self.next
    

    def set_prev(self, prev: Self) -> None:
        self.prev = prev


    def get_prev(self) -> Self:
        return self.prev
    

    def to_text(self) -> bytes:

        prev_hash = "none".encode('utf-8')
        next_hash = "none".encode('utf-8')

        if self.prev_hash is not None:
            prev_hash = prev_hash

        if self.next_hash is not None:
            next_hash = next_hash

        text = BLOCK_DELIMITER.join([prev_hash, self.message, self.pow, next_hash])
        return text



class Chain:

    def __init__(self) -> Self:
        self.head = None


    def find_hash(self, hash: bytes) -> Block:
        next = self.head
        while next.get_next() is not None:
            compare_hash = next.get_pow()
            if compare_hash == hash:
                return next
            next = next.get_next()
        raise ValueError("Could not find hash within Blockchain")


    def add_block(self, block: Block) -> None:

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


    def print_chain(self) -> None:
        next = self.head

        while next.get_next() is not None:
            next.print_values()
            next = next.get_next()

        next.print_values()


    def return_length(self) -> int:

        links = 0

        if self.head is not None:

            links = 1
            head = self.head
            while head.get_next() is not None:
                head = head.get_next()
                links += 1

        return links
    

    def to_text(self) -> bytes:

        head = self.head
        chunks = []

        chunks.append(head.to_text())

        while head.get_next() is not None:
            head = head.get_next()
            chunks.append(head.to_text())

        message = BLOCKCHAIN_DELIMITER.join(chunks)
        return message
    


def blockchain_from_text(message: bytes) -> Chain:

    chain = Chain()

    chunks = message.split(BLOCKCHAIN_DELIMITER)
    for chunk in chunks:
        block = block_from_text(chunk)
        chain.add_block(block)

    return chain


def block_from_text(chunk: bytes) -> Block:

    prev_hash, message, powork, next_hash = chunk.split(BLOCK_DELIMITER)

    if prev_hash == "none":
        prev_hash = None

    if next_hash == "none":
        next_hash = None

    block = Block(prev_hash=prev_hash, message=message, pow=powork, next_hash=next_hash)
    return block
       