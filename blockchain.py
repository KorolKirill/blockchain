import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify
from urllib.parse import urlparse
import requests


class Blockchain(object):

    def __init__(self, miner):
        self.chain = []
        self.mem_pool = []
        self.nodes = set()
        self.miner = miner
        # genesis block
        self.mineBlock(previous_hash='korol', proof=19112002)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def calculate_balances(self):
        balances = {}
        for i in range(len(self.chain)):
            for o in range(len(self.chain[i]["transactions"])):
                trxn = self.chain[i]["transactions"][o]
                if balances.get(trxn["recipient"]) is None:
                    balances[trxn["recipient"]] = trxn["amount"]
                else:
                    balances[trxn["recipient"]] += trxn["amount"]

                if trxn["sender"] != "0":
                    balances[trxn["sender"]] -= trxn["amount"]
        return balances

    def new_transaction(self, sender, recipient, amount):
        self.mem_pool.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        self.share_mempool()

    def share_mempool(self):
        neighbours = self.nodes
        data = {
            'mem_pool': self.mem_pool
        }
        for node in neighbours:
            response = requests.post(f'http://{node}/refresh_mempool', json=data)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if not self.valid_proof(last_block):
                return False

            if block['previous_hash'] != self.hash(last_block):
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    def proof_of_work(self, block):
        while self.valid_proof(block) is False:
            block['proof'] += 1
        return block

    def valid_proof(self, block):
        # У якості підтвердження доказу - наявність в кінці хешу [місяць народження].
        return Blockchain.hash(block)[-2:] == "11"

    def get_last_proof(self):
        if len(self.chain) > 0:
            return self.chain[-1]['proof']
        return 0


    def mineBlock(self, proof=None, previous_hash=None):
        minerAddress = self.miner
        # я Coinbase-транзакції
        minerReward = 19
        self.resolve_conflicts()
        coinbase = {
            'sender': '0',
            'recipient': minerAddress,
            'amount': minerReward,
        }
        self.new_block(coinbaseTRXN=coinbase, proof=proof, previous_hash=previous_hash)

    def new_block(self, coinbaseTRXN, proof=None, previous_hash=None):
        if proof is None:
            proof = self.get_last_proof()

        trxn_passed = []
        trxn_passed.append(coinbaseTRXN) # adds coinbase
        transaction_limit_per_block = 5
        balances = self.calculate_balances()
        counter = 0
        while counter < transaction_limit_per_block and len(self.mem_pool) > 0:
            upcoming_trxn = self.mem_pool.pop(0)
            if balances.get(upcoming_trxn['sender']) is not None:
                if balances[upcoming_trxn['sender']] > upcoming_trxn['amount']:
                    balances[upcoming_trxn['sender']] -= upcoming_trxn['amount']
                    if balances.get(upcoming_trxn["recipient"]) is None:
                        balances[upcoming_trxn["recipient"]] = upcoming_trxn["amount"]
                    else:
                        balances[upcoming_trxn["recipient"]] += upcoming_trxn["amount"]
                    trxn_passed.append(upcoming_trxn)
                    counter += 1
                    continue

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': trxn_passed,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        block = self.proof_of_work(block)
        self.share_mempool()
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
