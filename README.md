# Live Proof of Behavior (PoB) Network

A real-time distributed blockchain network demonstrating multiple consensus algorithms: **Proof of Behavior (PoB)**, **Proof of Stake (PoS)**, and **Proof of Work (PoW)**. Compare fairness, security, and speed across all three.

## What It Does

### Core Features

- **Real-Time Node Communication**: Each node runs as a separate Python process on its own port and communicates with peers via TCP sockets.
- **Multiple Consensus Algorithms**: Support for PoB, PoS, and PoW with pluggable strategy functions.
- **Live Transaction Propagation**: Transactions are created continuously and broadcast to all peers in real time.
- **Dynamic Validator Selection**: Validators are selected each round based on the chosen algorithm.
- **Distributed Blockchain**: Each node maintains its own copy of the blockchain and stays in sync as blocks are mined.
- **Live Block Mining**: Only the selected validator can mine a block in each round. The block is broadcast to peers.
- **Comprehensive Metrics**: Fairness, security, and speed metrics are collected and displayed.

---

## Consensus Algorithms

### Proof of Behavior (PoB)
**Selection formula**: `max(behavior_score + (uptime × 0.35))`

- **Fair**: Rewards nodes that generate valid transactions and maintain uptime
- **Behavior-driven**: Score increases with valid txs (+0.18), decreases with invalid txs (-0.28)
- **Best for**: Networks that prioritize honest behavior

### Proof of Stake (PoS)
**Selection formula**: Random weighted by node stake

- **Stake-based**: Nodes with higher stake have higher probability of selection
- **Deterministic**: Selection is proportional to economic investment
- **Best for**: Preserving wealth-based security models

### Proof of Work (PoW)
**Selection formula**: `max(hash_power)`

- **Work-based**: Nodes with highest computing power always selected
- **Deterministic**: Always picks the same node (least fair)
- **Best for**: Demonstrating tradeoffs between fairness and speed

---

## How to Run

### Mode 1: Live Network with Consensus Selection

Run one of the three consensus algorithms across multiple nodes in separate terminals:

**Terminal 1:**
```bash
python main.py --node-id 0 --consensus pob --cluster 0:10:50:5000 1:50:10:5001 2:20:20:5002 3:100:5:5003 4:5:100:5004
```

**Terminal 2-5:** (change `--node-id` for each)
```bash
python main.py --node-id 1 --consensus pob --cluster 0:10:50:5000 1:50:10:5001 2:20:20:5002 3:100:5:5003 4:5:100:5004
python main.py --node-id 2 --consensus pob --cluster 0:10:50:5000 1:50:10:5001 2:20:20:5002 3:100:5:5003 4:5:100:5004
python main.py --node-id 3 --consensus pob --cluster 0:10:50:5000 1:50:10:5001 2:20:20:5002 3:100:5:5003 4:5:100:5004
python main.py --node-id 4 --consensus pob --cluster 0:10:50:5000 1:50:10:5001 2:20:20:5002 3:100:5:5003 4:5:100:5004
```

Change `--consensus pob` to `--consensus pos` or `--consensus pow` to try different algorithms.

### Mode 2: Consensus Comparison (Fastest Way to Compare All Three)

Run an automated offline comparison of all three algorithms:

```bash
python compare_consensus.py --duration 60 --nodes 5 --tx-rate 3
```

This generates:
- Real-time output for each algorithm
- Comparison table with side-by-side metrics
- Rankings for fairness, security, and speed
- JSON output (`consensus_comparison.json`) with full results

**Options:**
- `--duration`: Simulation duration in seconds (default: 60)
- `--nodes`: Number of nodes to simulate (default: 5)
- `--tx-rate`: Transaction rate in tx/sec (default: 2.5)

---

## Command-Line Arguments (Live Network)

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--node-id` | int | 0 | The ID of this node (must exist in cluster) |
| `--consensus` | str | pob | Consensus algorithm: `pob`, `pos`, or `pow` |
| `--cluster` | space-separated strings | 5 default nodes | Cluster config format: `node_id:stake:hash_power:port` |
| `--tx-interval` | float | 2.5 | Seconds between auto-generated transactions |
| `--mine-interval` | float | 1.0 | Seconds between validator selection checks |
| `--batch-size` | int | 4 | Maximum transactions per block |
| `--manual` | flag | off | Disable auto-transaction generation |

---

## Understanding the Metrics

### Fairness (0.0 - 1.0)
- **1.0** = All nodes selected equally
- **0.5** = Moderate distribution
- **0.0** = Only one node selected (most unfair)

**Interpretation:**
- PoB: Higher fairness (rewards honest behavior)
- PoS: Medium fairness (biased toward high-stake nodes)
- PoW: Lowest fairness (always selects highest hash power)

### Security (0.0 - 1.0)
- **1.0** = All transactions are valid
- **0.5** = 50% of transactions valid
- **0.0** = All transactions invalid

**Interpretation:**
- Higher security = network better filters invalid txs
- All three algorithms have similar security (depends on tx generation, not consensus)

### Speed (blocks/sec)
- Higher = faster block time
- Affected by network latency and consensus complexity
- All three have similar speed in local tests

---

## Sample Output

### Live Network Output
```
[node 0] consensus=POB auto_tx=on tx_interval=2.5s mine_interval=1.0s
[node 0] created tx 5912eea2: node-0 -> node-1 (77) valid=False
[node 0] tx a5c46402 from node 1: node-1 -> node-0 (95) valid=True
[node 0] mined block 1 as validator (consensus=POB) with 4 txs
[node 0] height=12 pending=5 validator=N1 scores=[0:1.40, 1:2.75, 2:0.88, 3:1.50, 4:0.95]
```

### Comparison Output
```
==========================================================================================
COMPARISON SUMMARY
==========================================================================================
Metric                    PoB                  PoS                  PoW                 
------------------------------------------------------------------------------------------
Blocks Mined              90                   90                   90                  
Blocks/sec                0.9987               1.4980               2.9960              
Fairness (0-1)            0.2885               0.0552               0.0000              
Security (0-1)            0.7245               0.7147               0.6764              
Speed (0-1)               0.9986               1.0000               1.0000              
==========================================================================================

