#!/usr/bin/env python3
"""
Check transaction history and balances for both accounts
"""
from web3 import Web3
import requests

# Configuration
RPC_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Accounts
SENDER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
RECEIVER = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

def check_balances():
    """Check current balances"""
    print("=== Current Balances ===")
    
    sender_balance = w3.eth.get_balance(SENDER)
    receiver_balance = w3.eth.get_balance(RECEIVER)
    
    print(f"Sender ({SENDER}): {w3.from_wei(sender_balance, 'ether'):.4f} UCASH")
    print(f"Receiver ({RECEIVER}): {w3.from_wei(receiver_balance, 'ether'):.4f} UCASH")
    
    return sender_balance, receiver_balance

def get_transaction_history(address, start_block=0, end_block='latest'):
    """Get all transactions involving an address"""
    print(f"\n=== Transaction History for {address} ===")
    
    # Get current block number
    current_block = w3.eth.block_number
    if end_block == 'latest':
        end_block = current_block
    
    print(f"Scanning blocks {start_block} to {end_block}...")
    
    transactions = []
    
    # Scan recent blocks for transactions
    for block_num in range(max(0, current_block - 50), current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                # Check if this address is involved in the transaction
                if (tx['from'].lower() == address.lower() or 
                    (tx.get('to') and tx['to'].lower() == address.lower())):
                    
                    direction = "SENT" if tx['from'].lower() == address.lower() else "RECEIVED"
                    
                    transactions.append({
                        'block': block_num,
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'to': tx.get('to', 'CONTRACT'),
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'direction': direction,
                        'gas_used': tx.get('gas', 0),
                        'gas_price': tx.get('gasPrice', 0)
                    })
        except Exception as e:
            continue
    
    if transactions:
        print(f"Found {len(transactions)} transactions:")
        for tx in transactions:
            print(f"  Block {tx['block']}: {tx['direction']} {tx['value']:.4f} UCASH")
            print(f"    Hash: {tx['hash']}")
            print(f"    From: {tx['from']}")
            print(f"    To: {tx['to']}")
            print()
    else:
        print("No transactions found.")
    
    return transactions

def send_test_to_receiver():
    """Send a test transaction TO the receiver account"""
    print("\n=== Sending Test Transaction TO Receiver ===")
    
    try:
        # Private key for sender
        sender_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        sender_account = w3.eth.account.from_key(sender_key)
        
        # Get nonce
        nonce = w3.eth.get_transaction_count(sender_account.address)
        
        # Create transaction to receiver
        transaction = {
            'to': RECEIVER,
            'value': w3.to_wei(0.5, 'ether'),  # Send 0.5 UCASH
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': 1337
        }
        
        # Sign and send
        signed_txn = w3.eth.account.sign_transaction(transaction, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"Transaction sent: {tx_hash.hex()}")
        print("Waiting for confirmation...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔍 MetaMask Transaction Visibility Test")
    print("=" * 50)
    
    # Check initial balances
    sender_bal, receiver_bal = check_balances()
    
    # Get transaction history for both accounts
    print("\n" + "="*50)
    get_transaction_history(SENDER)
    
    print("\n" + "="*50)
    get_transaction_history(RECEIVER)
    
    # Send a test transaction if receiver has no balance
    if receiver_bal == 0:
        print("\n" + "="*50)
        if send_test_to_receiver():
            print("\n=== After Transaction ===")
            check_balances()
            
            # Check history again
            print("\n" + "="*50)
            get_transaction_history(RECEIVER)

if __name__ == "__main__":
    main()
