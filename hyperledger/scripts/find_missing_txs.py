#!/usr/bin/env python3
"""
Find Missing Transactions - Diagnostic Tool
Specifically looking for transactions from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
"""
from web3 import Web3
import json

# Configuration
RPC_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Target addresses
SENDER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
RECIPIENT1 = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
RECIPIENT2 = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"

def check_account_status():
    """Check current status of all accounts"""
    print("🔍 Account Status Check")
    print("=" * 60)
    
    accounts = {
        "Sender": SENDER,
        "Recipient 1": RECIPIENT1, 
        "Recipient 2": RECIPIENT2
    }
    
    for name, address in accounts.items():
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')
        nonce = w3.eth.get_transaction_count(address)
        
        print(f"{name} ({address}):")
        print(f"  💰 Balance: {balance_eth:.6f} UCASH")
        print(f"  🔢 Nonce: {nonce} transactions sent")
        print()

def scan_recent_blocks_detailed(blocks_to_scan=50):
    """Detailed scan of recent blocks"""
    print(f"🔍 Detailed Block Scan (Last {blocks_to_scan} blocks)")
    print("=" * 60)
    
    current_block = w3.eth.block_number
    start_block = max(0, current_block - blocks_to_scan)
    
    print(f"Scanning blocks {start_block} to {current_block}")
    print(f"Current block: {current_block}")
    print()
    
    all_transactions = []
    sender_transactions = []
    blocks_with_txs = []
    
    for block_num in range(start_block, current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            if len(block.transactions) > 0:
                blocks_with_txs.append(block_num)
                print(f"📦 Block {block_num}: {len(block.transactions)} transactions")
                
                for i, tx in enumerate(block.transactions):
                    all_transactions.append(tx)
                    
                    print(f"  Transaction {i+1}:")
                    print(f"    Hash: {tx['hash'].hex()}")
                    print(f"    From: {tx['from']}")
                    print(f"    To: {tx.get('to', 'CONTRACT_CREATION')}")
                    print(f"    Value: {w3.from_wei(tx['value'], 'ether'):.6f} UCASH")
                    print(f"    Gas: {tx['gas']:,} @ {w3.from_wei(tx['gasPrice'], 'gwei'):.2f} gwei")
                    
                    # Check if it's from our sender
                    if tx['from'].lower() == SENDER.lower():
                        sender_transactions.append(tx)
                        print(f"    🎯 MATCH: Transaction from target sender!")
                    
                    print()
        
        except Exception as e:
            print(f"❌ Error reading block {block_num}: {e}")
    
    print(f"📊 Scan Results:")
    print(f"  Total blocks with transactions: {len(blocks_with_txs)}")
    print(f"  Total transactions found: {len(all_transactions)}")
    print(f"  Transactions from sender: {len(sender_transactions)}")
    
    if blocks_with_txs:
        print(f"  Blocks with transactions: {blocks_with_txs}")
    
    return sender_transactions

def check_by_nonce():
    """Check transactions by nonce - more reliable method"""
    print(f"\n🔢 Checking Transactions by Nonce")
    print("=" * 60)
    
    current_nonce = w3.eth.get_transaction_count(SENDER)
    print(f"Current nonce for {SENDER}: {current_nonce}")
    
    if current_nonce == 0:
        print("No transactions sent from this address yet.")
        return []
    
    print(f"This means {current_nonce} transactions have been sent from this address.")
    print("Let's try to find them...")
    
    found_transactions = []
    
    # Try to find transactions by checking recent blocks more thoroughly
    current_block = w3.eth.block_number
    
    # Go back further to find transactions
    for block_num in range(max(0, current_block - 200), current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if tx['from'].lower() == SENDER.lower():
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    
                    found_transactions.append({
                        'block': block_num,
                        'hash': tx['hash'].hex(),
                        'nonce': tx['nonce'],
                        'to': tx.get('to', 'CONTRACT_CREATION'),
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_used': receipt['gasUsed'],
                        'gas_price': w3.from_wei(tx['gasPrice'], 'gwei'),
                        'status': 'SUCCESS' if receipt['status'] == 1 else 'FAILED'
                    })
        except:
            continue
    
    print(f"\n🎯 Found {len(found_transactions)} transactions from sender:")
    
    for tx in sorted(found_transactions, key=lambda x: x['nonce']):
        print(f"  Nonce {tx['nonce']} - Block {tx['block']}")
        print(f"    To: {tx['to']}")
        print(f"    Value: {tx['value']:.6f} UCASH")
        print(f"    Hash: {tx['hash']}")
        print(f"    Status: {tx['status']}")
        print(f"    Gas: {tx['gas_used']:,} @ {tx['gas_price']:.2f} gwei")
        print()
    
    return found_transactions

def check_mempool():
    """Check if transactions are stuck in mempool"""
    print(f"\n⏳ Checking Mempool/Pending Transactions")
    print("=" * 60)
    
    try:
        # Try different methods to check pending transactions
        methods = [
            "eth_pendingTransactions",
            "txpool_content", 
            "txpool_status",
            "txpool_inspect"
        ]
        
        for method in methods:
            try:
                result = w3.manager.request_blocking(method, [])
                print(f"✅ {method}: {result}")
            except Exception as e:
                print(f"❌ {method}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Mempool check failed: {e}")

def check_specific_transaction_hash():
    """Ask user for transaction hash from MetaMask"""
    print(f"\n🔗 Check Specific Transaction Hash")
    print("=" * 60)
    print("If you have the transaction hash from MetaMask, enter it here to verify:")
    
    try:
        tx_hash = input("Enter transaction hash (or press Enter to skip): ").strip()
        
        if tx_hash:
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            
            try:
                tx = w3.eth.get_transaction(tx_hash)
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                
                print(f"✅ Transaction found!")
                print(f"  Hash: {tx['hash'].hex()}")
                print(f"  Block: {receipt['blockNumber']}")
                print(f"  From: {tx['from']}")
                print(f"  To: {tx.get('to', 'CONTRACT_CREATION')}")
                print(f"  Value: {w3.from_wei(tx['value'], 'ether'):.6f} UCASH")
                print(f"  Status: {'SUCCESS' if receipt['status'] == 1 else 'FAILED'}")
                print(f"  Gas used: {receipt['gasUsed']:,}")
                
                return tx
                
            except Exception as e:
                print(f"❌ Transaction not found: {e}")
                
    except KeyboardInterrupt:
        print("\nSkipped.")
    
    return None

def main():
    """Main diagnostic function"""
    print("🚨 Transaction Diagnostic Tool")
    print("=" * 60)
    print("Looking for transactions from 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
    print("to 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 and 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC")
    print()
    
    # 1. Check account status
    check_account_status()
    
    # 2. Scan recent blocks
    sender_txs = scan_recent_blocks_detailed(100)
    
    # 3. Check by nonce (more reliable)
    nonce_txs = check_by_nonce()
    
    # 4. Check mempool
    check_mempool()
    
    # 5. Check specific hash if available
    check_specific_transaction_hash()
    
    # Summary
    print(f"\n📊 Final Summary")
    print("=" * 60)
    
    if sender_txs or nonce_txs:
        print("✅ Transactions found! Your blockchain is working correctly.")
        print("The issue might be with log filtering or scanning range.")
    else:
        print("❌ No transactions found in the scanned range.")
        print("Possible causes:")
        print("  1. Transactions are in blocks outside our scan range")
        print("  2. Transactions failed and weren't mined")
        print("  3. MetaMask is connected to a different network")
        print("  4. There's a network configuration issue")
    
    print(f"\n💡 Next steps:")
    print("1. Check MetaMask network settings (should be localhost:8545, Chain ID 1337)")
    print("2. Verify the transaction hash in MetaMask activity tab")
    print("3. Check if transactions are pending or failed")
    print("4. Run this script again with the specific transaction hash")

if __name__ == "__main__":
    main()
