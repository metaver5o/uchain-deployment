# UCASH Blockchain - Home Deployment

🚀 **Professional EVM L1 UCASH Node for Home Deployment**

A complete Ethereum-compatible blockchain built with Hyperledger Besu, featuring the UCASH token with ultra-low transaction fees and fast block times.

## � Features

- **EVM Compatible**: Full Ethereum Virtual Machine compatibility
- **Ultra-Low Fees**: Minimum gas price of 0.000002 UCASH per transaction
- **Fast Blocks**: 5-second block time for quick confirmations
- **MetaMask Ready**: Works seamlessly with MetaMask wallet
- **Docker Containerized**: One-command deployment
- **Pre-funded Accounts**: 10 test accounts with 1000 UCASH each

## 🏗️ Technical Specifications

- **Consensus**: Clique Proof of Authority (PoA)
- **Chain ID**: 1337
- **Currency**: UCASH
- **Block Time**: 5 seconds
- **Gas Price**: 2,000,000,000,000 wei (0.000002 UCASH)
- **Gas Limit**: 30,000,000 per block

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- MetaMask browser extension

### 1. Clone and Start
```bash
git clone <repository-url>
cd uchain-deployment/hyperledger
docker compose up -d
```

### 2. Verify Blockchain is Running
```bash
# Check if blocks are being produced
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  http://localhost:8545

# Check gas price (should return 0x1d1a94a2000 = 0.000002 UCASH)
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}' \
  http://localhost:8545
```

## 🦊 MetaMask Configuration

### Add UCASH Network
1. Open MetaMask
2. Click Networks → "Add Network" → "Add a network manually"
3. Enter the following details:

| Field | Value |
|-------|-------|
| **Network Name** | uchain-local |
| **RPC URL** | http://localhost:8545 |
| **Chain ID** | 1337 |
| **Currency Symbol** | UCASH |
| **Block Explorer URL** | *(leave empty)* |

### Import Test Accounts

Import these pre-funded accounts into MetaMask:

#### Account 1 (Miner/Validator)
- **Address**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- **Private Key**: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
- **Balance**: ~1000 UCASH

#### Account 2 (Recommended for Testing)
- **Address**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
- **Private Key**: `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d`
- **Balance**: 1000 UCASH

#### Account 3
- **Address**: `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC`
- **Private Key**: `0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a`
- **Balance**: 1000 UCASH

*Additional accounts available in the genesis configuration file.*

## 💸 Transaction Testing

1. **Import multiple accounts** into MetaMask using the private keys above
2. **Send transactions** between accounts to test functionality
3. **Verify transactions** appear as both "Sent" and "Received" in respective accounts
4. **Confirm low fees** - transactions cost only 0.000002 UCASH minimum

## �️ Development

### Project Structure
```
hyperledger/
├── docker-compose.yml     # Container orchestration
├── config/
│   ├── genesis.json       # Blockchain genesis configuration
│   ├── jwtsecret.hex     # Engine API authentication
│   └── key               # Node private key for mining
└── README.md             # This file
```

### Configuration Files

#### Genesis Configuration (`config/genesis.json`)
- Pre-funded accounts with 1000 UCASH each
- Clique PoA consensus with 5-second blocks
- EIP compatibility for modern Ethereum features

#### Docker Compose (`docker-compose.yml`)
- Hyperledger Besu execution client
- Optimized for single-node development
- Port mappings for RPC (8545) and WebSocket (8546)

## 🔧 Management Commands

### Start/Stop Blockchain
```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart with fresh data
docker compose down
docker volume rm hyperledger_besu-data
docker compose up -d
```

### Check Status
```bash
# Container status
docker compose ps

# View logs
docker compose logs besu_el --tail=20

# Check block production
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  http://localhost:8545
```

## 🌐 Network Endpoints

- **RPC Endpoint**: http://localhost:8545
- **WebSocket**: ws://localhost:8546
- **Engine API**: http://localhost:8551 (internal)

## ✅ Verification Checklist

After deployment, verify:

- [ ] Containers are running: `docker compose ps`
- [ ] Blocks are producing: Block number increases every 5 seconds
- [ ] Gas price correct: Returns `0x1d1a94a2000` (0.000002 UCASH)
- [ ] MetaMask connects successfully to localhost:8545
- [ ] Test accounts imported and showing 1000 UCASH balance
- [ ] Transactions confirm within 5-10 seconds
- [ ] Both "Sent" and "Received" transactions appear in MetaMask

## � Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check Docker is running
docker ps

# Remove old volumes and restart
docker compose down
docker volume prune
docker compose up -d
```

**No blocks producing:**
```bash
# Check Besu logs for errors
docker compose logs besu_el

# Verify genesis configuration is valid
cat config/genesis.json | jq .
```

**MetaMask connection issues:**
- Ensure RPC URL is exactly `http://localhost:8545`
- Verify Chain ID is `1337`
- Try refreshing MetaMask or restarting browser

## 📋 System Requirements

- **OS**: macOS, Linux, or Windows with Docker Desktop
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Port 8545 and 8546 available

## 🎯 Production Notes

This configuration is optimized for **development and testing**. For production deployment:

- Implement proper key management
- Configure networking security
- Set up monitoring and logging
- Consider multi-node setup for redundancy
- Implement backup strategies

## � Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker compose logs`
3. Verify network configuration in MetaMask
4. Ensure all prerequisites are met

---

**🎉 Congratulations! Your UCASH blockchain is ready for home deployment!**

*Built with Hyperledger Besu • Ethereum Compatible • Ultra-Low Fees*
