import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        
        self.createBlock(proof = 1, previousHash = '0')

    def createBlock(self, proof, previousHash):
        block = {
                "index": len(self.chain) + 1,
                "timestamp": str(datetime.datetime.now()),
                "proof": proof,
                "transactions": self.transactions,
                "previousHash": previousHash
        }
        self.chain.append(block)
        self.transactions = []
        self.nodes = set()
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

    def isChainValid(self, chain):
        previousBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['previousHash'] != self.hash(previousBlock):
                return False
            hashOperation = self.chainFormula(previousBlock['proof'], block['proof'])
            if self.isHashValidForChain(hashOperation) is False:
                return False
            previousBlock = block
            blockIndex += 1
        return True
    
    def addTransaction(self, sender, recipient, amount):
        self.transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })
        prevBlock = self.getPreviousBlock()
        return prevBlock["index"] + 1
    
    def addNode(self, address):
        parsed = urlparse(address)
        self.nodes.add(parsed.netloc)
        
    def longestChain(self):
        maxLen = len(self.chain)
        newChain = None
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                json = response.json()
                if(json['length'] > maxLen and self.isChainValid(json['chain'])):
                    newChain = json['chain']
                    maxLen = json['length']
        if newChain:
            self.chain = newChain
            return True
        return False

nodeAddress = str(uuid4()).replace("-", "");

blockchain = Blockchain()

app = Flask(__name__)

@app.route('/mine', methods = ['GET'])
def mine():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    blockchain.addTransaction(sender=nodeAddress, recipient="cryptominer", amount=1)
    block = blockchain.createBlock(proof, previousHash)
    response = {
                "index": block["index"],
                "timestamp": block["timestamp"],
                "proof": block["proof"],
                "transactions": block["transactions"],
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
    isValid = blockchain.isChainValid(blockchain.chain)
    if isValid:
        response = {"message": "The chain is valid"}
    else:
        response = {"message": "The chain is not valid"}
    return jsonify(response), 200

@app.route('/transaction', methods = ['POST'])
def transaction():
    json = request.get_json()
    tKeys = ["sender", "receiver", "amount"]

    #@todo
    if not all(key in json for key in tKeys):
        return jsonify({"message": "Not all required keys are present"}), 400
    index = blockchain.addTransaction(sender=json["sender"], recipient=json["recipient"], amount=json["amount"])
    return jsonify({"message": f"Transaction is going to be added in {index}"}), 201

@app.route('/connect', methods = ['POST'])
def connect():
    json = request.get_json()
    nodes = json.get("nodes")
    if nodes is None:
        return return jsonify({"message": "No node found"}), 400
    
    for node in nodes:
        blockchain.addNode(node)
    return jsonify({"message": f"Nodes added", "total": list(blockchain.nodes)}), 201

@app.route('/replace', methods = ['GET'])
def replace():
    replaced = blockchain.longestChain()
    if replaced:
        response = {"message": "The chain has been replaced}
    else:
        response = {"message": "The chain has not been replaced"}
    return jsonify(response), 200


app.run("127.0.0.1", 5000)