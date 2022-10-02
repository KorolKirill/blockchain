import hashlib
import json

from time import time
from uuid import uuid4


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='korol', proof=19112002)

    def proof_of_work(self, block):
        while self.valid_proof(block) is False:
            block['proof'] += 1
        return block

    def valid_proof(self, block):
        guess_hash = Blockchain.hash(block)
        return guess_hash[-2:] == "11"  # У якості підтвердження доказу - наявність в кінці хешу [місяць народження].

    def get_last_proof(self):
        if self.chain[-1] is None:
            return 0
        return self.chain[-1]['proof']

    def new_block(self, proof=None, previous_hash=None):
        if proof is None:
            proof = self.get_last_proof()

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        block = self.proof_of_work(block)

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
