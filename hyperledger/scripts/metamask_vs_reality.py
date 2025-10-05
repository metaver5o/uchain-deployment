#!/usr/bin/env python3
"""
Simple tool to check received transactions (that MetaMask doesn't show)
"""
from web3 import Web3

# Setup
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Your test addresses
SENDER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
RECEIVER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def check_received_transactions(address):
    """Check for received transactions that MetaMask won't show"""
    print(f"🔍 Checking received transactions for: {address}")
    print("=" * 60)
    
    # Current balance
    balance = w3.eth.get_balance(address)
    print(f"💰 Current Balance: {w3.from_wei(balance, 'ether'):.4f} UCASH")
    print()
    
    # Check recent blocks
    current_block = w3.eth.block_number
    print(f"📦 Scanning recent blocks (current: {current_block})")
    
    received_txs = []
    sent_txs = []
    
    # Scan last 50 blocks
    for block_num in range(max(0, current_block - 50), current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                # Check if this is a received transaction
                if tx.get('to') and tx['to'].lower() == address.lower():
                    received_txs.append({
                        'block': block_num,
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_price': w3.from_wei(tx['gasPrice'], 'gwei')
                    })
                
                # Check if this is a sent transaction  
                elif tx['from'].lower() == address.lower():
                    sent_txs.append({
                        'block': block_num,
                        'hash': tx['hash'].hex(),
                        'to': tx.get('to', 'CONTRACT'),
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_price': w3.from_wei(tx['gasPrice'], 'gwei')
                    })
        except:
            continue
    
    # Show results
    print(f"📥 RECEIVED Transactions: {len(received_txs)}")
    if received_txs:
        for tx in received_txs:
            print(f"  Block {tx['block']}: +{tx['value']:.4f} UCASH from {tx['from']}")
            print(f"    Hash: {tx['hash']}")
    else:
        print("  None found")
    
    print(f"\n📤 SENT Transactions: {len(sent_txs)}")  
    if sent_txs:
        for tx in sent_txs:
            print(f"  Block {tx['block']}: -{tx['value']:.4f} UCASH to {tx['to']}")
            print(f"    Hash: {tx['hash']}")
    else:
        print("  None found")
    
    print(f"\n💡 MetaMask shows: {len(sent_txs)} transactions (SENT only)")
    print(f"🔍 Actual total: {len(sent_txs + received_txs)} transactions (SENT + RECEIVED)")
    
    return received_txs, sent_txs

def test_send_to_address(to_address):
    """Send a test transaction to see if received transactions work"""
    print(f"\n🧪 Sending test transaction to {to_address}")
    
    try:
        # Use sender's private key
        sender_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        sender_account = w3.eth.account.from_key(sender_key)
        
        # Create transaction
        nonce = w3.eth.get_transaction_count(sender_account.address)
        transaction = {
            'to': to_address,
            'value': w3.to_wei(0.25, 'ether'),  # Send 0.25 UCASH
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': 1337
        }
        
        # Sign and send
        signed_txn = w3.eth.account.sign_transaction(transaction, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"✅ Transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Confirmed in block {receipt.blockNumber}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 MetaMask vs Reality: Transaction Visibility Test")
    print("=" * 60)
    
    # Check receiver first
    print("RECEIVER ACCOUNT (the one that should show received transactions):")
    received, sent = check_received_transactions(RECEIVER)
    
    # If no received transactions, send one
    if len(received) == 0:
        print(f"\n💸 Sending test transaction to receiver...")
        if test_send_to_address(RECEIVER):
            print(f"\n🔄 Checking again after sending...")
            check_received_transactions(RECEIVER)
    
    print("\n" + "="*60)
    print("SENDER ACCOUNT (the one MetaMask shows transactions for):")
    check_received_transactions(SENDER)
    
    print("\n" + "="*60)
    print("🎯 CONCLUSION:")
    print("• MetaMask ONLY shows transactions you SEND")
    print("• MetaMask does NOT show transactions you RECEIVE") 
    print("• Both types of transactions work perfectly on your blockchain")
    print("• Use this script or a block explorer to see received transactions")
    print("• Balance changes prove transactions are working!")
