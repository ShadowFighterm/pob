"""
Live network node implementation.

Classes:
- LocalNetworkNode: A distributed blockchain node with TCP socket communication
"""

from __future__ import annotations

import json
import random
import socket
import threading
import time
from typing import Callable, Dict, Iterable, List, Optional

from models import Transaction, NodeState, Block, Blockchain
from metrics import ConsensusMetrics

HOST = "127.0.0.1"


class LocalNetworkNode:
    """
    A live blockchain node that communicates with peers over TCP sockets.
    
    Features:
    - Real-time transaction broadcast
    - Configurable consensus algorithm
    - Distributed block mining and syncing
    - Metrics collection
    """
    
    def __init__(
        self,
        local_node_id: int,
        cluster: Dict[int, dict],
        consensus_fn: Optional[Callable] = None,
        consensus_name: str = "pob",
        auto_tx: bool = True,
        tx_interval: float = 2.5,
        mine_interval: float = 1.0,
        batch_size: int = 4,
    ) -> None:
        """
        Initialize a network node.
        
        Args:
            local_node_id: This node's ID
            cluster: Dict mapping node_id to {'stake', 'hash_power', 'port'}
            consensus_fn: Function to select validator (default: PoB)
            consensus_name: Name of consensus algorithm for logging
            auto_tx: Whether to auto-generate transactions
            tx_interval: Seconds between transactions
            mine_interval: Seconds between validator checks
            batch_size: Max transactions per block
        """
        if local_node_id not in cluster:
            raise ValueError(f"Node {local_node_id} is not present in the supplied cluster")

        self.node_id = local_node_id
        self.consensus_fn = consensus_fn
        self.consensus_name = consensus_name
        self.metrics = ConsensusMetrics(consensus_name)
        self.nodes = {
            node_id: NodeState(
                node_id=node_id,
                stake=config["stake"],
                hash_power=config["hash_power"],
                port=config["port"],
            )
            for node_id, config in cluster.items()
        }
        self.local_node = self.nodes[self.node_id]
        self.cluster = cluster
        self.auto_tx = auto_tx
        self.tx_interval = tx_interval
        self.mine_interval = mine_interval
        self.batch_size = batch_size
        self.blockchain = Blockchain()
        self.mempool: List[Transaction] = []
        self.seen_transactions: set[str] = set()
        self.seen_blocks: set[str] = set()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Create genesis block
        self._startup_block = Block(0, self.node_id, [], "0" * 64)
        self.blockchain.add_block(self._startup_block)
        self.seen_blocks.add(self._startup_block.hash)

    def start(self) -> None:
        """Start the node's server and background threads."""
        server_thread = threading.Thread(target=self._serve, daemon=True)
        server_thread.start()

        if self.auto_tx:
            producer_thread = threading.Thread(target=self._transaction_loop, daemon=True)
            producer_thread.start()

        miner_thread = threading.Thread(target=self._miner_loop, daemon=True)
        miner_thread.start()

        status_thread = threading.Thread(target=self._status_loop, daemon=True)
        status_thread.start()

        print(
            f"[node {self.node_id}] live on port {self.local_node.port}; "
            f"peers={sorted(node_id for node_id in self.cluster if node_id != self.node_id)}"
        )
        print(
            f"[node {self.node_id}] consensus={self.consensus_name.upper()} auto_tx={'on' if self.auto_tx else 'off'} "
            f"tx_interval={self.tx_interval}s mine_interval={self.mine_interval}s"
        )

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_event.set()
            print(f"[node {self.node_id}] shutting down")
            print(self.metrics.summary())

    def _serve(self) -> None:
        """TCP server loop: accept incoming connections from peers."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, self.local_node.port))
            server.listen()
            server.settimeout(1.0)

            while not self.stop_event.is_set():
                try:
                    connection, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                threading.Thread(target=self._handle_connection, args=(connection,), daemon=True).start()

    def _handle_connection(self, connection: socket.socket) -> None:
        """Handle a single peer connection."""
        buffer = ""
        with connection:
            connection.settimeout(1.0)
            while not self.stop_event.is_set():
                try:
                    chunk = connection.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break

                if not chunk:
                    break

                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    raw_message, buffer = buffer.split("\n", 1)
                    raw_message = raw_message.strip()
                    if raw_message:
                        self._handle_message(json.loads(raw_message))

    def _handle_message(self, message: dict) -> None:
        """Process a message from a peer."""
        message_type = message.get("type")
        if message_type == "transaction":
            transaction = Transaction.from_dict(message["transaction"])
            accepted = self._register_transaction(transaction, local_echo=False)
            if accepted:
                print(
                    f"[node {self.node_id}] tx {transaction.tx_id[:8]} from node {transaction.origin_node_id}: "
                    f"{transaction.sender} -> {transaction.receiver} ({transaction.amount}) valid={transaction.valid}"
                )
        elif message_type == "block":
            block = Block.from_dict(message["block"])
            self._accept_block(block)

    def _register_transaction(self, transaction: Transaction, local_echo: bool) -> bool:
        """Add a transaction to the mempool if not already seen."""
        with self.lock:
            if transaction.tx_id in self.seen_transactions:
                return False

            self.seen_transactions.add(transaction.tx_id)
            self.mempool.append(transaction)
            self.metrics.record_transaction(transaction.valid)

            origin_node_id = transaction.origin_node_id if transaction.origin_node_id is not None else self.node_id
            origin_node = self.nodes.get(origin_node_id)
            if origin_node is not None:
                origin_node.update_behavior(transaction)

            if local_echo:
                print(
                    f"[node {self.node_id}] created tx {transaction.tx_id[:8]}: "
                    f"{transaction.sender} -> {transaction.receiver} ({transaction.amount}) valid={transaction.valid}"
                )
            return True

    def _accept_block(self, block: Block) -> None:
        """Process and add a block from a peer to the chain."""
        with self.lock:
            if block.hash in self.seen_blocks:
                return

            latest_block = self.blockchain.latest_block
            if latest_block is not None and block.previous_hash != latest_block.hash:
                return

            if not self.blockchain.add_block(block):
                return

            self.seen_blocks.add(block.hash)
            included_ids = {tx.tx_id for tx in block.transactions}
            self.mempool = [tx for tx in self.mempool if tx.tx_id not in included_ids]
            print(
                f"[node {self.node_id}] accepted block {block.index} from node {block.validator_id} "
                f"with {len(block.transactions)} txs"
            )

    def _broadcast(self, message: dict) -> None:
        """Send a message to all peers."""
        payload = (json.dumps(message) + "\n").encode("utf-8")
        for node_id, peer in self.cluster.items():
            if node_id == self.node_id:
                continue

            try:
                with socket.create_connection((HOST, peer["port"]), timeout=1.0) as connection:
                    connection.sendall(payload)
            except OSError:
                continue

    def _transaction_loop(self) -> None:
        """Background loop: continuously generate and broadcast transactions."""
        while not self.stop_event.is_set():
            time.sleep(max(0.5, self.tx_interval + random.uniform(-0.4, 0.7)))
            receiver_id = random.choice([node_id for node_id in self.cluster if node_id != self.node_id])
            transaction = Transaction(
                sender=f"node-{self.node_id}",
                receiver=f"node-{receiver_id}",
                amount=random.randint(1, 100),
                valid=random.choice([True, True, False]),
                origin_node_id=self.node_id,
            )
            if self._register_transaction(transaction, local_echo=True):
                self._broadcast({"type": "transaction", "transaction": transaction.to_dict()})

    def _miner_loop(self) -> None:
        """Background loop: select validator and mine blocks."""
        while not self.stop_event.is_set():
            time.sleep(self.mine_interval)
            with self.lock:
                if not self.mempool:
                    continue

                validator = self.consensus_fn(self.nodes.values())
                if validator.node_id != self.node_id:
                    continue

                block_start_time = time.time()
                transactions = self.mempool[: self.batch_size]
                previous_hash = self.blockchain.latest_block.hash if self.blockchain.latest_block else "0" * 64
                block = Block(
                    index=len(self.blockchain.chain),
                    validator_id=self.node_id,
                    transactions=transactions,
                    previous_hash=previous_hash,
                )

                if not self.blockchain.add_block(block):
                    continue

                block_time = time.time() - block_start_time
                self.metrics.record_block(self.node_id, block_time)
                self.seen_blocks.add(block.hash)
                mined_ids = {tx.tx_id for tx in transactions}
                self.mempool = [tx for tx in self.mempool if tx.tx_id not in mined_ids]

            print(
                f"[node {self.node_id}] mined block {block.index} as validator (consensus={self.consensus_name.upper()}) "
                f"with {len(transactions)} txs"
            )
            self._broadcast({"type": "block", "block": block.to_dict()})

    def _status_loop(self) -> None:
        """Background loop: periodically log node status."""
        while not self.stop_event.is_set():
            time.sleep(5)
            with self.lock:
                validator = self.consensus_fn(self.nodes.values())
                scores = ", ".join(
                    f"{node.node_id}:{node.consensus_score():.2f}"
                    for node in sorted(self.nodes.values(), key=lambda item: item.node_id)
                )
                chain_length = len(self.blockchain.chain)
                pending = len(self.mempool)

            print(
                f"[node {self.node_id}] height={chain_length - 1} pending={pending} "
                f"validator=N{validator.node_id} scores=[{scores}]"
            )
