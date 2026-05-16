"""
Interact with the ValidatorReputation Smart Contract

This script demonstrates:
1. Registering validators
2. Updating validator metrics
3. Reading validator data
4. Getting validator rankings
"""

import json
from eth_connector import EthereumConnector


def load_contract_info() -> dict:
    """Load contract address and ABI from file."""
    try:
        with open('contract_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("contract_info.json not found. Deploy contract first with: python deploy_contract.py")


def main():
    print("\n" + "="*70)
    print("🤝 VALIDATOR REPUTATION CONTRACT INTERACTION")
    print("="*70 + "\n")
    
    try:
        # Connect to Sepolia
        print("🔗 Connecting to Ethereum Sepolia...")
        eth = EthereumConnector()
        
        # Load contract info
        print("📋 Loading contract information...")
        contract_info = load_contract_info()
        contract_address = contract_info['address']
        contract_abi = contract_info['abi']
        
        print(f"✅ Contract loaded: {contract_address}\n")
        
        # Get contract instance
        contract = eth.get_contract(contract_address, contract_abi)
        
        # Demo: Register validators
        print("="*70)
        print("1️⃣  REGISTERING VALIDATORS")
        print("="*70 + "\n")
        
        # Example validator addresses (you can use any Ethereum addresses)
        validators_to_register = [
            "0xBe6e120A4FAcaf29B718C6DE82d6C37243318C37",  # Your account
            "0x1234567890123456789012345678901234567890",
            "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        ]
        
        print("Registering validators:")
        for validator_addr in validators_to_register:
            print(f"\n  Registering: {validator_addr}")
            try:
                receipt = eth.execute_contract_function(
                    contract,
                    "registerValidator",
                    validator_addr
                )
                print(f"  ✅ Registered in tx: {receipt['transactionHash'].hex()}")
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
        
        # Demo: Update validator metrics
        print("\n" + "="*70)
        print("2️⃣  UPDATING VALIDATOR METRICS")
        print("="*70 + "\n")
        
        print("Updating validator metrics (PoB scores):\n")
        
        # Example metrics
        metrics_updates = [
            {
                'validator': validators_to_register[0],
                'valid_txs': 45,
                'invalid_txs': 2,
                'behavior_score': 150,  # 1.5 (stored as 150)
                'uptime_score': 95,     # 95%
            },
            {
                'validator': validators_to_register[1],
                'valid_txs': 38,
                'invalid_txs': 5,
                'behavior_score': 125,  # 1.25
                'uptime_score': 88,
            },
            {
                'validator': validators_to_register[2],
                'valid_txs': 52,
                'invalid_txs': 1,
                'behavior_score': 175,  # 1.75
                'uptime_score': 99,
            },
        ]
        
        for metrics in metrics_updates:
            print(f"  Validator: {metrics['validator'][:10]}...")
            print(f"    Valid TXs: {metrics['valid_txs']}")
            print(f"    Invalid TXs: {metrics['invalid_txs']}")
            print(f"    Behavior Score: {metrics['behavior_score']/100:.2f}")
            print(f"    Uptime: {metrics['uptime_score']}%")
            
            try:
                receipt = eth.execute_contract_function(
                    contract,
                    "updateValidatorMetrics",
                    metrics['validator'],
                    metrics['valid_txs'],
                    metrics['invalid_txs'],
                    metrics['behavior_score'],
                    metrics['uptime_score']
                )
                print(f"    ✅ Updated in tx: {receipt['transactionHash'].hex()}\n")
            except Exception as e:
                print(f"    ⚠️  Error: {e}\n")
        
        # Demo: Read validator data
        print("="*70)
        print("3️⃣  READING VALIDATOR DATA")
        print("="*70 + "\n")
        
        for validator_addr in validators_to_register:
            print(f"  Validator: {validator_addr}")
            try:
                metrics = eth.call_contract_function(
                    contract,
                    "getValidatorMetrics",
                    validator_addr
                )
                
                print(f"    Valid Transactions: {metrics[1]}")
                print(f"    Invalid Transactions: {metrics[2]}")
                print(f"    Uptime Score: {metrics[3]}%")
                print(f"    Behavior Score: {metrics[4]/100:.2f}")
                print(f"    PoB Reputation Score: {metrics[5]/10000:.4f}")
                print(f"    Last Updated: {metrics[6]}")
                print()
            except Exception as e:
                print(f"    ⚠️  Error reading: {e}\n")
        
        # Demo: Get validator count
        print("="*70)
        print("4️⃣  VALIDATOR COUNT")
        print("="*70 + "\n")
        
        try:
            count = eth.call_contract_function(contract, "getValidatorCount")
            print(f"  Total Validators: {count}\n")
        except Exception as e:
            print(f"  Error: {e}\n")
        
        print("="*70)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*70)
        print(f"\n📍 Contract Address: {contract_address}")
        print(f"🔍 View on Etherscan: https://sepolia.etherscan.io/address/{contract_address}")
        print(f"\n💡 Next Steps:")
        print(f"   - Monitor validator metrics over time")
        print(f"   - Compare PoW vs PoS vs PoB validator selection")
        print(f"   - Analyze fairness metrics\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
