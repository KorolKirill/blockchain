from uuid import uuid4
import hashlib
import json
from textwrap import dedent
from time import time
from flask import Flask, jsonify, request

from blockchain import Blockchain


def lab2():
    blockchainTest = Blockchain()
    print(blockchainTest.last_block)
    blockchainTest.mineBlock()
    print(blockchainTest.last_block)
    blockchainTest.new_transaction("Kirill", "oleg", 3)
    blockchainTest.new_transaction("Kirill", "vanya", 5)
    blockchainTest.mineBlock()
    blockchainTest.new_transaction("Kirill", "oleg", 2)
    print(blockchainTest.last_block)
    print(blockchainTest.calculate_balances())

def lab1():
    blockchainTest = Blockchain()
    print(blockchainTest.last_block)
    print(blockchainTest.hash(blockchainTest.last_block))
    blockchainTest.new_transaction("kirill", "alex", 0.3)

    blockchainTest.new_block()
    print(blockchainTest.last_block)
    print(blockchainTest.hash(blockchainTest.last_block))


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain("kirill")


@app.route('/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values['nodes']
    if nodes is None:
        return {"message": "Error: Please supply a valid list of nodes", "m": nodes}, 300

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/refresh_mempool', methods=['POST'])
def refresh_mempool():
    values = request.get_json()

    mem_pool = values.get('mem_pool')
    if mem_pool is None:
        return "Error: wrong mem_pool", 400
    blockchain.mem_pool = mem_pool

    response = {
        'message': 'mem_pool was updated',
        'current_mem_pool': mem_pool,
    }
    return jsonify(response), 201


@app.route('/balances', methods=['GET'])
def balances():
    balances = blockchain.calculate_balances()
    response = {"balances": balances}
    return jsonify(response), 200

@app.route('/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    blockchain.mineBlock()
    response = {
        'message': 'Block was successfully mined',
        'last block': blockchain.last_block
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Перевірка того, що необхідні поля знаходяться серед POST-даних
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
        # Створення нової транзакції
    blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction was added to the mempool and waiting to be added to Block'}
    return jsonify(response), 201


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # lab1()
    # lab2()
    blockchain.mineBlock()
    print(blockchain.last_block)
    blockchain.new_transaction("kirill", "oleg", 3)
    blockchain.new_transaction("kirill", "vanya", 5)
    blockchain.new_transaction("kirill", "oleg", 2)
    print(blockchain.mem_pool)
    print(  blockchain.last_block)
    blockchain.mineBlock()
    print(blockchain.mem_pool)
    print(  blockchain.last_block)
    blockchain.mineBlock()
    print(  blockchain.last_block)
    print(  blockchain.calculate_balances())
   # app.run(host='0.0.0.0', port=5000)

