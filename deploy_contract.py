"""
Deploy ValidatorReputation Smart Contract to Ethereum Sepolia

This script:
1. Compiles the Solidity contract
2. Deploys it to Sepolia
3. Saves the contract address and ABI for future use
"""

import json
import os
from solcx import compile_source, install_solc
from eth_connector import EthereumConnector


# Read the Solidity contract
CONTRACT_SOURCE_FILE = "ValidatorReputation.sol"


def read_contract_source() -> str:
    """Read Solidity contract from file."""
    with open(CONTRACT_SOURCE_FILE, 'r') as f:
        return f.read()


def compile_contract(source_code: str) -> dict:
    """Compile Solidity contract using solcx."""
    print("🔨 Compiling smart contract...")
    
    # Install solc version if not already installed
    print("   Installing Solidity compiler 0.8.19...")
    install_solc('0.8.19')
    
    compiled_sol = compile_source(
        source_code,
        output_values=["abi", "bin"],
        solc_version="0.8.19"
    )
    
    # Get contract data
    contract_id, contract_interface = compiled_sol.popitem()
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']
    
    print(f"✅ Contract compiled successfully")
    print(f"   Name: {contract_id}")
    print(f"   ABI entries: {len(abi)}")
    
    return {'abi': abi, 'bytecode': bytecode}


def deploy_contract(eth: EthereumConnector, contract_data: dict) -> dict:
    """Deploy contract to Sepolia."""
    print("\n🚀 Deploying contract to Sepolia...")
    print(f"   Gas price: {eth.get_gas_price_gwei()} Gwei")
    print(f"   Account: {eth.get_account_address()}")
    print(f"   Balance: {eth.get_account_balance()} ETH\n")
    
    contract_address = eth.deploy_contract(
        contract_data['abi'],
        contract_data['bytecode'],
        constructor_args=[]
    )
    
    return contract_address


def save_contract_info(contract_address: str, abi: list) -> None:
    """Save contract info to JSON for future use."""
    contract_info = {
        'address': contract_address,
        'abi': abi,
        'network': 'sepolia',
        'chain_id': 11155111,
    }
    
    with open('contract_info.json', 'w') as f:
        json.dump(contract_info, f, indent=2)
    
    print(f"✅ Contract info saved to contract_info.json")


def main():
    print("\n" + "="*70)
    print("📝 VALIDATOR REPUTATION CONTRACT DEPLOYMENT")
    print("="*70 + "\n")
    
    try:
        # Step 1: Read contract source
        print("📂 Reading contract source...")
        source_code = read_contract_source()
        print(f"✅ Contract loaded ({len(source_code)} bytes)\n")
        
        # Step 2: Compile contract
        contract_data = compile_contract(source_code)
        
        # Step 3: Connect to Sepolia
        print("\n🔗 Connecting to Ethereum Sepolia...")
        eth = EthereumConnector()
        
        # Step 4: Deploy contract
        contract_address = deploy_contract(eth, contract_data)
        
        # Step 5: Save contract info
        save_contract_info(contract_address, contract_data['abi'])
        
        print("\n" + "="*70)
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"\n📍 Contract Address: {contract_address}")
        print(f"\n✨ Next steps:")
        print(f"   1. Save this address: {contract_address}")
        print(f"   2. View on Sepolia Etherscan:")
        print(f"      https://sepolia.etherscan.io/address/{contract_address}")
        print(f"   3. Run: python interact_contract.py\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ DEPLOYMENT FAILED")
        print("="*70)
        print(f"\n{type(e).__name__}: {e}\n")
        print("Troubleshooting:")
        print("1. Install solcx: pip install py-solcx")
        print("2. Make sure ValidatorReputation.sol exists")
        print("3. Check your Sepolia ETH balance")
        print("4. Check gas prices\n")


if __name__ == "__main__":
    main()
