# Proof of Behavior (PoB)

## A Dynamic Validator Reputation Framework for Blockchain Fairness

This project now has two connected parts:

1. A local Python prototype that compares PoB, PoS, and PoW.
2. A real Ethereum Sepolia integration that stores validator reputation data on-chain and analyzes live blockchain behavior off-chain.

The main research goal is to test whether a behavior-aware validator reputation model can improve fairness compared with stake-based or hash-power-based selection.

---

## What Is Included

### Local Prototype
- Real-time TCP-based distributed blockchain simulation.
- Pluggable PoB, PoS, and PoW validator selection.
- Fairness, security, and throughput benchmarking.

### Sepolia Integration
- Ethereum Sepolia connection through Web3.py.
- Smart contract deployment for validator reputation storage.
- On-chain validator registration and metric updates.
- Real blockchain analysis using Sepolia block and transaction data.

---

## Project Files

### Core Python Modules
- [main.py](main.py) - live local node entry point.
- [node.py](node.py) - distributed TCP node implementation.
- [consensus.py](consensus.py) - PoB, PoS, and PoW selection logic.
- [models.py](models.py) - block, transaction, blockchain, and node models.
- [metrics.py](metrics.py) - fairness, security, and throughput metrics.
- [compare_consensus.py](compare_consensus.py) - offline comparison tool.

### Sepolia Modules
- [eth_connector.py](eth_connector.py) - Web3 connection helper.
- [ValidatorReputation.sol](ValidatorReputation.sol) - validator reputation smart contract.
- [deploy_contract.py](deploy_contract.py) - compile and deploy the contract.
- [interact_contract.py](interact_contract.py) - register validators and update metrics.
- [analyze_real_blockchain.py](analyze_real_blockchain.py) - analyze live Sepolia blocks.

### Output Files
- [contract_info.json](contract_info.json) - deployed contract address and ABI.
- [blockchain_analysis_results.json](blockchain_analysis_results.json) - latest real-network analysis results.
- [consensus_comparison.json](consensus_comparison.json) - latest local simulation comparison.

---

## What We Built So Far

### Local Consensus Prototype
- Proof of Behavior rewards valid behavior and uptime.
- Proof of Stake uses stake-weighted random selection.
- Proof of Work selects the highest hash power node.
- The comparison tool generates fairness, security, and speed metrics.

### Sepolia Testnet Workflow
- Connected the project to Ethereum Sepolia.
- Deployed a validator reputation smart contract.
- Registered validators and stored metrics on-chain.
- Analyzed real Sepolia blocks and produced a PoW vs PoB comparison.

### Main Finding
- PoB is the fairness-oriented design.
- PoS remains wealth-biased.
- PoW remains hash-power dominant.

---

## Requirements

### You Need
- Python 3.10 or newer.
- MetaMask.
- Some Sepolia test ETH for contract deployment and contract updates.
- A private key exported from the MetaMask account used for Sepolia.

### Python Packages
Install these in your environment:

```bash
pip install web3 python-dotenv py-solc-x
```

---

## Configuration

Create a `.env` file in the project root and set these values:

```env
PRIVATE_KEY=your_metamask_private_key
SEPOLIA_RPC_URL=https://sepolia.drpc.org
CHAIN_ID=11155111
GAS_LIMIT=3000000
GAS_PRICE_GWEI=50
```

Do not commit `.env` to Git.

---

## Run It Step by Step

### 1. Test the Sepolia connection

```bash
python test_connection.py
```

### 2. Deploy the smart contract

```bash
python deploy_contract.py
```

This creates `contract_info.json` and deploys the validator reputation contract to Sepolia.

### 3. Interact with the contract

```bash
python interact_contract.py
```

This registers validators, updates validator metrics, and reads the stored data back from Sepolia.

### 4. Analyze real blockchain data

```bash
python analyze_real_blockchain.py
```

This reads recent Sepolia blocks, computes validator behavior metrics, compares PoW-style and PoB-style selection, and writes `blockchain_analysis_results.json`.

### 5. Run the local simulation comparison

```bash
python compare_consensus.py --duration 60 --nodes 5 --tx-rate 3
```

This is still useful for a controlled side-by-side comparison of PoB, PoS, and PoW.

---

## Current Research Direction

The project originally focused on a standalone blockchain simulator. It now focuses on blockchain-integrated behavioral validation:

- Validator fairness analysis.
- Behavior-based trust scoring.
- Real blockchain interaction through Ethereum Sepolia.
- Off-chain Python analysis that complements on-chain reputation storage.

The PoB score used in the project is:

```text
S_i = B_i + (U_i × 0.35)
```

Where:
- `B_i` is the behavior score.
- `U_i` is the uptime factor.

The behavior update rule is:

```text
B_i(t) = B_i(t-1) + 0.18 × ValidTx_i - 0.28 × InvalidTx_i
```

---

## How to Read the Results

- `contract_info.json` stores the deployed contract address and ABI.
- `blockchain_analysis_results.json` stores the Sepolia block analysis output.
- `consensus_comparison.json` stores the local simulation comparison results.

The latest Sepolia workflow showed that the contract deployment, validator registration, metric updates, and block analysis all complete successfully.

---

## Troubleshooting

- If `test_connection.py` fails, verify that `.env` has a valid private key and Sepolia RPC URL.
- If contract deployment fails, confirm that the wallet has Sepolia ETH.
- If you get checksum address errors, make sure addresses are converted with Web3 checksum handling.
- If `py-solc-x` is missing, install it with `pip install py-solc-x`.

---

## Summary

This project now demonstrates a complete PoB research path:

- a working local PoB/PoS/PoW benchmark,
- a deployed Sepolia smart contract for validator reputation,
- and a real-network analysis pipeline for fairness evaluation.

That makes the project usable both as a prototype and as a blockchain-integrated research demo.

---

## License

MIT