RANKINGS (higher is better):

Fairness:  PoB (0.2885) > PoS (0.0552) > PoW (0.0000)
Security:  PoB (0.7245) > PoS (0.7147) > PoW (0.6764)
Speed:     PoW (2.9957 blocks/s) > PoS (1.4979 blocks/s) > PoB (0.9986 blocks/s)
```

---

## Key Observations

### Proof of Behavior (PoB) - BEST FOR FAIRNESS
- **Fairness**: ✓ Better distribution (0.28+)
- **Security**: ✓ Similar to PoS (~0.72)
- **Speed**: ⚠ Slower (depends on behavior accumulation)
- **Trait**: Rewards honest validators with higher probability over time

### Proof of Stake (PoS) - BALANCED
- **Fairness**: ⚠ Biased toward high-stake nodes (0.05)
- **Security**: ✓ Good (~0.71)
- **Speed**: ✓ Fast (randomness helps)
- **Trait**: Protects against Sybil attacks via economic cost

### Proof of Work (PoW) - FASTEST BUT UNFAIR
- **Fairness**: ✗ Always same node (0.0)
- **Security**: ⚠ Lowest (~0.67)
- **Speed**: ✓ Fastest deterministic selection
- **Trait**: No randomness; purely computational superiority

---

## Demo Scenarios

### Scenario 1: PoB Live Demo (3 minutes)
```bash
# Terminal 1
python main.py --node-id 0 --consensus pob --tx-interval 0.8 --mine-interval 0.5

# Terminal 2
python main.py --node-id 1 --consensus pob --tx-interval 0.8 --mine-interval 0.5

# Terminal 3
python main.py --node-id 2 --consensus pob --tx-interval 0.8 --mine-interval 0.5
```

**What to watch:**
- Nodes 1 and 2 compete based on behavior scores
- Fairness improves as validators get more chances
- Watch how behavior score affects validator selection

### Scenario 2: Fast Comparison (1 minute)
```bash
python compare_consensus.py --duration 60 --nodes 5 --tx-rate 5
```

**What you'll see:**
- PoW always selects node 4 (lowest fairness)
- PoS favors node 3 (highest stake)
- PoB more evenly distributes selections
- Fairness rankings are clear

### Scenario 3: Custom 3-Node Network
```bash
# Run with custom stake/hash power distribution
python main.py --node-id 0 --consensus pos --cluster 0:100:10:6000 1:50:20:6001 2:30:50:6002
python main.py --node-id 1 --consensus pos --cluster 0:100:10:6000 1:50:20:6001 2:30:50:6002
python main.py --node-id 2 --consensus pos --cluster 0:100:10:6000 1:50:20:6001 2:30:50:6002
```

---

## Architecture

### Modular Design

The codebase is organized into focused, reusable modules:

```
POB/
├── main.py                      # Live network entry point (CLI wrapper)
├── compare_consensus.py         # Consensus comparison tool (orchestration)
├── models.py                    # Core data structures (Transaction, Block, Blockchain, NodeState)
├── consensus.py                 # Pluggable consensus algorithms (PoB, PoS, PoW)
├── metrics.py                   # Performance metrics (ConsensusMetrics, fairness/security/speed)
├── node.py                      # Live P2P network node (LocalNetworkNode with TCP)
├── simulator.py                 # Offline simulation engine (ConsensusSimulator)
├── README.md                    # This file
├── IMPLEMENTATION_SUMMARY.md    # Quick implementation reference
├── consensus_comparison.json    # Results from last comparison run
└── __pycache__/                 # Python cache
```

### Module Responsibilities

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `models.py` | Data structures | `Transaction`, `Block`, `Blockchain`, `NodeState` |
| `consensus.py` | Algorithm selection | `select_validator_pob()`, `select_validator_pos()`, `select_validator_pow()` |
| `metrics.py` | Performance tracking | `ConsensusMetrics` (fairness, security, speed) |
| `node.py` | Live P2P networking | `LocalNetworkNode` (TCP sockets, mining, broadcasts) |
| `simulator.py` | Offline testing | `ConsensusSimulator` (controlled environment) |
| `main.py` | CLI for live network | Argument parsing, node instantiation |
| `compare_consensus.py` | Comparison orchestration | Algorithm comparison, results reporting |

---

## Troubleshooting

### Ports Already in Use
```bash
python main.py --node-id 0 --cluster 0:10:50:7000 1:50:10:7001 ...
```

### All Nodes Show Same Validator (PoW)
This is expected—PoW always picks the highest hash power node. See node 4 with `hash_power=100`.

### Fairness Score Always Low
This is normal in short runs. Fairness improves over time as PoB behavior scores accumulate.

### Comparison Produces Different Results Each Time
Expected! PoS uses randomness, so results vary. Run multiple times for average behavior.

---

## Further Reading

- **Proof of Behavior**: Rewards validator behavior and uptime (novel approach)
- **Proof of Stake**: Economic security via stake ownership (Ethereum 2.0, Cardano)
- **Proof of Work**: Computational security via hash power (Bitcoin, Ethereum 1.0)

---

## License

MIT

