#!/bin/bash

# u.chain Quick Start Script
# Generates wallets on-the-fly and launches the blockchain

echo "🌟 u.chain Quick Start"
echo "======================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if we have existing wallets
if [ -f "WALLETS.txt" ]; then
    echo "📋 Found existing wallet configuration:"
    echo
    head -10 WALLETS.txt
    echo
    read -p "🤔 Use existing wallets? (y/n): " use_existing
    
    if [ "$use_existing" = "n" ] || [ "$use_existing" = "N" ]; then
        echo "🔄 Generating fresh wallets..."
        rm -f genesis.json WALLETS.txt config/wallets_config.json
    else
        echo "✅ Using existing wallet configuration"
    fi
fi

# Setup Python environment if needed
if [ ! -d "wallet_env" ]; then
    echo "📦 Setting up Python environment..."
    python3 -m venv wallet_env
    source wallet_env/bin/activate
    pip install -r requirements.txt >/dev/null 2>&1
else
    source wallet_env/bin/activate
fi

# Launch with wallet generation
echo "🚀 Launching u.chain with dynamic wallets..."
python dynamic_launcher.py

# Check if launch was successful
if [ $? -eq 0 ]; then
    echo
    echo "🎉 u.chain is running!"
    echo "📊 View logs: docker compose logs -f"
    echo "🛑 Stop: docker compose down"
    echo "🏦 Wallet info: cat WALLETS.txt"
    echo
    echo "🔗 Connect to: http://localhost:8545"
    echo "⛓️  Chain ID: 1337"
else
    echo "❌ Failed to launch u.chain"
    exit 1
fi
