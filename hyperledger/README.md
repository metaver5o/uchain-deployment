# u.chain Dynamic Wallet System

This setup automatically generates wallets on-the-fly when launching the u.chain blockchain, making development and testing much easier.

## 🚀 Quick Start

```bash
# One-command launch (recommended)
./quickstart.sh

# Or use the interactive menu
./launch.sh
```

## 🏦 Wallet Generation Features

### Deterministic Wallets (Default)
- Uses predefined seed phrases for consistent testing
- Same addresses every time for reproducible development
- Three wallet groups: Treasury, Validators, Users

### Random Wallets
- Generates fresh random seed phrases
- Different addresses each launch
- Good for testing randomness and edge cases

## 📋 Generated Wallet Groups

### Treasury Accounts (Seed: `abandon abandon abandon...`)
- **Treasury_Main**: Primary treasury account
- **Treasury_Reserve**: Reserve funds
- **Treasury_Ops**: Operational expenses

### Validator Accounts (Seed: `test test test...`)
- **Validator_1**: Primary validator
- **Validator_2**: Secondary validator  
- **Validator_3**: Backup validator

### User Accounts (Seed: `void come effort...`)
- **User_Alice**: Test user Alice
- **User_Bob**: Test user Bob
- **User_Charlie**: Test user Charlie
- **User_Dave**: Test user Dave

Each account is pre-funded with **1000 UCASH**.

## 🛠️ Usage Options

### 1. Full Launch (Wallets + Blockchain)
```bash
./quickstart.sh
# or 
python dynamic_launcher.py
```

### 2. Generate Wallets Only
```bash
python dynamic_launcher.py --wallets-only
```

### 3. Use Random Wallets
```bash
python dynamic_launcher.py --random
```

### 4. Interactive Menu
```bash
./launch.sh
```

## 📁 Generated Files

- **`genesis.json`**: Blockchain genesis with wallet allocations
- **`WALLETS.txt`**: Quick reference for all wallet info
- **`config/wallets_config.json`**: Detailed wallet configuration
- **`config/jwtsecret.hex`**: JWT secret for consensus communication

## 🦊 MetaMask Integration

### Import via Seed Phrase (Recommended)
1. Open MetaMask
2. Click account menu → "Import Account"
3. Select "Import using account seed phrase"
4. Use one of the seed phrases from `WALLETS.txt`

### Import via Private Key
1. Copy any private key from `WALLETS.txt`
2. MetaMask → Import Account → Private Key
3. Paste the private key

### Network Configuration
- **Network Name**: u.chain Devnet
- **RPC URL**: `http://localhost:8545`
- **Chain ID**: `1337`
- **Currency Symbol**: `UCASH`

## 🔧 Development Tools

### Web3 Connection Test
```bash
source wallet_env/bin/activate
python test_web3_connection.py
```

### Wallet Manager
```bash
source wallet_env/bin/activate
python wallet_manager.py
```

### Generate Environment Variables
The wallet manager can create `.env` files and Hardhat configurations for easy integration with your dApps.

## 🐳 Docker Management

### View Logs
```bash
docker compose logs -f
```

### Stop Blockchain
```bash
docker compose down
```

### Reset Everything
```bash
docker compose down -v
rm -rf genesis.json WALLETS.txt config/wallets_config.json
```

## 🔐 Security Notes

- **Development Only**: These are test wallets with known seed phrases
- **Never use in production**: Generate fresh seeds for mainnet
- **Backup Important**: Save your seed phrases securely
- **Private Keys**: Never share private keys in production

## 🎯 Advanced Usage

### Custom Wallet Configuration
Edit `dynamic_launcher.py` to customize:
- Number of wallets per group
- Initial balance amounts  
- Wallet naming schemes
- Seed phrase sources

### Integration with dApps
Use the generated `config/wallets_config.json` to automatically configure your development environment.

### Automated Testing
The deterministic wallets make automated testing easier since you get the same addresses every time.

## 🐛 Troubleshooting

### Docker Issues
```bash
# Restart Docker daemon
# Check Docker compose version
docker compose version
```

### Python Environment
```bash
# Recreate virtual environment
rm -rf wallet_env
python3 -m venv wallet_env
source wallet_env/bin/activate
pip install -r requirements.txt
```

### Genesis File Issues
```bash
# Regenerate genesis file
python dynamic_launcher.py --wallets-only
```

## 📚 File Structure

```
hyperledger/
├── quickstart.sh              # One-command launch
├── launch.sh                  # Interactive menu  
├── dynamic_launcher.py        # Main wallet generator
├── wallet_manager.py          # Wallet management tools
├── generate_wallets.py        # Original generator
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Blockchain configuration
├── genesis.json              # Generated genesis file
├── WALLETS.txt               # Quick wallet reference
├── config/
│   ├── wallets_config.json   # Detailed wallet config
│   ├── jwtsecret.hex         # JWT secret
│   └── besu_config.toml      # Besu configuration
└── wallet_env/               # Python virtual environment
```

## 🚀 What's Next?

1. **Launch your blockchain**: `./quickstart.sh`
2. **Import wallets to MetaMask**: Use seed phrases from `WALLETS.txt`
3. **Start building**: Connect your dApps to `http://localhost:8545`
4. **Test transactions**: Send UCASH between the generated accounts

Happy building! 🎉
