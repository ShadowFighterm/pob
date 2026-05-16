"""
Test script to verify Ethereum Sepolia connection.

Run this to check:
- Connection to Sepolia testnet
- Wallet is loaded
- Balance is available
- Gas prices
"""

from eth_connector import EthereumConnector


def main():
    print("\n" + "="*60)
    print("🔗 ETHEREUM SEPOLIA CONNECTION TEST")
    print("="*60 + "\n")
    
    try:
        # Connect to Sepolia
        eth = EthereumConnector()
        
        # Test 1: Get account info
        print("📊 ACCOUNT INFORMATION")
        print("-" * 60)
        address = eth.get_account_address()
        print(f"Address: {address}")
        
        balance = eth.get_account_balance()
        print(f"Balance: {balance} ETH")
        
        if balance == 0:
            print("⚠️  Balance is 0 ETH! Get free Sepolia ETH from faucet:")
            print("   https://sepoliafaucet.com/")
        
        # Test 2: Get gas info
        print("\n⛽ GAS INFORMATION")
        print("-" * 60)
        gas_price = eth.get_gas_price_gwei()
        print(f"Current Gas Price: {gas_price} Gwei")
        
        # Test 3: Get latest block
        print("\n📦 LATEST BLOCK")
        print("-" * 60)
        latest_block = eth.get_latest_block()
        print(f"Block Number: {latest_block['number']}")
        print(f"Miner: {latest_block['miner']}")
        print(f"Transactions: {latest_block['transactions']}")
        print(f"Gas Used: {latest_block['gas_used']} / {latest_block['gas_limit']}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nNext step: Deploy smart contract")
        print("Run: python deploy_validator_contract.py\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR")
        print("="*60)
        print(f"\n{type(e).__name__}: {e}\n")
        print("Troubleshooting:")
        print("1. Check if PRIVATE_KEY is set in .env")
        print("2. Make sure MetaMask is on Sepolia testnet")
        print("3. Verify you have Sepolia ETH (use faucet)")
        print("4. Check internet connection\n")


if __name__ == "__main__":
    main()
