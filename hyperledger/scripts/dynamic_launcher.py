#!/usr/bin/env python3
"""
Dynamic u.chain Launcher
Generates wallets on-the-fly and creates genesis file during blockchain startup
"""

import json
import os
import sys
import subprocess
from mnemonic import Mnemonic
from eth_account import Account
import time

# Enable unaudited HD wallet features
Account.enable_unaudited_hdwallet_features()

class DynamicChainLauncher:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.wallets = []
        self.config_dir = "config"
        self.genesis_template = {
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
            "timestamp": hex(int(time.time())),
            "gasLimit": "0x47b784",
            "difficulty": "0x1",
            "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "coinbase": "0x0000000000000000000000000000000000000000",
            "alloc": {}
        }
    
    def generate_wallet_from_seed(self, seed_phrase, account_index=0, name="", balance_eth="1000"):
        """Generate a wallet from seed phrase and add to genesis allocation"""
        account = Account.from_mnemonic(seed_phrase, account_path=f"m/44'/60'/0'/0/{account_index}")
        
        wallet_info = {
            "name": name or f"Account_{account_index}",
            "address": account.address,
            "private_key": account.key.hex(),
            "seed_phrase": seed_phrase,
            "derivation_path": f"m/44'/60'/0'/0/{account_index}",
            "account_index": account_index,
            "balance_eth": balance_eth
        }
        
        self.wallets.append(wallet_info)
        return wallet_info
    
    def generate_fresh_seed(self):
        """Generate a fresh random seed phrase"""
        return self.mnemo.generate(strength=256)  # 24 words
    
    def setup_wallets(self, use_deterministic=True, wallet_count=10):
        """Setup wallets - either deterministic or random"""
        print("🏦 Setting up wallets...")
        
        if use_deterministic:
            # Use predictable seeds for consistent testing
            seeds = [
                {
                    "seed": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                    "names": ["Treasury_Main", "Treasury_Reserve", "Treasury_Ops"],
                    "count": 3
                },
                {
                    "seed": "test test test test test test test test test test test junk", 
                    "names": ["Validator_1", "Validator_2", "Validator_3"],
                    "count": 3
                },
                {
                    "seed": "void come effort suffer camp survey warrior heavy shoot primary clutch crush open amazing screen patrol group space point ten exist slush involve unfold",
                    "names": ["User_Alice", "User_Bob", "User_Charlie", "User_Dave"],
                    "count": 4
                }
            ]
        else:
            # Generate fresh random seeds
            seeds = []
            for i in range(3):  # 3 different seed groups
                fresh_seed = self.generate_fresh_seed()
                seeds.append({
                    "seed": fresh_seed,
                    "names": [f"Random_Account_{j}" for j in range(i*3, (i+1)*3)],
                    "count": 3
                })
        
        # Generate wallets from seeds
        for seed_group in seeds:
            for i in range(seed_group["count"]):
                name = seed_group["names"][i] if i < len(seed_group["names"]) else f"Account_{len(self.wallets)}"
                self.generate_wallet_from_seed(seed_group["seed"], i, name)
        
        print(f"✅ Generated {len(self.wallets)} wallet accounts")
        return self.wallets
    
    def create_genesis_file(self):
        """Create genesis file with wallet allocations"""
        print("💎 Creating genesis file with wallet allocations...")
        
        # Add wallets to genesis allocation
        for wallet in self.wallets:
            balance_wei = str(int(float(wallet["balance_eth"]) * 10**18))
            self.genesis_template["alloc"][wallet["address"]] = {"balance": balance_wei}
        
        # Save genesis file
        with open("genesis.json", 'w') as f:
            json.dump(self.genesis_template, f, indent=2)
        
        print(f"✅ Genesis file created with {len(self.wallets)} funded accounts")
    
    def create_jwt_secret(self):
        """Create JWT secret for Engine API"""
        print("🔐 Generating JWT secret...")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Generate random 32-byte hex string
        import secrets
        jwt_secret = secrets.token_hex(32)
        
        with open(f"{self.config_dir}/jwtsecret.hex", 'w') as f:
            f.write(jwt_secret)
        
        print("✅ JWT secret generated")
    
    def save_wallet_info(self):
        """Save wallet information for later use"""
        print("💾 Saving wallet information...")
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Save detailed wallet config
        wallet_config = {
            "network": "u.chain-devnet",
            "chain_id": 1337,
            "rpc_url": "http://localhost:8545",
            "timestamp": int(time.time()),
            "wallets": self.wallets
        }
        
        with open(f"{self.config_dir}/wallets_config.json", 'w') as f:
            json.dump(wallet_config, f, indent=2)
        
        # Create quick reference file
        quick_ref = "# u.chain Wallet Quick Reference\\n"
        quick_ref += f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n"
        quick_ref += f"# Chain ID: 1337\\n"
        quick_ref += f"# RPC URL: http://localhost:8545\\n\\n"
        
        quick_ref += "# SEED PHRASES (Keep Secure!)\\n"
        seen_seeds = set()
        for wallet in self.wallets:
            seed = wallet["seed_phrase"]
            if seed not in seen_seeds:
                quick_ref += f"# {seed}\\n"
                seen_seeds.add(seed)
        
        quick_ref += "\\n# ACCOUNTS\\n"
        for wallet in self.wallets:
            quick_ref += f"# {wallet['name']}:\\n"
            quick_ref += f"#   Address: {wallet['address']}\\n"
            quick_ref += f"#   Private Key: {wallet['private_key']}\\n\\n"
        
        with open("WALLETS.txt", 'w') as f:
            f.write(quick_ref)
        
        print("✅ Wallet info saved to config/wallets_config.json and WALLETS.txt")
    
    def print_wallet_summary(self):
        """Print wallet summary"""
        print("\\n🏦 Wallet Summary")
        print("=" * 50)
        
        for wallet in self.wallets:
            print(f"📋 {wallet['name']}")
            print(f"   Address: {wallet['address']}")
            print(f"   Balance: {wallet['balance_eth']} UCASH")
            print()
        
        print("🔐 Seed Phrases:")
        seen_seeds = set()
        for wallet in self.wallets:
            seed = wallet["seed_phrase"]
            if seed not in seen_seeds:
                print(f"   • {seed}")
                seen_seeds.add(seed)
        
        print("\\n🌐 Network Info:")
        print("   Chain ID: 1337")
        print("   RPC URL: http://localhost:8545")
        print("   Currency: UCASH")
    
    def launch_blockchain(self):
        """Launch the blockchain using Docker Compose"""
        print("\\n🚀 Launching u.chain blockchain...")
        
        try:
            # Launch with docker compose
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Blockchain launched successfully!")
            print("\\n📊 Container Status:")
            
            # Check container status
            status_result = subprocess.run(
                ["docker", "compose", "ps"],
                capture_output=True,
                text=True
            )
            print(status_result.stdout)
            
            print("\\n🔗 Endpoints:")
            print("   JSON-RPC: http://localhost:8545")
            print("   WebSocket: ws://localhost:8546")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to launch blockchain: {e}")
            print("Error output:", e.stderr)
            return False
    
    def full_launch_sequence(self, use_deterministic=True):
        """Complete launch sequence"""
        print("🌟 u.chain Dynamic Launcher")
        print("=" * 40)
        
        # Step 1: Setup wallets
        self.setup_wallets(use_deterministic)
        
        # Step 2: Create genesis file
        self.create_genesis_file()
        
        # Step 3: Create JWT secret
        self.create_jwt_secret()
        
        # Step 4: Save wallet info
        self.save_wallet_info()
        
        # Step 5: Print summary
        self.print_wallet_summary()
        
        # Step 6: Launch blockchain
        success = self.launch_blockchain()
        
        if success:
            print("\\n🎉 u.chain is ready!")
            print("💡 Import wallets into MetaMask using the seed phrases above")
            print("📁 Wallet details saved in WALLETS.txt and config/wallets_config.json")
        
        return success

def main():
    """Main function with CLI options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="u.chain Dynamic Launcher")
    parser.add_argument("--random", action="store_true", help="Use random seed phrases instead of deterministic ones")
    parser.add_argument("--wallets-only", action="store_true", help="Only generate wallets, don't launch blockchain")
    
    args = parser.parse_args()
    
    launcher = DynamicChainLauncher()
    
    if args.wallets_only:
        launcher.setup_wallets(not args.random)
        launcher.create_genesis_file()
        launcher.save_wallet_info()
        launcher.print_wallet_summary()
    else:
        launcher.full_launch_sequence(not args.random)

if __name__ == "__main__":
    main()
