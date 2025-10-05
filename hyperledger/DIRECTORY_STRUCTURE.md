# UChain Hyperledger Directory Structure

## 📁 Clean Directory Tree

```
hyperledger/
├── 📄 README.md                    # Main documentation
├── 🖼️  Topologia.PNG               # Network topology diagram (for README)
├── 📝 WALLETS.txt                  # Wallet addresses and info
├── 🔧 requirements.txt             # Python dependencies
├── 🚀 deploy-network.sh            # Main deployment script
├── 🎯 watch_both_nodes.sh          # Transaction monitoring script
│
├── 🐳 Docker Compose Files:
│   ├── docker-compose.yml          # Main compose (single node)
│   ├── docker-compose.server.yml   # Server node setup
│   ├── docker-compose.home.yml     # Home node setup  
│   └── docker-compose.test.yml     # Test environment (both nodes)
│
├── ⚙️ Environment Files:
│   ├── .env                        # Main environment variables
│   ├── .env.home                   # Home node specific
│   ├── .env.network                # Network configuration
│   └── .env.test                   # Test environment
│
├── 🔧 Configuration:
│   ├── config/                     # Besu configuration files
│   │   ├── genesis.json            # Genesis block config
│   │   ├── key                     # Validator private key
│   │   └── ...
│   ├── genesis.json                # Main genesis file
│   └── genesis_with_wallets.json   # Genesis with pre-funded wallets
│
├── 🧰 Development Tools:
│   ├── scripts/                    # All utility scripts (gitignored)
│   │   ├── generate_wallets.py     # Wallet generation
│   │   ├── launch.sh               # Network launcher
│   │   ├── quickstart.sh           # Quick setup
│   │   ├── poa_diagnostic.py       # PoA chain diagnostics
│   │   ├── block_explorer.py       # Simple block explorer
│   │   ├── test_transactions.py    # Transaction testing
│   │   └── ... (all diagnostic tools)
│   └── wallet_env/                 # Python virtual environment
│
└── 🚫 .gitignore                   # Git ignore rules
```

## 🎯 Core Production Files Only

The main directory now contains only essential files for:
- ✅ **Network Deployment** (docker-compose files, deploy script)
- ✅ **Configuration** (genesis, environment files)
- ✅ **Documentation** (README, topology diagram)
- ✅ **Monitoring** (watch_both_nodes.sh)

## 🧰 Development Tools

All diagnostic and utility scripts are organized in `scripts/` folder:
- 🚫 **Not tracked in git** (thanks to .gitignore)
- 🔧 **Available for development** when needed
- 🧹 **Keeps main directory clean** for production

## 🚀 Ready for Production

Your hyperledger directory is now production-ready with:
- Clean structure
- Only essential files visible
- All development tools organized
- Proper git ignore setup
