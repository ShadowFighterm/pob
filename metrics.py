"""
Metrics collection and analysis for consensus algorithms.

Classes:
- ConsensusMetrics: Tracks and calculates performance metrics
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ConsensusMetrics:
    """
    Tracks performance metrics for consensus algorithms.
    
    Metrics tracked:
    - Blocks mined and mining rate
    - Transactions processed and rate
    - Validator selection fairness
    - Security (valid tx ratio)
    - Speed (blocks/sec)
    """
    consensus_type: str
    validator_selections: Dict[int, int] = field(default_factory=dict)
    blocks_mined: int = 0
    transactions_processed: int = 0
    invalid_transactions: int = 0
    start_time: float = field(default_factory=time.time)
    block_times: List[float] = field(default_factory=list)

    @property
    def elapsed_time(self) -> float:
        """Total elapsed time since metrics creation."""
        return time.time() - self.start_time

    @property
    def blocks_per_second(self) -> float:
        """Average blocks mined per second."""
        elapsed = self.elapsed_time
        return self.blocks_mined / elapsed if elapsed > 0 else 0

    @property
    def transactions_per_second(self) -> float:
        """Average transactions processed per second."""
        elapsed = self.elapsed_time
        return self.transactions_processed / elapsed if elapsed > 0 else 0

    @property
    def average_block_time(self) -> float:
        """Average time to mine one block."""
        return sum(self.block_times) / len(self.block_times) if self.block_times else 0

    def record_block(self, validator_id: int, block_time: float | None = None) -> None:
        """Record a mined block and update validator selection count."""
        self.blocks_mined += 1
        self.validator_selections[validator_id] = self.validator_selections.get(validator_id, 0) + 1
        if block_time is not None:
            self.block_times.append(block_time)

    def record_transaction(self, valid: bool) -> None:
        """Record a transaction as valid or invalid."""
        self.transactions_processed += 1
        if not valid:
            self.invalid_transactions += 1

    def fairness_score(self) -> float:
        """
        Calculate fairness of validator selection (0.0 - 1.0).
        
        1.0 = Perfect fairness (all nodes selected equally)
        0.5 = Moderate fairness (60/40 split)
        0.0 = Complete unfairness (one node selected 100%)
        
        Based on coefficient of variation of validator selections.
        """
        if not self.validator_selections:
            return 0.0
        values = list(self.validator_selections.values())
        num_nodes = len(values)
        total_selections = sum(values)
        
        if num_nodes < 2 or total_selections == 0:
            return 0.0
        
        # Calculate coefficient of variation
        average = total_selections / num_nodes
        variance = sum((v - average) ** 2 for v in values) / num_nodes
        std_dev = variance ** 0.5
        cv = std_dev / average if average > 0 else float('inf')
        
        # Convert CV to fairness score
        if cv >= 1.0:
            return 1.0 / (1.0 + cv)
        else:
            return max(0.0, 1.0 - cv)

    def security_score(self) -> float:
        """
        Calculate security score: valid transaction ratio (0.0 - 1.0).
        
        1.0 = All transactions valid (100%)
        0.7 = 70% of transactions valid
        0.0 = All transactions invalid
        """
        if self.transactions_processed == 0:
            return 1.0
        return 1.0 - (self.invalid_transactions / self.transactions_processed)

    def speed_score(self) -> float:
        """
        Calculate speed score: blocks per second normalized to 0-1 range.
        
        Assumes 1 block/sec is "good", caps at 1.0.
        """
        bps = self.blocks_per_second
        return min(1.0, bps)

    def to_dict(self) -> dict:
        """Convert all metrics to a dictionary for serialization."""
        return {
            "consensus_type": self.consensus_type,
            "blocks_mined": self.blocks_mined,
            "transactions_processed": self.transactions_processed,
            "invalid_transactions": self.invalid_transactions,
            "elapsed_time": round(self.elapsed_time, 2),
            "blocks_per_second": round(self.blocks_per_second, 4),
            "transactions_per_second": round(self.transactions_per_second, 4),
            "average_block_time": round(self.average_block_time, 4),
            "validator_selections": dict(self.validator_selections),
            "fairness_score": round(self.fairness_score(), 4),
            "security_score": round(self.security_score(), 4),
            "speed_score": round(self.speed_score(), 4),
        }

    def summary(self) -> str:
        """Generate a formatted summary of all metrics."""
        d = self.to_dict()
        fairness_status = "[OK] FAIR" if d["fairness_score"] > 0.8 else "[!] SKEWED"
        security_status = "[OK] SECURE" if d["security_score"] > 0.95 else "[!] VULNERABLE"
        return (
            f"\n{'='*70}\n"
            f"Consensus: {d['consensus_type'].upper()}\n"
            f"{'='*70}\n"
            f"Elapsed Time:        {d['elapsed_time']:>6}s\n"
            f"Blocks Mined:        {d['blocks_mined']:>6}\n"
            f"Blocks/sec:          {d['blocks_per_second']:>6.4f}\n"
            f"Avg Block Time:      {d['average_block_time']:>6.4f}s\n"
            f"Transactions:        {d['transactions_processed']:>6}\n"
            f"Invalid Txs:         {d['invalid_transactions']:>6}\n"
            f"Txs/sec:             {d['transactions_per_second']:>6.4f}\n"
            f"Validator Picks:     {d['validator_selections']}\n"
            f"\nSCORES (0.0 - 1.0):\n"
            f"  Fairness:          {d['fairness_score']:>6.4f}  {fairness_status}\n"
            f"  Security:          {d['security_score']:>6.4f}  {security_status}\n"
            f"  Speed:             {d['speed_score']:>6.4f}\n"
            f"{'='*70}\n"
        )
