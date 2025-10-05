#!/usr/bin/env python3
"""
Wallet Import Helper for u.chain
Provides easy commands to import wallets into MetaMask and other tools
"""

import json
import qrcode
from io import StringIO
import os

def load_wallet_config():
    """Load wallet configuration from JSON file"""
    try:
        with open('config/wallets_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Wallet configuration not found. Run generate_wallets.py first.")
        return None

def print_wallet_summary(config):
    """Print a summary of all wallets"""
    print("🏦 u.chain Wallet Summary")
    print("=" * 50)
    print(f"Chain ID: {config['chain_id']}")
    print(f"Network: {config['network']}")
    print(f"Total Wallets: {len(config['wallets'])}")
    print()
    
    for wallet in config['wallets']:
        print(f"📋 {wallet['name']}")
        print(f"   Address: {wallet['address']}")
        print(f"   Private Key: {wallet['private_key']}")
        print(f"   Derivation: {wallet['derivation_path']}")
        print()

def generate_metamask_import_guide(config):
    """Generate MetaMask import instructions"""
    print("🦊 MetaMask Import Guide")
    print("=" * 40)
    print()
    print("1. Open MetaMask extension")
    print("2. Click on account icon (top right)")
    print("3. Select 'Import Account'")
    print("4. Choose 'Private Key' as import type")
    print("5. Copy-paste one of these private keys:")
    print()
    
    for wallet in config['wallets']:
        print(f"   {wallet['name']}: {wallet['private_key']}")
    
    print()
    print("6. Or use 'Import via seed phrase' with these mnemonics:")
    print()
    
    seen_seeds = set()
    for wallet in config['wallets']:
        seed = wallet['seed_phrase']
        if seed not in seen_seeds:
            print(f"   • {seed}")
            seen_seeds.add(seed)
    
    print()
    print("🌐 Network Configuration:")
    print("   Network Name: u.chain Devnet")
    print("   RPC URL: http://localhost:8545")
    print(f"   Chain ID: {config['chain_id']}")
    print("   Currency Symbol: UCASH")
    print("   Block Explorer: (Local)")

def generate_hardhat_config(config):
    """Generate Hardhat configuration snippet"""
    print("⚒️  Hardhat Configuration")
    print("=" * 30)
    
    hardhat_config = f"""
// Add this to your hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");

const accounts = [
"""
    
    for wallet in config['wallets']:
        hardhat_config += f'  "{wallet["private_key"]}", // {wallet["name"]}\n'
    
    hardhat_config += f"""];

module.exports = {{
  solidity: "0.8.19",
  networks: {{
    uchain: {{
      url: "http://localhost:8545",
      chainId: {config['chain_id']},
      accounts: accounts
    }}
  }}
}};
"""
    
    print(hardhat_config)
    
    # Save to file
    with open('hardhat-accounts.js', 'w') as f:
        f.write(hardhat_config)
    print("💾 Saved to: hardhat-accounts.js")

def generate_env_file(config):
    """Generate .env file with private keys"""
    print("📄 Environment Variables")
    print("=" * 25)
    
    env_content = f"""# u.chain Wallet Configuration
CHAIN_ID={config['chain_id']}
RPC_URL=http://localhost:8545

# Private Keys
"""
    
    for i, wallet in enumerate(config['wallets']):
        env_var_name = wallet['name'].upper().replace(' ', '_').replace('-', '_')
        env_content += f"{env_var_name}_PRIVATE_KEY={wallet['private_key']}\n"
        env_content += f"{env_var_name}_ADDRESS={wallet['address']}\n"
    
    env_content += """
# Seed Phrases (Keep Secure!)
"""
    
    seen_seeds = set()
    seed_counter = 1
    for wallet in config['wallets']:
        seed = wallet['seed_phrase']
        if seed not in seen_seeds:
            env_content += f"SEED_PHRASE_{seed_counter}=\"{seed}\"\n"
            seen_seeds.add(seed)
            seed_counter += 1
    
    print(env_content)
    
    # Save to file
    with open('wallets.env', 'w') as f:
        f.write(env_content)
    print("💾 Saved to: wallets.env")

def generate_web3_connection_script(config):
    """Generate Web3 connection test script"""
    script_content = f'''#!/usr/bin/env python3
"""
Web3 Connection Test for u.chain
"""

from web3 import Web3
import json

# Connection setup
rpc_url = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(rpc_url))

def test_connection():
    """Test connection to u.chain node"""
    try:
        if w3.is_connected():
            print("✅ Connected to u.chain node")
            print(f"Chain ID: {{w3.eth.chain_id}}")
            print(f"Latest block: {{w3.eth.block_number}}")
            return True
        else:
            print("❌ Failed to connect to u.chain node")
            return False
    except Exception as e:
        print(f"❌ Connection error: {{e}}")
        return False

def check_balances():
    """Check balances of all generated wallets"""
    if not test_connection():
        return
    
    print("\\n💰 Wallet Balances:")
    print("-" * 40)
    
    wallets = {config['wallets']}
    
    for wallet in wallets:
        try:
            balance_wei = w3.eth.get_balance(wallet['address'])
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"{{wallet['name']:15}} | {{balance_eth:>10}} UCASH | {{wallet['address']}}")
        except Exception as e:
            print(f"{{wallet['name']:15}} | ERROR: {{e}}")

def send_test_transaction():
    """Send a test transaction between wallets"""
    if not test_connection():
        return
    
    # Use first two wallets for test
    sender = {config['wallets'][0]}
    receiver = {config['wallets'][1]}
    
    print(f"\\n🔄 Test Transaction:")
    print(f"From: {{sender['name']}} ({{sender['address']}})")
    print(f"To: {{receiver['name']}} ({{receiver['address']}})")
    
    try:
        # Create account from private key
        sender_account = w3.eth.account.from_key(sender['private_key'])
        
        # Build transaction
        transaction = {{
            'to': receiver['address'],
            'value': w3.to_wei(1, 'ether'),  # Send 1 UCASH
            'gas': 21000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': w3.eth.get_transaction_count(sender['address']),
        }}
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, sender['private_key'])
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"✅ Transaction sent: {{tx_hash.hex()}}")
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Transaction confirmed in block: {{tx_receipt.blockNumber}}")
        
    except Exception as e:
        print(f"❌ Transaction failed: {{e}}")

if __name__ == "__main__":
    print("🔗 u.chain Web3 Connection Test")
    print("=" * 35)
    
    test_connection()
    check_balances()
    
    # Uncomment to test transactions
    # send_test_transaction()
'''
    
    with open('test_web3_connection.py', 'w') as f:
        f.write(script_content)
    
    print("🔗 Web3 Connection Test Script")
    print("=" * 35)
    print("💾 Saved to: test_web3_connection.py")
    print()
    print("To test the connection:")
    print("  source wallet_env/bin/activate")
    print("  python test_web3_connection.py")

def main():
    """Main menu for wallet management"""
    config = load_wallet_config()
    if not config:
        return
    
    while True:
        print("\n🏦 u.chain Wallet Manager")
        print("=" * 30)
        print("1. 📋 Show wallet summary")
        print("2. 🦊 Generate MetaMask import guide")
        print("3. ⚒️  Generate Hardhat configuration")
        print("4. 📄 Generate .env file")
        print("5. 🔗 Generate Web3 test script")
        print("6. 🚪 Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            print_wallet_summary(config)
        elif choice == '2':
            generate_metamask_import_guide(config)
        elif choice == '3':
            generate_hardhat_config(config)
        elif choice == '4':
            generate_env_file(config)
        elif choice == '5':
            generate_web3_connection_script(config)
        elif choice == '6':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
