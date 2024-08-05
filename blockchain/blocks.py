from constants import *
from encryptions import *
from Crypto.Hash import SHA256
from merkle import *


class Block:

    def __init__(self, transactions: list[bytes]=[], pow: int=None, prev_hash: bytes=None, tree_size: int=8, root: bytes=None):
        self.transactions = transactions
        self.pow = pow
        self.prev_hash = prev_hash
        self.tree_size = tree_size
        self.tree = None
        self.root = root


    def set_prev_hash(self, hash):
        self.prev_hash = hash


    def finalise_block(self):
        self.create_tree()
        self.pow = return_proof_of_work(self.root)
    

    def create_tree(self) -> None:
        self.tree = merkleTree()
        self.tree.makeTreeFromArray(self.transactions)
        self.tree.calculateMerkleRoot()
        self.root = self.tree.getMerkleRoot()


    def add_transaction(self, transaction: bytes) -> bool:

        self.transactions.append(transaction)
        
        if len(self.transactions) == self.tree_size:
            self.finalise_block()
            return True
        
        return False


    def to_bytes(self) -> bytes:
        prev_hash = self.prev_hash
        if self.prev_hash == None:
            prev_hash = b"None"
        return BLOCK_DELIMITER.join([self.root, int.to_bytes(self.pow), prev_hash])
    


class Chain:

    def __init__(self) -> Self:
        self.chain = [Block()]


    def add_transaction(self, transaction: bytes) -> None:
        self.chain[-1].add_transaction(transaction)


    def add_block(self, block: Block) -> None:

        if len(self.chain) > 1:
            block.set_prev_hash(self.chain[-1].to_bytes())

        self.chain.append(block)


    def find_hash(self, hash: bytes) -> Block:
        for block in self.chain:
            root = block.to_bytes()
            if root == hash:
                return block
            
        raise ValueError("Could not find hash within Blockchain")
    

    def return_length(self) -> int:

        return len(self.chain)


    def to_bytes(self) -> bytes:

        chunks = []

        for block in self.chain:
            chunks.append(block.to_bytes())

        message = BLOCKCHAIN_DELIMITER.join(chunks)
        return message
    

def blockchain_from_bytes(message: bytes) -> Chain:

    chain = Chain()

    chunks = message.split(BLOCKCHAIN_DELIMITER)
    for chunk in chunks:
        block = block_from_bytes(chunk)
        chain.add_block(block)

    return chain


def block_from_bytes(chunk: bytes) -> Block:

    root, pow, prev_hash = chunk.split(BLOCK_DELIMITER)

    pow = int.from_bytes(pow)

    if prev_hash == b"None":
        prev_hash = None

    block = Block(prev_hash=prev_hash, pow=pow, root=root)
    return block
       