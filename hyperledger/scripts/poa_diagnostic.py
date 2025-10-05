#!/usr/bin/env python3
"""
PoA Chain Transaction Diagnostic Tool
Specifically for Clique Proof of Authority chains
"""
from web3 import Web3
import time

# Configuration
RPC_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Add PoA middleware - ESSENTIAL for PoA chains!
try:
    from web3.middleware import geth_poa_middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
except ImportError:
    # For newer versions of web3.py
    from web3.middleware import ExtraDataToPOAMiddleware
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Your PoA validator
VALIDATOR_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def check_poa_status():
    """Check PoA chain status and validator info"""
    print("🏛️ PoA Chain Status")
    print("=" * 50)
    
    try:
        # Basic info
        current_block = w3.eth.block_number
        chain_id = w3.eth.chain_id
        
        print(f"Chain ID: {chain_id}")
        print(f"Current block: {current_block}")
        
        # Get latest block details
        latest_block = w3.eth.get_block('latest')
        print(f"Latest block hash: {latest_block['hash'].hex()}")
        print(f"Block timestamp: {latest_block['timestamp']}")
        print(f"Block miner/validator: {latest_block['miner']}")
        print(f"Gas used: {latest_block['gasUsed']:,} / {latest_block['gasLimit']:,}")
        
        # Check if our validator is the active one
        if latest_block['miner'].lower() == VALIDATOR_ADDRESS.lower():
            print("✅ Our validator is actively sealing blocks!")
        else:
            print(f"⚠️ Block sealed by different validator: {latest_block['miner']}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error checking PoA status: {e}")
        return False

def check_clique_signers():
    """Check Clique signers/validators"""
    print("👥 Clique Validators")
    print("=" * 50)
    
    try:
        # Try to get clique signers
        result = w3.manager.request_blocking("clique_getSigners", ["latest"])
        print(f"Active signers: {result}")
        
        for signer in result:
            if signer.lower() == VALIDATOR_ADDRESS.lower():
                print(f"✅ {signer} - Our validator (ACTIVE)")
            else:
                print(f"📝 {signer} - Other validator")
        
        print()
        
    except Exception as e:
        print(f"⚠️ Could not get clique signers: {e}")
        print("This might be normal if clique API is not enabled.")

def monitor_block_sealing(duration=30):
    """Monitor block sealing in real-time"""
    print(f"⏱️ Monitoring Block Sealing ({duration}s)")
    print("=" * 50)
    
    start_time = time.time()
    last_block = w3.eth.block_number
    blocks_by_our_validator = 0
    total_blocks = 0
    
    print(f"Starting at block {last_block}")
    print("Watching for new blocks...\n")
    
    try:
        while time.time() - start_time < duration:
            current_block = w3.eth.block_number
            
            if current_block > last_block:
                # New block found
                for block_num in range(last_block + 1, current_block + 1):
                    total_blocks += 1
                    block = w3.eth.get_block(block_num)
                    
                    validator = block['miner']
                    tx_count = len(block.transactions) if hasattr(block, 'transactions') else 0
                    
                    if validator.lower() == VALIDATOR_ADDRESS.lower():
                        blocks_by_our_validator += 1
                        validator_status = "✅ OUR VALIDATOR"
                    else:
                        validator_status = "📝 Other validator"
                    
                    print(f"📦 Block {block_num}: {validator_status}")
                    print(f"   Validator: {validator}")
                    print(f"   Transactions: {tx_count}")
                    print(f"   Timestamp: {block['timestamp']}")
                    
                    # If there are transactions, show them
                    if tx_count > 0:
                        block_full = w3.eth.get_block(block_num, full_transactions=True)
                        for i, tx in enumerate(block_full.transactions):
                            print(f"   TX {i+1}: {tx['hash'].hex()}")
                            print(f"          From: {tx['from']}")
                            print(f"          To: {tx.get('to', 'CONTRACT')}")
                            print(f"          Value: {w3.from_wei(tx['value'], 'ether'):.6f} UCASH")
                    print()
                
                last_block = current_block
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")
    
    print(f"\n📊 Sealing Summary:")
    print(f"Total new blocks: {total_blocks}")
    print(f"Blocks by our validator: {blocks_by_our_validator}")
    if total_blocks > 0:
        percentage = (blocks_by_our_validator / total_blocks) * 100
        print(f"Our validator percentage: {percentage:.1f}%")
    
    return total_blocks > 0

def check_validator_account():
    """Check validator account status"""
    print("🔑 Validator Account Status")
    print("=" * 50)
    
    balance = w3.eth.get_balance(VALIDATOR_ADDRESS)
    balance_eth = w3.from_wei(balance, 'ether')
    nonce = w3.eth.get_transaction_count(VALIDATOR_ADDRESS)
    
    print(f"Validator: {VALIDATOR_ADDRESS}")
    print(f"Balance: {balance_eth:.6f} UCASH")
    print(f"Nonce: {nonce} (transactions sent)")
    print()
    
    return balance_eth, nonce

def test_transaction_from_validator():
    """Send a test transaction from the validator account"""
    print("🧪 Test Transaction from Validator")
    print("=" * 50)
    
    PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    TO_ADDRESS = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    
    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        
        # Get current status
        balance = w3.eth.get_balance(account.address)
        nonce = w3.eth.get_transaction_count(account.address)
        
        print(f"From: {account.address}")
        print(f"To: {TO_ADDRESS}")
        print(f"Current balance: {w3.from_wei(balance, 'ether'):.6f} UCASH")
        print(f"Current nonce: {nonce}")
        
        # Create transaction
        transaction = {
            'to': TO_ADDRESS,
            'value': w3.to_wei(0.1, 'ether'),
            'gas': 21000,
            'gasPrice': w3.to_wei(2000, 'gwei'),  # Match your min gas price
            'nonce': nonce,
            'chainId': 1337
        }
        
        print(f"Sending 0.1 UCASH...")
        
        # Sign and send
        signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"✅ Transaction sent: {tx_hash.hex()}")
        print("⏳ Waiting for confirmation...")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
        print(f"Gas used: {receipt.gasUsed:,}")
        print(f"Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🏛️ PoA Chain Diagnostic Tool")
    print("=" * 60)
    print("Checking Clique Proof of Authority chain status...")
    print()
    
    # 1. Check basic PoA status
    poa_ok = check_poa_status()
    
    if not poa_ok:
        print("❌ Basic PoA checks failed. Chain might not be running properly.")
        return
    
    # 2. Check validator info
    check_validator_account()
    
    # 3. Check clique signers
    check_clique_signers()
    
    # 4. Monitor block sealing
    print("Starting block sealing monitor...")
    blocks_produced = monitor_block_sealing(15)
    
    if not blocks_produced:
        print("⚠️ No new blocks produced during monitoring!")
        print("This indicates the PoA validator might not be working properly.")
    
    # 5. Test transaction
    print("\n" + "="*60)
    choice = input("Send a test transaction? (y/n): ").lower().strip()
    
    if choice == 'y':
        success = test_transaction_from_validator()
        
        if success:
            print("\n✅ Transaction successful! Your PoA chain is working.")
            print("If transactions aren't showing in logs, check the log level configuration.")
        else:
            print("\n❌ Transaction failed. There might be a PoA configuration issue.")
    
    print("\n🎯 PoA Chain Analysis Complete!")

if __name__ == "__main__":
    main()
