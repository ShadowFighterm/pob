"""
Core data models for the blockchain consensus system.

Classes:
- Transaction: Represents a blockchain transaction
- NodeState: Tracks node metrics and behavior
- Block: Represents a blockchain block
- Blockchain: Manages the chain of blocks
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from hashlib import sha256
from typing import List


@dataclass
class Transaction:
    """Represents a blockchain transaction."""
    sender: str
    receiver: str
    amount: int
    valid: bool = True
    origin_node_id: int | None = None
    tx_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert transaction to dictionary for serialization."""
        return {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "valid": self.valid,
            "origin_node_id": self.origin_node_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create transaction from dictionary."""
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            amount=int(data["amount"]),
            valid=bool(data.get("valid", True)),
            origin_node_id=data.get("origin_node_id"),
            tx_id=data.get("tx_id") or uuid.uuid4().hex,
            created_at=float(data.get("created_at", time.time())),
        )


@dataclass
class NodeState:
    """Tracks the state and metrics of a network node."""
    node_id: int
    stake: int = 0
    hash_power: int = 0
    port: int = 0
    behavior_score: float = 1.0
    valid_transactions: int = 0
    invalid_transactions: int = 0
    uptime: float = field(default_factory=lambda: __import__('random').uniform(0.7, 1.0))

    def update_behavior(self, transaction: Transaction) -> None:
        """Update behavior score based on transaction validity."""
        if transaction.valid:
            self.valid_transactions += 1
            self.behavior_score += 0.18
        else:
            self.invalid_transactions += 1
            self.behavior_score -= 0.28

    def consensus_score(self) -> float:
        """Calculate PoB consensus score (behavior + uptime)."""
        return round(self.behavior_score + (self.uptime * 0.35), 4)

    def to_dict(self) -> dict:
        """Convert node state to dictionary."""
        return {
            "node_id": self.node_id,
            "stake": self.stake,
            "hash_power": self.hash_power,
            "port": self.port,
            "behavior_score": self.behavior_score,
            "valid_transactions": self.valid_transactions,
            "invalid_transactions": self.invalid_transactions,
            "uptime": self.uptime,
        }


@dataclass
class Block:
    """Represents a blockchain block."""
    index: int
    validator_id: int
    transactions: List[Transaction]
    previous_hash: str
    timestamp: float = field(default_factory=time.time)
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    hash: str = ""

    def __post_init__(self) -> None:
        """Calculate hash upon creation."""
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block."""
        payload = json.dumps(
            {
                "index": self.index,
                "validator_id": self.validator_id,
                "transactions": [tx.to_dict() for tx in self.transactions],
                "previous_hash": self.previous_hash,
                "timestamp": self.timestamp,
                "nonce": self.nonce,
            },
            sort_keys=True,
        ).encode("utf-8")
        return sha256(payload).hexdigest()

    def to_dict(self) -> dict:
        """Convert block to dictionary for serialization."""
        return {
            "index": self.index,
            "validator_id": self.validator_id,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """Create block from dictionary."""
        block = cls(
            index=int(data["index"]),
            validator_id=int(data["validator_id"]),
            transactions=[Transaction.from_dict(tx) for tx in data.get("transactions", [])],
            previous_hash=data.get("previous_hash", "0" * 64),
            timestamp=float(data.get("timestamp", time.time())),
            nonce=data.get("nonce") or uuid.uuid4().hex,
        )
        block.hash = data.get("hash", block.calculate_hash())
        return block


class Blockchain:
    """Manages a blockchain (chain of blocks)."""
    
    def __init__(self) -> None:
        """Initialize an empty blockchain."""
        self.chain: List[Block] = []

    @property
    def latest_block(self) -> Block | None:
        """Get the most recent block in the chain."""
        return self.chain[-1] if self.chain else None

    def add_block(self, block: Block) -> bool:
        """
        Add a block to the chain with validation.
        
        Returns:
            True if block was added, False if validation failed.
        """
        if self.chain:
            if block.index != len(self.chain):
                return False
            if block.previous_hash != self.chain[-1].hash:
                return False
        elif block.index != 0:
            return False

        if any(existing.hash == block.hash for existing in self.chain):
            return False

        self.chain.append(block)
        return True
