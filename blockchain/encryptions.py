import math
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


def generate_key_pair():
    private_key = ECC.generate(curve='p256')
    public_key = private_key.public_key()

    return private_key, public_key


def sign(message, private_key):

    hashed_message = SHA256.new(message)
    signer = DSS.new(private_key, 'fips-186-3')
    signature = signer.sign(hashed_message)

    return signature


def verify(message, signature, public_key):
    hashed_message = SHA256.new(message)
    verifier = DSS.new(public_key, 'fips-186-3')
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
        hash = sha256(digest_message).digest()

        tracker = 0
        while hash[tracker] == 0:
            tracker += 1

        zeros = 8 - (int(math.log(hash[tracker], 2)) + 1) + tracker*8

        if zeros >= zero_score:

            return pow, hash
        
        pow += 1