"""
Live network node runner.

Entry point for running a blockchain node with configurable consensus algorithm.
Supports PoB, PoS, and PoW consensus mechanisms.
"""

import argparse
from typing import Dict, List

from consensus import select_validator_pob, select_validator_pos, select_validator_pow
from node import LocalNetworkNode

DEFAULT_CLUSTER = [
    "0:10:50:5000",
    "1:50:10:5001",
    "2:20:20:5002",
    "3:100:5:5003",
    "4:5:100:5004",
]


def parse_cluster(cluster_entries: List[str]) -> Dict[int, dict]:
    """Parse cluster entries in format 'node_id:stake:hash_power:port'."""
    cluster = {}
    for entry in cluster_entries:
        node_id, stake, hash_power, port = map(int, entry.split(":"))
        cluster[node_id] = {
            "node_id": node_id,
            "stake": stake,
            "hash_power": hash_power,
            "port": port,
        }
    return cluster


def build_parser() -> argparse.ArgumentParser:
    """Build command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Run a live local network blockchain node with configurable consensus"
    )
    parser.add_argument(
        "--node-id",
        type=int,
        default=0,
        help="ID of this node (default: 0)",
    )
    parser.add_argument(
        "--consensus",
        choices=["pob", "pos", "pow"],
        default="pob",
        help="Consensus algorithm: PoB (Proof of Behavior), PoS (Proof of Stake), PoW (Proof of Work)",
    )
    parser.add_argument(
        "--cluster",
        nargs="*",
        default=DEFAULT_CLUSTER,
        help="Cluster nodes as 'node_id:stake:hash_power:port' (default: 5-node standard cluster)",
    )
    parser.add_argument(
        "--tx-interval",
        type=float,
        default=2.5,
        help="Seconds between transaction generation (default: 2.5)",
    )
    parser.add_argument(
        "--mine-interval",
        type=float,
        default=1.0,
        help="Seconds between mining attempts (default: 1.0)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Maximum transactions per block (default: 4)",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Disable automatic transaction generation",
    )
    return parser


def main() -> None:
    """Parse arguments and start node."""
    parser = build_parser()
    args = parser.parse_args()

    # Parse cluster configuration
    cluster = parse_cluster(args.cluster)

    # Map consensus name to function
    consensus_map = {
        "pob": select_validator_pob,
        "pos": select_validator_pos,
        "pow": select_validator_pow,
    }

    # Create and start node
    node = LocalNetworkNode(
        local_node_id=args.node_id,
        cluster=cluster,
        consensus_fn=consensus_map[args.consensus],
        consensus_name=args.consensus,
        auto_tx=not args.manual,
        tx_interval=args.tx_interval,
        mine_interval=args.mine_interval,
        batch_size=args.batch_size,
    )
    node.start()


if __name__ == "__main__":
    main()
