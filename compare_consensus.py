#!/usr/bin/env python3
"""
Consensus Algorithm Comparison Tool

Runs PoB, PoS, and PoW in separate simulated networks and compares:
- Fairness (validator selection distribution)
- Security (valid transaction ratio)
- Speed (blocks per second)

Usage:
    python compare_consensus.py [--duration 60] [--nodes 5] [--tx-rate 2.5]
"""

import argparse
import json
from typing import Dict

from consensus import select_validator_pob, select_validator_pos, select_validator_pow
from metrics import ConsensusMetrics
from simulator import ConsensusSimulator


def compare_consensus(num_nodes: int = 5, duration: float = 60.0, tx_rate: float = 2.5) -> None:
    """Run and compare all three consensus algorithms."""
    print(f"\n{'='*70}")
    print("CONSENSUS ALGORITHM COMPARISON")
    print(f"{'='*70}")
    print(f"Number of Nodes:     {num_nodes}")
    print(f"Simulation Duration: {duration}s")
    print(f"Transaction Rate:    {tx_rate} tx/s")
    print(f"{'='*70}\n")

    results = {}

    # Run PoB
    print("Running Proof of Behavior (PoB)...")
    sim_pob = ConsensusSimulator(num_nodes, select_validator_pob, "pob", duration, tx_rate)
    sim_pob.run()
    results["pob"] = sim_pob.metrics
    print(sim_pob.metrics.summary())

    # Run PoS
    print("Running Proof of Stake (PoS)...")
    sim_pos = ConsensusSimulator(num_nodes, select_validator_pos, "pos", duration, tx_rate)
    sim_pos.run()
    results["pos"] = sim_pos.metrics
    print(sim_pos.metrics.summary())

    # Run PoW
    print("Running Proof of Work (PoW)...")
    sim_pow = ConsensusSimulator(num_nodes, select_validator_pow, "pow", duration, tx_rate)
    sim_pow.run()
    results["pow"] = sim_pow.metrics
    print(sim_pow.metrics.summary())

    # Comparison table
    print_comparison(results)

    # Save to JSON
    json_results = {name: metrics.to_dict() for name, metrics in results.items()}
    with open("consensus_comparison.json", "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"\nResults saved to consensus_comparison.json")


def print_comparison(results: Dict[str, ConsensusMetrics]) -> None:
    """Print a comparison table of all three consensus algorithms."""
    print(f"\n{'='*90}")
    print("COMPARISON SUMMARY")
    print(f"{'='*90}")
    print(
        f"{'Metric':<25} {'PoB':<20} {'PoS':<20} {'PoW':<20}\n"
        + f"{'-'*90}"
    )

    metrics_to_display = [
        ("Blocks Mined", "blocks_mined", "d"),
        ("Blocks/sec", "blocks_per_second", ".4f"),
        ("Avg Block Time (s)", "average_block_time", ".4f"),
        ("Transactions", "transactions_processed", "d"),
        ("Txs/sec", "transactions_per_second", ".4f"),
        ("Fairness (0-1)", "fairness_score", ".4f"),
        ("Security (0-1)", "security_score", ".4f"),
        ("Speed (0-1)", "speed_score", ".4f"),
    ]

    for metric_name, metric_key, fmt_spec in metrics_to_display:
        pob_val = results["pob"].to_dict()[metric_key]
        pos_val = results["pos"].to_dict()[metric_key]
        pow_val = results["pow"].to_dict()[metric_key]

        pob_str = f"{pob_val:{fmt_spec}}"
        pos_str = f"{pos_val:{fmt_spec}}"
        pow_str = f"{pow_val:{fmt_spec}}"

        print(f"{metric_name:<25} {pob_str:<20} {pos_str:<20} {pow_str:<20}")

    print(f"{'='*90}\n")

    # Rankings
    print("RANKINGS (higher is better):\n")

    fairness_scores = {
        "PoB": results["pob"].fairness_score(),
        "PoS": results["pos"].fairness_score(),
        "PoW": results["pow"].fairness_score(),
    }
    fairness_ranked = sorted(fairness_scores.items(), key=lambda x: x[1], reverse=True)
    print(f"Fairness:  {' > '.join(f'{name} ({score:.4f})' for name, score in fairness_ranked)}")

    security_scores = {
        "PoB": results["pob"].security_score(),
        "PoS": results["pos"].security_score(),
        "PoW": results["pow"].security_score(),
    }
    security_ranked = sorted(security_scores.items(), key=lambda x: x[1], reverse=True)
    print(f"Security:  {' > '.join(f'{name} ({score:.4f})' for name, score in security_ranked)}")

    speed_scores = {
        "PoB": results["pob"].blocks_per_second,
        "PoS": results["pos"].blocks_per_second,
        "PoW": results["pow"].blocks_per_second,
    }
    speed_ranked = sorted(speed_scores.items(), key=lambda x: x[1], reverse=True)
    print(f"Speed:     {' > '.join(f'{name} ({score:.4f} blocks/s)' for name, score in speed_ranked)}\n")


def main() -> None:
    """Parse arguments and run comparison."""
    parser = argparse.ArgumentParser(description="Compare PoB, PoS, and PoW consensus algorithms")
    parser.add_argument("--duration", type=float, default=60.0, help="Simulation duration in seconds")
    parser.add_argument("--nodes", type=int, default=5, help="Number of nodes in the network")
    parser.add_argument("--tx-rate", type=float, default=2.5, help="Transaction rate (tx/sec)")

    args = parser.parse_args()

    compare_consensus(num_nodes=args.nodes, duration=args.duration, tx_rate=args.tx_rate)


if __name__ == "__main__":
    main()
