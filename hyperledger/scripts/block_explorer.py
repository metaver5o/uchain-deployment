#!/usr/bin/env python3
"""
Simple Block Explorer - Shows ALL transactions for any address
"""
from web3 import Web3
import sys

RPC_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def explore_address(address, blocks_to_scan=300):
    """Show all transactions involving an address"""
    print(f"🔍 Block Explorer for: {address}")
    print("=" * 80)
    
    current_block = w3.eth.block_number
    start_block = max(0, current_block - blocks_to_scan)
    
    print(f"Scanning blocks {start_block} to {current_block}...")
    
    # Current balance
    balance = w3.eth.get_balance(address)
    print(f"💰 Current Balance: {w3.from_wei(balance, 'ether'):.4f} UCASH")
    print()
    
    transactions = []
    
    for block_num in range(start_block, current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if (tx['from'].lower() == address.lower() or 
                    (tx.get('to') and tx['to'].lower() == address.lower())):
                    
                    # Get transaction receipt for gas info
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    
                    tx_info = {
                        'block': block_num,
                        'timestamp': block['timestamp'],
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'to': tx.get('to', 'CONTRACT_CREATION'),
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_used': receipt['gasUsed'],
                        'gas_price': tx['gasPrice'],
                        'status': 'SUCCESS' if receipt['status'] == 1 else 'FAILED',
                        'direction': 'SENT' if tx['from'].lower() == address.lower() else 'RECEIVED'
                    }
                    transactions.append(tx_info)
        except Exception as e:
            continue
    
    if transactions:
        print(f"📋 Found {len(transactions)} transactions:")
        print()
        
        for i, tx in enumerate(reversed(transactions), 1):  # Show newest first
            direction_emoji = "📤" if tx['direction'] == 'SENT' else "📥"
            status_emoji = "✅" if tx['status'] == 'SUCCESS' else "❌"
            
            print(f"{i}. {direction_emoji} {tx['direction']} - {status_emoji} {tx['status']}")
            print(f"   💰 Amount: {tx['value']:.4f} UCASH")
            print(f"   🔗 Hash: {tx['hash']}")
            print(f"   📦 Block: {tx['block']}")
            print(f"   👤 From: {tx['from']}")
            print(f"   🎯 To: {tx['to']}")
            print(f"   ⛽ Gas Used: {tx['gas_used']:,} (Price: {w3.from_wei(tx['gas_price'], 'gwei'):.2f} gwei)")
            print()
    else:
        print("No transactions found in recent blocks.")
        print("Try increasing the scan range or check if the address is correct.")

if __name__ == "__main__":
    # Default addresses from your setup
    addresses = {
        "sender": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "receiver": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    }
    
    if len(sys.argv) > 1:
        address = sys.argv[1]
        explore_address(address)
    else:
        print("🏠 UChain Block Explorer")
        print("=" * 50)
        print("Usage examples:")
        print(f"  python3 {sys.argv[0]} 0xYourAddress")
        print()
        print("Pre-configured addresses:")
        for name, addr in addresses.items():
            print(f"  {name.capitalize()}: {addr}")
        print()
        
        # Show both accounts
        for name, addr in addresses.items():
            explore_address(addr, 50)
            print("\n" + "="*80 + "\n")
