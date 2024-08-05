import math
import time
import struct
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def generate_key_pair():
    private_key = RSA.generate(2048)
    public_key = private_key.public_key()

    return private_key, public_key


def sign(message, private_key):


    timestamp = struct.pack("f", time.time())
    hashed_message = SHA256.new(message)
    hashed_message.update(timestamp)
    signer = pkcs1_15.new(private_key)
    signature = signer.sign(hashed_message)

    return signature


def verify(message, signature, public_key):
    hashed_message = SHA256.new(message)
    verifier = pkcs1_15.new(public_key)
    try:
        verifier.verify(hashed_message, signature)
        return True
    except ValueError:
        return False


def return_proof_of_work(message, zero_score=10):
    pow = 0
    zeros = -1

    while True:
        zeros = 0
        digest_message = message + pow.to_bytes(pow.bit_length())
        hash = SHA256(digest_message).digest()

        tracker = 0
        while hash[tracker] == 0:
            tracker += 1

        zeros = 8 - (int(math.log(hash[tracker], 2)) + 1) + tracker*8

        if zeros >= zero_score:

            return pow, hash
        
        pow += 1