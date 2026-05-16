"""
Ethereum Sepolia Connection Module

Handles all connections to the real Ethereum Sepolia testnet.
Uses Web3.py to interact with blockchain.
"""

from __future__ import annotations

import os
from typing import Optional
from dotenv import load_dotenv
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import json

# Load environment variables
load_dotenv()


class EthereumConnector:
    """
    Manages connection to Ethereum Sepolia testnet.
    
    Features:
    - Connect to Sepolia RPC endpoint
    - Manage wallet/account
    - Deploy smart contracts
    - Call smart contract functions
    - Read blockchain data
    """
    
    def __init__(self) -> None:
        """Initialize Ethereum Sepolia connection."""
        self.rpc_url = os.getenv("SEPOLIA_RPC_URL")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.chain_id = int(os.getenv("CHAIN_ID", "11155111"))
        
        if not self.rpc_url:
            raise ValueError("SEPOLIA_RPC_URL not found in .env")
        
        # Connect to Sepolia
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Sepolia testnet")
        
        print(f"✅ Connected to Sepolia (Chain ID: {self.chain_id})")
        print(f"   RPC: {self.rpc_url}")
        
        # Set up account if private key provided
        self.account: Optional[Account] = None
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            print(f"✅ Account loaded: {self.account.address}")
        else:
            print("⚠️  No private key provided. Some operations will be read-only.")
    
    def get_account_balance(self) -> float:
        """Get balance of connected account in ETH."""
        if not self.account:
            raise ValueError("No account connected. Provide PRIVATE_KEY in .env")
        
        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    def get_account_address(self) -> str:
        """Get address of connected account."""
        if not self.account:
            raise ValueError("No account connected. Provide PRIVATE_KEY in .env")
        return self.account.address
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei."""
        return self.w3.eth.gas_price
    
    def get_gas_price_gwei(self) -> float:
        """Get current gas price in Gwei."""
        return float(self.w3.from_wei(self.w3.eth.gas_price, 'gwei'))
    
    def get_latest_block(self) -> dict:
        """Get latest block information."""
        block = self.w3.eth.get_block('latest')
        return {
            'number': block['number'],
            'timestamp': block['timestamp'],
            'miner': block['miner'],
            'gas_used': block['gasUsed'],
            'gas_limit': block['gasLimit'],
            'transactions': len(block['transactions']),
        }
    
    def get_block_transactions(self, block_number: int) -> list:
        """Get all transactions in a block."""
        block = self.w3.eth.get_block(block_number)
        transactions = []
        
        for tx_hash in block['transactions']:
            tx = self.w3.eth.get_transaction(tx_hash)
            transactions.append({
                'hash': tx['hash'].hex(),
                'from': tx['from'],
                'to': tx['to'],
                'value': float(self.w3.from_wei(tx['value'], 'ether')),
                'gas': tx['gas'],
                'gas_price': float(self.w3.from_wei(tx['gasPrice'], 'gwei')),
            })
        
        return transactions
    
    def deploy_contract(
        self,
        contract_abi: list,
        contract_bytecode: str,
        constructor_args: list | None = None,
    ) -> str:
        """
        Deploy a smart contract to Sepolia.
        
        Args:
            contract_abi: Contract ABI (from Solidity compiler)
            contract_bytecode: Contract bytecode (from Solidity compiler)
            constructor_args: Arguments to pass to constructor
            
        Returns:
            Contract address (string)
        """
        if not self.account:
            raise ValueError("No account connected. Cannot deploy contract.")
        
        print("📝 Deploying contract...")
        
        # Create contract instance
        contract = self.w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        
        # Build transaction
        constructor_args = constructor_args or []
        constructor_tx = contract.constructor(*constructor_args).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price,
        })
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(constructor_tx, self.private_key)
        
        # Send raw transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"   Transaction hash: {tx_hash.hex()}")
        print("   Waiting for confirmation...")
        
        # Wait for receipt (up to 5 minutes)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        contract_address = tx_receipt['contractAddress']
        print(f"✅ Contract deployed at: {contract_address}")
        print(f"   Block: {tx_receipt['blockNumber']}")
        
        return contract_address
    
    def get_contract(self, contract_address: str, contract_abi: list) -> Contract:
        """
        Get a contract instance for calling functions.
        
        Args:
            contract_address: Address of deployed contract
            contract_abi: Contract ABI
            
        Returns:
            Web3 Contract instance
        """
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=contract_abi
        )
    
    def call_contract_function(
        self,
        contract: Contract,
        function_name: str,
        *args
    ) -> any:
        """
        Call a read-only contract function (no gas cost).
        
        Args:
            contract: Contract instance
            function_name: Name of function to call
            *args: Function arguments
            
        Returns:
            Function return value
        """
        function = getattr(contract.functions, function_name)
        return function(*args).call()
    
    def execute_contract_function(
        self,
        contract: Contract,
        function_name: str,
        *args
    ) -> str:
        """
        Execute a contract function that modifies state (costs gas).
        
        Args:
            contract: Contract instance
            function_name: Name of function to call
            *args: Function arguments
            
        Returns:
            Transaction receipt
        """
        if not self.account:
            raise ValueError("No account connected. Cannot execute transaction.")
        
        function = getattr(contract.functions, function_name)
        
        # Build transaction
        tx = function(*args).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price,
        })
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"   Transaction sent: {tx_hash.hex()}")
        print("   Waiting for confirmation...")
        
        # Wait for receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print(f"✅ Transaction confirmed in block {tx_receipt['blockNumber']}")
        
        return tx_receipt
