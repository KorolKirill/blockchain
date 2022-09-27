# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import blockchain;



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    blockchain = blockchain.Blockchain()
    print(blockchain.last_block)
    print(blockchain.hash(blockchain.last_block))
    blockchain.new_transaction("kirill", "alex", 0.3)

    proof = blockchain.proof_of_work(blockchain.last_block['proof'])
    blockchain.new_block(proof)
    print(blockchain.last_block)
    print(blockchain.hash(blockchain.last_block))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
