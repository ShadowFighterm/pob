import os
import json
from web3 import Web3
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print('Failed to connect to Sepolia')
        return

    with open('contract_info.json', 'r') as f:
        contract_data = json.load(f)
    
    contract_address = contract_data['address']
    contract_abi = contract_data['abi']
    
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    current_block = w3.eth.block_number
    # Search the last 50,000 blocks as per the node limit
    start_block = max(0, current_block - 49999)

    events = []
    try:
        reg_events = contract.events.ValidatorRegistered.get_logs(from_block=start_block)
        upd_events = contract.events.ValidatorUpdated.get_logs(from_block=start_block)
        events = list(reg_events) + list(upd_events)
    except Exception as e:
        print(f'Error fetching logs from block {start_block}: {e}')
        return

    total_gas_used = 0
    total_fee_eth = 0

    print(f'{"Tx Hash":<68} | {"Block":<10} | {"Gas Used":<10} | {"Gas Price (Gwei)":<18} | {"Fee (ETH)"}')
    print("-" * 125)

    for event in events:
        tx_hash = event['transactionHash'].hex()
        block_number = event['blockNumber']
        
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
        gas_used = tx_receipt['gasUsed']
        
        effective_gas_price = tx_receipt.get('effectiveGasPrice', 0)
        gas_price_gwei = w3.from_wei(effective_gas_price, 'gwei')
        fee_eth = w3.from_wei(gas_used * effective_gas_price, 'ether')
        
        total_gas_used += gas_used
        total_fee_eth += fee_eth
        
        print(f'{tx_hash:<68} | {block_number:<10} | {gas_used:<10} | {gas_price_gwei:<18.4f} | {fee_eth:.10f}')

    print('\nSummary:')
    print(f'Total Interactions found (last 50,000 blocks): {len(events)}')
    print(f'Total Gas Used: {total_gas_used}')
    print(f'Total Estimated Fee: {total_fee_eth:.10f} ETH')

if __name__ == '__main__':
    main()
