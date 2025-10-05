#!/usr/bin/env python3
"""
Wallet Generation Script for u.chain
Generates deterministic wallets from seed phrases for testing and development
"""

import json
from mnemonic import Mnemonic
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic, seed_from_mnemonic, key_from_seed
import os

# Enable unaudited HD wallet features
Account.enable_unaudited_hdwallet_features()

class WalletGenerator:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.wallets = []
        
    def generate_wallet_from_seed(self, seed_phrase, account_index=0, name=""):
        """Generate a wallet from a seed phrase"""
        if not self.mnemo.check(seed_phrase):
            raise ValueError("Invalid mnemonic seed phrase")
            
        # Generate account from seed phrase using BIP44 derivation path
        account = Account.from_mnemonic(seed_phrase, account_path=f"m/44'/60'/0'/0/{account_index}")
        
        wallet_info = {
            "name": name or f"Account_{account_index}",
            "address": account.address,
            "private_key": account.key.hex(),
            "seed_phrase": seed_phrase,
            "derivation_path": f"m/44'/60'/0'/0/{account_index}",
            "account_index": account_index
        }
        
        self.wallets.append(wallet_info)
        return wallet_info
    
    def generate_multiple_accounts_from_seed(self, seed_phrase, count=5, names=None):
        """Generate multiple accounts from the same seed phrase"""
        accounts = []
        for i in range(count):
            name = names[i] if names and i < len(names) else f"Account_{i}"
            wallet = self.generate_wallet_from_seed(seed_phrase, i, name)
            accounts.append(wallet)
        return accounts
    
    def create_genesis_alloc(self, balance_eth="1000"):
        """Create genesis allocation from generated wallets"""
        balance_wei = str(int(float(balance_eth) * 10**18))
        alloc = {}
        
        for wallet in self.wallets:
            alloc[wallet["address"]] = {"balance": balance_wei}
            
        return alloc
    
    def save_wallets_config(self, filename="wallets_config.json"):
        """Save wallet configuration to JSON file"""
        config = {
            "network": "u.chain-devnet",
            "chain_id": 1337,
            "wallets": self.wallets,
            "genesis_alloc": self.create_genesis_alloc()
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config

def main():
    print("🏦 u.chain Wallet Generator")
    print("=" * 40)
    
    generator = WalletGenerator()
    
    # Predefined seed phrases for consistent testing
    test_seeds = [
        {
            "name": "Treasury",
            "seed": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            "accounts": ["Treasury_Main", "Treasury_Reserve", "Treasury_Dev"]
        },
        {
            "name": "Validators",
            "seed": "test test test test test test test test test test test junk",
            "accounts": ["Validator_1", "Validator_2", "Validator_3"]
        },
        {
            "name": "Users",
            "seed": "void come effort suffer camp survey warrior heavy shoot primary clutch crush open amazing screen patrol group space point ten exist slush involve unfold",
            "accounts": ["User_Alice", "User_Bob", "User_Charlie", "User_Dave", "User_Eve"]
        }
    ]
    
    print("Generating wallets from predefined seeds...")
    
    for seed_group in test_seeds:
        print(f"\n📝 Generating {seed_group['name']} accounts...")
        accounts = generator.generate_multiple_accounts_from_seed(
            seed_group["seed"], 
            len(seed_group["accounts"]), 
            seed_group["accounts"]
        )
        
        for account in accounts:
            print(f"  ✅ {account['name']}: {account['address']}")
    
    # Save configuration
    config_file = "config/wallets_config.json"
    os.makedirs("config", exist_ok=True)
    
    config = generator.save_wallets_config(config_file)
    print(f"\n💾 Saved wallet configuration to: {config_file}")
    
    # Generate updated genesis file
    genesis_file = "genesis_with_wallets.json"
    
    # Read existing genesis template
    try:
        with open("genesis.json", 'r') as f:
            genesis = json.load(f)
    except:
        # Fallback genesis structure
        genesis = {
            "config": {
                "chainId": 1337,
                "constantinopleBlock": 0,
                "petersburgBlock": 0,
                "istanbulBlock": 0,
                "muirGlacierBlock": 0,
                "berlinBlock": 0,
                "londonBlock": 0,
                "arrowGlacierBlock": 0,
                "grayGlacierBlock": 0,
                "bellatrixBlock": 0,
                "capellaBlock": 0,
                "denebBlock": 0,
                "terminalTotalDifficulty": 0,
                "terminalBlockNumber": 0,
                "terminalBlockHash": "0x0000000000000000000000000000000000000000000000000000000000000000"
            },
            "nonce": "0x0",
            "timestamp": "0x61668800",
            "gasLimit": "0x47b784",
            "difficulty": "0x1",
            "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "coinbase": "0x0000000000000000000000000000000000000000",
            "alloc": {}
        }
    
    # Update alloc with generated wallets
    genesis["alloc"] = config["genesis_alloc"]
    
    with open(genesis_file, 'w') as f:
        json.dump(genesis, f, indent=2)
    
    print(f"💎 Generated genesis file with wallet allocations: {genesis_file}")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"  • Generated {len(generator.wallets)} wallet accounts")
    print(f"  • Each account funded with 1000 UCASH")
    print(f"  • Chain ID: 1337")
    print(f"  • All accounts use standard BIP44 derivation")
    
    print(f"\n🔐 Seed Phrases (SAVE THESE SECURELY):")
    seen_seeds = set()
    for wallet in generator.wallets:
        seed = wallet["seed_phrase"]
        if seed not in seen_seeds:
            print(f"  • {seed}")
            seen_seeds.add(seed)
    
    return config

if __name__ == "__main__":
    main()
