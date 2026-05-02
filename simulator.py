"""
Consensus algorithm simulator for offline comparison.

Classes:
- ConsensusSimulator: Simulates a consensus algorithm in a controlled environment
"""

from __future__ import annotations

import random
import time
from typing import Callable

from models import Transaction, NodeState, Block
from metrics import ConsensusMetrics


class ConsensusSimulator:
    """
    Simulates a consensus algorithm in a controlled environment.
    
    Useful for comparing different algorithms under identical conditions.
    """
    
    def __init__(
        self,
        num_nodes: int,
        consensus_fn: Callable,
        consensus_name: str,
        duration: float,
        tx_rate: float,
    ) -> None:
        """
        Initialize the simulator.
        
        Args:
            num_nodes: Number of nodes in the simulation
            consensus_fn: Function to select validator
            consensus_name: Name of consensus algorithm
            duration: Simulation duration in seconds
            tx_rate: Transactions per second
        """
        self.num_nodes = num_nodes
        self.consensus_fn = consensus_fn
        self.consensus_name = consensus_name
        self.duration = duration
        self.tx_rate = tx_rate
        self.metrics = ConsensusMetrics(consensus_name)

        # Create nodes with varied stake and hash power
        self.nodes = [
            NodeState(node_id=0, stake=10, hash_power=50),
            NodeState(node_id=1, stake=50, hash_power=10),
            NodeState(node_id=2, stake=20, hash_power=20),
            NodeState(node_id=3, stake=100, hash_power=5),
            NodeState(node_id=4, stake=5, hash_power=100),
        ]
        if num_nodes < 5:
            self.nodes = self.nodes[:num_nodes]

    def run(self) -> None:
        """Run the simulation for the specified duration."""
        start_time = time.time()
        block_count = 0

        print(f"Starting {self.consensus_name.upper()} simulation for {self.duration}s...")

        while time.time() - start_time < self.duration:
            # Generate transactions
            num_txs = random.randint(2, 6)
            for _ in range(num_txs):
                sender_id = random.randint(0, self.num_nodes - 1)
                receiver_id = random.choice([i for i in range(self.num_nodes) if i != sender_id])
                tx = Transaction(
                    sender=f"node-{sender_id}",
                    receiver=f"node-{receiver_id}",
                    amount=random.randint(1, 100),
                    valid=random.choice([True, True, False]),  # 2/3 valid
                )
                self.metrics.record_transaction(tx.valid)

                # Update node behavior
                node = self.nodes[sender_id]
                node.update_behavior(tx)

            # Select validator and mine block
            validator = self.consensus_fn(self.nodes)
            block = Block(
                index=block_count,
                validator_id=validator.node_id,
                transactions=[],  # Empty for simulation
                previous_hash="0" * 64,  # Simplified for simulation
            )
            block_time = random.uniform(0.1, 0.5)  # Simulate block time
            self.metrics.record_block(validator.node_id, block_time)
            block_count += 1

            # Sleep to control tx rate
            time.sleep(1.0 / self.tx_rate)

    def get_results(self) -> dict:
        """Get the metrics as a dictionary."""
        return self.metrics.to_dict()
