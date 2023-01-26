import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:

    def __init__(self):
        self.chain = []
        self.createBlock(proof = 1, previousHash = '0')

    def createBlock(self, proof, previousHash):
        block = {
                "index": len(self.chain) + 1,
                "timestamp": str(datetime.datetime.now()),
                "proof": proof,
                "previousHash": previousHash
        }
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        newProof = 1
        checkProof = False
        while checkProof is False:
            hashOperation = self.chainFormula(previousProof, newProof)
            if self.isHashValidForChain(hashOperation) is True:
                checkProof = True
            else:
                newProof += 1
        return newProof

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, skipkeys=True).encode()).hexdigest()

    def chainFormula(self, previousProof, proof):
        return hashlib.sha256(str(proof - previousProof).encode()).hexdigest()

    def isHashValidForChain(self, hash):
        return hash[:5] == "01021"

    def isChainValid(self):
        previousBlock = self.chain[0]
        blockIndex = 1
        while blockIndex < len(self.chain):
            block = self.chain[blockIndex]
            if block['previousHash'] != self.hash(previousBlock):
                return False
            hashOperation = self.chainFormula(previousBlock['proof'], block['proof'])
            if self.isHashValidForChain(hashOperation) is False:
                return False
            previousBlock = block
            blockIndex += 1
        return True


blockchain = Blockchain()

app = Flask(__name__)

@app.route('/mine', methods = ['GET'])
def mine():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    block = blockchain.createBlock(proof, previousHash)
    response = {
                "index": block["index"],
                "timestamp": block["timestamp"],
                "proof": block["proof"],
                "previousHash": block["previousHash"]
    }
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def chain():
    response = {
            "chain" : blockchain.chain,
            "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/valid', methods = ['GET'])
def valid():
    isValid = blockchain.isChainValid()
    if isValid:
        response = {"message": "The chain is valid"}
    else:
        response = {"message": "The chain is not valid"}
    return jsonify(response), 200

app.run("127.0.0.1", 5000)