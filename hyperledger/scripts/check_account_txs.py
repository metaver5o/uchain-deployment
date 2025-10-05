#!/usr/bin/env python3
"""
Transaction Checker for 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Comprehensive transaction history and activity monitor
"""
from web3 import Web3
import time
from datetime import datetime

# Configuration
RPC_URL = "http://localhost:8545"
TARGET_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_account_info():
    """Get basic account information"""
    print(f"🏦 Account Information")
    print("=" * 50)
    print(f"Address: {TARGET_ADDRESS}")
    
    # Balance
    balance = w3.eth.get_balance(TARGET_ADDRESS)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_eth:.6f} UCASH")
    
    # Nonce (transaction count)
    nonce = w3.eth.get_transaction_count(TARGET_ADDRESS)
    print(f"🔢 Nonce (transactions sent): {nonce}")
    
    # Current block
    current_block = w3.eth.block_number
    print(f"📦 Current block: {current_block}")
    
    return balance, nonce, current_block

def scan_transaction_history(blocks_to_scan=100):
    """Scan for all transactions involving this address"""
    print(f"\n🔍 Transaction History Scan")
    print("=" * 50)
    
    current_block = w3.eth.block_number
    start_block = max(0, current_block - blocks_to_scan)
    
    print(f"Scanning blocks {start_block} to {current_block} ({blocks_to_scan} blocks)")
    
    sent_transactions = []
    received_transactions = []
    total_gas_used = 0
    
    for block_num in range(start_block, current_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                # Transaction sent FROM this address
                if tx['from'].lower() == TARGET_ADDRESS.lower():
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    gas_used = receipt['gasUsed']
                    gas_cost = gas_used * tx['gasPrice']
                    total_gas_used += gas_cost
                    
                    sent_transactions.append({
                        'block': block_num,
                        'timestamp': block['timestamp'],
                        'hash': tx['hash'].hex(),
                        'to': tx.get('to', 'CONTRACT_CREATION'),
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_used': gas_used,
                        'gas_price': w3.from_wei(tx['gasPrice'], 'gwei'),
                        'gas_cost': w3.from_wei(gas_cost, 'ether'),
                        'status': 'SUCCESS' if receipt['status'] == 1 else 'FAILED',
                        'nonce': tx['nonce']
                    })
                
                # Transaction received BY this address
                elif tx.get('to') and tx['to'].lower() == TARGET_ADDRESS.lower():
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    
                    received_transactions.append({
                        'block': block_num,
                        'timestamp': block['timestamp'],
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'value': w3.from_wei(tx['value'], 'ether'),
                        'gas_price': w3.from_wei(tx['gasPrice'], 'gwei'),
                        'status': 'SUCCESS' if receipt['status'] == 1 else 'FAILED'
                    })
        except Exception as e:
            # Skip blocks that can't be read
            continue
    
    # Display results
    print(f"\n📤 SENT Transactions: {len(sent_transactions)}")
    if sent_transactions:
        total_sent = sum(tx['value'] for tx in sent_transactions)
        total_gas_fees = w3.from_wei(total_gas_used, 'ether')
        
        print(f"   Total sent: {total_sent:.6f} UCASH")
        print(f"   Total gas fees: {total_gas_fees:.6f} UCASH")
        print(f"   Total cost: {total_sent + total_gas_fees:.6f} UCASH")
        print()
        
        for tx in reversed(sent_transactions):  # Show newest first
            dt = datetime.fromtimestamp(tx['timestamp'])
            status_emoji = "✅" if tx['status'] == 'SUCCESS' else "❌"
            print(f"   {status_emoji} Block {tx['block']} ({dt.strftime('%H:%M:%S')})")
            print(f"      💸 Sent {tx['value']:.6f} UCASH to {tx['to']}")
            print(f"      🔗 Hash: {tx['hash']}")
            print(f"      ⛽ Gas: {tx['gas_used']:,} units @ {tx['gas_price']:.2f} gwei = {tx['gas_cost']:.6f} UCASH")
            print(f"      🔢 Nonce: {tx['nonce']}")
            print()
    else:
        print("   No sent transactions found")
    
    print(f"📥 RECEIVED Transactions: {len(received_transactions)}")
    if received_transactions:
        total_received = sum(tx['value'] for tx in received_transactions)
        print(f"   Total received: {total_received:.6f} UCASH")
        print()
        
        for tx in reversed(received_transactions):  # Show newest first
            dt = datetime.fromtimestamp(tx['timestamp'])
            status_emoji = "✅" if tx['status'] == 'SUCCESS' else "❌"
            print(f"   {status_emoji} Block {tx['block']} ({dt.strftime('%H:%M:%S')})")
            print(f"      💰 Received {tx['value']:.6f} UCASH from {tx['from']}")
            print(f"      🔗 Hash: {tx['hash']}")
            print()
    else:
        print("   No received transactions found")
    
    return sent_transactions, received_transactions

def send_test_transaction(to_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8", amount=0.1):
    """Send a test transaction from this account"""
    print(f"\n🧪 Sending Test Transaction")
    print("=" * 50)
    
    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        
        # Check balance first
        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, 'ether')
        
        if balance_eth < amount:
            print(f"❌ Insufficient balance: {balance_eth:.6f} UCASH (need {amount} UCASH)")
            return False
        
        # Get current gas price and nonce
        gas_price = w3.eth.gas_price
        nonce = w3.eth.get_transaction_count(account.address)
        
        print(f"From: {account.address}")
        print(f"To: {to_address}")
        print(f"Amount: {amount} UCASH")
        print(f"Gas price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei")
        print(f"Nonce: {nonce}")
        
        # Create transaction
        transaction = {
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': 1337
        }
        
        # Sign and send
        signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"✅ Transaction sent: {tx_hash.hex()}")
        print("⏳ Waiting for confirmation...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        gas_used = receipt['gasUsed']
        gas_cost = gas_used * gas_price
        gas_cost_eth = w3.from_wei(gas_cost, 'ether')
        
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
        print(f"⛽ Gas used: {gas_used:,} units")
        print(f"💸 Gas cost: {gas_cost_eth:.6f} UCASH")
        print(f"💰 Total cost: {amount + gas_cost_eth:.6f} UCASH")
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return False

def monitor_live_activity(duration=60):
    """Monitor live transaction activity for this address"""
    print(f"\n👁️ Live Transaction Monitor")
    print("=" * 50)
    print(f"Monitoring {TARGET_ADDRESS} for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    start_time = time.time()
    last_block = w3.eth.block_number
    
    try:
        while time.time() - start_time < duration:
            current_block = w3.eth.block_number
            
            # Check new blocks
            if current_block > last_block:
                for block_num in range(last_block + 1, current_block + 1):
                    try:
                        block = w3.eth.get_block(block_num, full_transactions=True)
                        
                        for tx in block.transactions:
                            # Check if our address is involved
                            if (tx['from'].lower() == TARGET_ADDRESS.lower() or 
                                (tx.get('to') and tx['to'].lower() == TARGET_ADDRESS.lower())):
                                
                                direction = "SENT" if tx['from'].lower() == TARGET_ADDRESS.lower() else "RECEIVED"
                                value = w3.from_wei(tx['value'], 'ether')
                                
                                print(f"🚨 NEW TRANSACTION - Block {block_num}")
                                print(f"   {direction}: {value:.6f} UCASH")
                                print(f"   Hash: {tx['hash'].hex()}")
                                print(f"   From: {tx['from']}")
                                print(f"   To: {tx.get('to', 'CONTRACT')}")
                                print()
                    except:
                        continue
                
                last_block = current_block
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    
    print(f"📊 Monitoring complete. Checked {last_block - (w3.eth.block_number - int(duration/15))} new blocks.")

def main():
    """Main function"""
    print("🔍 Transaction Checker for 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
    print("=" * 70)
    
    # Get account info
    balance, nonce, current_block = get_account_info()
    
    # Scan transaction history
    sent_txs, received_txs = scan_transaction_history(100)
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 50)
    print(f"Total transactions sent: {len(sent_txs)}")
    print(f"Total transactions received: {len(received_txs)}")
    print(f"Current balance: {w3.from_wei(balance, 'ether'):.6f} UCASH")
    
    # Interactive options
    print(f"\n🎯 Options:")
    print("1. Send test transaction")
    print("2. Monitor live activity")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            to_addr = input("Enter recipient address (or press Enter for default): ").strip()
            if not to_addr:
                to_addr = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
            
            amount = input("Enter amount in UCASH (or press Enter for 0.1): ").strip()
            if not amount:
                amount = 0.1
            else:
                amount = float(amount)
            
            send_test_transaction(to_addr, amount)
            
        elif choice == "2":
            duration = input("Monitor duration in seconds (or press Enter for 60): ").strip()
            if not duration:
                duration = 60
            else:
                duration = int(duration)
            
            monitor_live_activity(duration)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
