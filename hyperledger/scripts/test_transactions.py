#!/usr/bin/env python3
"""
Comprehensive Blockchain Transaction Test Script
"""
import json
import time
import requests
from web3 import Web3
from eth_account import Account

# Configuration
RPC_URL = "http://localhost:8545"
CHAIN_ID = 1337

# Test accounts (from common test mnemonics)
SENDER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
RECEIVER_ADDRESS = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"

def rpc_call(method, params=None):
    """Make RPC call to the node"""
    if params is None:
        params = []
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"RPC Error: {e}")
        return None

def test_basic_connectivity():
    """Test basic RPC connectivity"""
    print("=== Testing Basic Connectivity ===")
    
    # Test block number
    result = rpc_call("eth_blockNumber")
    if result and "result" in result:
        block_num = int(result["result"], 16)
        print(f"✅ Current block: {block_num}")
    else:
        print("❌ Failed to get block number")
        return False
    
    # Test chain ID
    result = rpc_call("eth_chainId")
    if result and "result" in result:
        chain_id = int(result["result"], 16)
        print(f"✅ Chain ID: {chain_id}")
    else:
        print("❌ Failed to get chain ID")
    
    # Test network version
    result = rpc_call("net_version")
    if result and "result" in result:
        print(f"✅ Network version: {result['result']}")
    else:
        print("⚠️ Could not get network version")
    
    return True

def check_accounts():
    """Check test account balances"""
    print("\n=== Checking Account Balances ===")
    
    # Derive sender address
    sender_account = Account.from_key(SENDER_PRIVATE_KEY)
    sender_address = sender_account.address
    
    print(f"Sender: {sender_address}")
    print(f"Receiver: {RECEIVER_ADDRESS}")
    
    # Check sender balance
    result = rpc_call("eth_getBalance", [sender_address, "latest"])
    if result and "result" in result:
        sender_balance = int(result["result"], 16)
        sender_balance_eth = sender_balance / 10**18
        print(f"✅ Sender balance: {sender_balance_eth:.4f} UCASH")
    else:
        print("❌ Failed to get sender balance")
        return False
    
    # Check receiver balance
    result = rpc_call("eth_getBalance", [RECEIVER_ADDRESS, "latest"])
    if result and "result" in result:
        receiver_balance = int(result["result"], 16)
        receiver_balance_eth = receiver_balance / 10**18
        print(f"✅ Receiver balance: {receiver_balance_eth:.4f} UCASH")
    else:
        print("❌ Failed to get receiver balance")
    
    return sender_balance > 0

def send_test_transaction():
    """Send a test transaction"""
    print("\n=== Sending Test Transaction ===")
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        # Setup accounts
        sender_account = Account.from_key(SENDER_PRIVATE_KEY)
        sender_address = sender_account.address
        
        # Get nonce
        nonce = w3.eth.get_transaction_count(sender_address)
        print(f"Sender nonce: {nonce}")
        
        # Get gas price
        gas_price = w3.eth.gas_price
        print(f"Gas price: {gas_price} wei ({gas_price / 10**9:.2f} gwei)")
        
        # Create transaction
        transaction = {
            'to': RECEIVER_ADDRESS,
            'value': w3.to_wei(0.1, 'ether'),  # Send 0.1 UCASH
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': CHAIN_ID
        }
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, SENDER_PRIVATE_KEY)
        print(f"Signed transaction hash: {signed_txn.hash.hex()}")
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"✅ Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        print("Waiting for transaction receipt...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        print(f"✅ Transaction mined in block: {receipt.blockNumber}")
        print(f"Gas used: {receipt.gasUsed}")
        print(f"Status: {'Success' if receipt.status == 1 else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return False

def monitor_blocks(duration=30):
    """Monitor new blocks for a specified duration"""
    print(f"\n=== Monitoring Blocks for {duration} seconds ===")
    
    # Get starting block
    result = rpc_call("eth_blockNumber")
    if not result or "result" not in result:
        print("❌ Failed to get starting block")
        return
    
    start_block = int(result["result"], 16)
    print(f"Starting at block: {start_block}")
    
    start_time = time.time()
    last_block = start_block
    
    while time.time() - start_time < duration:
        result = rpc_call("eth_blockNumber")
        if result and "result" in result:
            current_block = int(result["result"], 16)
            if current_block > last_block:
                print(f"📦 New block: {current_block} (+ {current_block - last_block})")
                
                # Get block details
                block_result = rpc_call("eth_getBlockByNumber", [hex(current_block), True])
                if block_result and "result" in block_result:
                    block = block_result["result"]
                    tx_count = len(block.get("transactions", []))
                    print(f"   Transactions: {tx_count}")
                    if tx_count > 0:
                        print("   Transaction details:")
                        for i, tx in enumerate(block["transactions"]):
                            print(f"     {i+1}. {tx['hash']} from {tx['from']} to {tx.get('to', 'CONTRACT')}")
                
                last_block = current_block
        
        time.sleep(2)
    
    print(f"Monitoring complete. Blocks advanced: {last_block - start_block}")

def check_docker_status():
    """Check if Docker containers are running"""
    print("\n=== Checking Docker Status ===")
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"❌ Could not check Docker status: {e}")

def main():
    """Run all tests"""
    print("🔧 Blockchain Network Test Suite")
    print("=" * 50)
    
    # Check Docker first
    check_docker_status()
    
    # Basic connectivity
    if not test_basic_connectivity():
        print("❌ Basic connectivity failed. Check if your node is running.")
        return
    
    # Check accounts
    if not check_accounts():
        print("❌ Account check failed. Check if accounts have funds.")
        return
    
    # Send test transaction
    if send_test_transaction():
        print("✅ Transaction test passed!")
    else:
        print("⚠️ Transaction test failed - this might be the issue")
    
    # Monitor for new activity
    print("\nPress Ctrl+C to skip monitoring...")
    try:
        monitor_blocks(30)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    
    print("\n🏁 Test suite complete!")

if __name__ == "__main__":
    main()
