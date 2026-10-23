import hashlib
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from . import config
from . import database


@dataclass
class Block:
    index: int
    timestamp: str
    txn_id: str
    fraud_score: float
    explanation_hash: str
    prev_hash: str
    current_hash: str
    signature: str


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.private_key = None
        self.public_key = None
        self._load_or_create_keys()
        self.load_chain_from_db()

    @staticmethod
    def compute_hash(index: int, timestamp: str, txn_id: str,
                      fraud_score: float, explanation_hash: str, prev_hash: str) -> str:
        block_string = f"{index}{timestamp}{txn_id}{fraud_score}{explanation_hash}{prev_hash}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def _load_or_create_keys(self):
        os.makedirs(config.KEY_DIR, exist_ok=True)
        if os.path.exists(config.PRIVATE_KEY_PATH) and os.path.exists(config.PUBLIC_KEY_PATH):
            with open(config.PRIVATE_KEY_PATH, 'rb') as f:
                self.private_key = RSA.import_key(f.read())
            with open(config.PUBLIC_KEY_PATH, 'rb') as f:
                self.public_key = RSA.import_key(f.read())
            return

        key = RSA.generate(2048)
        self.private_key = key
        self.public_key = key.publickey()
        with open(config.PRIVATE_KEY_PATH, 'wb') as f:
            f.write(key.export_key(format='PEM'))
        with open(config.PUBLIC_KEY_PATH, 'wb') as f:
            f.write(self.public_key.export_key(format='PEM'))

    def _sign_hash(self, value: str) -> str:
        digest = SHA256.new(value.encode('utf-8'))
        signature = pkcs1_15.new(self.private_key).sign(digest)
        return signature.hex()

    def _verify_signature(self, value: str, signature_hex: str) -> bool:
        if not signature_hex:
            return False
        try:
            digest = SHA256.new(value.encode('utf-8'))
            signature = bytes.fromhex(signature_hex)
            pkcs1_15.new(self.public_key).verify(digest, signature)
            return True
        except (ValueError, TypeError):
            return False

    def load_chain_from_db(self):
        rows = database.fetch_blocks(limit=100000)
        self.chain = []
        for row in rows:
            b = Block(
                index=row[0],
                txn_id=row[1],
                timestamp=row[2],
                fraud_score=row[3],
                explanation_hash=row[4],
                prev_hash=row[5],
                current_hash=row[6],
                signature=row[7] if len(row) > 7 else "",
            )
            self.chain.append(b)
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        timestamp = datetime.utcnow().isoformat()
        genesis_hash = self.compute_hash(0, timestamp, 'GENESIS', 0.0, 'GENESIS', '0')
        signature = self._sign_hash(genesis_hash)
        genesis_block = Block(
            index=0,
            timestamp=timestamp,
            txn_id='GENESIS',
            fraud_score=0.0,
            explanation_hash='GENESIS',
            prev_hash='0',
            current_hash=genesis_hash,
            signature=signature,
        )
        self.chain.append(genesis_block)
        database.insert_block(
            block_index=genesis_block.index,
            txn_id=genesis_block.txn_id,
            timestamp=genesis_block.timestamp,
            fraud_score=genesis_block.fraud_score,
            explanation_hash=genesis_block.explanation_hash,
            prev_hash=genesis_block.prev_hash,
            current_hash=genesis_block.current_hash,
            signature=genesis_block.signature,
        )

    def add_block(self, txn_id: str, fraud_score: float, explanation: str) -> Block:
        prev_block = self.chain[-1]
        explanation_hash = hashlib.sha256(explanation.encode('utf-8')).hexdigest()
        index = prev_block.index + 1
        timestamp = datetime.utcnow().isoformat()
        current_hash = self.compute_hash(
            index=index,
            timestamp=timestamp,
            txn_id=txn_id,
            fraud_score=fraud_score,
            explanation_hash=explanation_hash,
            prev_hash=prev_block.current_hash,
        )
        signature = self._sign_hash(current_hash)
        new_block = Block(
            index=index,
            timestamp=timestamp,
            txn_id=txn_id,
            fraud_score=fraud_score,
            explanation_hash=explanation_hash,
            prev_hash=prev_block.current_hash,
            current_hash=current_hash,
            signature=signature,
        )
        self.chain.append(new_block)
        database.insert_block(
            block_index=new_block.index,
            txn_id=new_block.txn_id,
            timestamp=new_block.timestamp,
            fraud_score=new_block.fraud_score,
            explanation_hash=new_block.explanation_hash,
            prev_hash=new_block.prev_hash,
            current_hash=new_block.current_hash,
            signature=new_block.signature,
        )
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            recalculated_hash = self.compute_hash(
                curr.index, curr.timestamp, curr.txn_id,
                curr.fraud_score, curr.explanation_hash, curr.prev_hash,
            )
            if curr.current_hash != recalculated_hash:
                return False
            if curr.prev_hash != prev.current_hash:
                return False
            if not self._verify_signature(curr.current_hash, curr.signature):
                return False
        return True

    def export_ledger(self):
        data = [asdict(b) for b in self.chain]
        with open(config.LEDGER_EXPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
