#!/bin/bash

# Function to launch the u.chain local devnet (PoS setup)
launch_local_devnet() {
    echo "🚀 Starting u.chain local PoS devnet with dynamic wallet generation..."
    
    # Check if Python virtual environment exists
    if [ ! -d "wallet_env" ]; then
        echo "📦 Setting up Python environment..."
        python3 -m venv wallet_env
        source wallet_env/bin/activate
        pip install -r requirements.txt
    else
        source wallet_env/bin/activate
    fi
    
    # Launch with dynamic wallet generation
    python dynamic_launcher.py
}

# Function to launch a Public Ethereum Testnet node
launch_public_testnet() {
    read -p "Enter desired testnet (e.g., holesky, sepolia): " NET
    echo "Starting Besu execution client on $NET..."
    # Note: For public PoS testnets, you MUST run a consensus client (Teku) separately!
    docker run -d --name besu-$NET -p 8545:8545 hyperledger/besu:latest \
        --network=$NET \
        --sync-mode=SNAP \
        --rpc-http-enabled
}

# Function to launch with random wallets
launch_random_devnet() {
    echo "🎲 Starting u.chain with random wallet generation..."
    
    if [ ! -d "wallet_env" ]; then
        echo "📦 Setting up Python environment..."
        python3 -m venv wallet_env
        source wallet_env/bin/activate
        pip install -r requirements.txt
    else
        source wallet_env/bin/activate
    fi
    
    python dynamic_launcher.py --random
}

# Function to generate wallets only
generate_wallets_only() {
    echo "🏦 Generating wallets without launching blockchain..."
    
    if [ ! -d "wallet_env" ]; then
        echo "📦 Setting up Python environment..."
        python3 -m venv wallet_env
        source wallet_env/bin/activate
        pip install -r requirements.txt
    else
        source wallet_env/bin/activate
    fi
    
    python dynamic_launcher.py --wallets-only
}

# Function to show wallet information
show_wallet_info() {
    echo "📊 Current Wallet Information"
    echo "============================"
    
    if [ -f "WALLETS.txt" ]; then
        cat WALLETS.txt
    elif [ -f "config/wallets_config.json" ]; then
        echo "📋 Wallet config found. Run wallet manager for details:"
        echo "source wallet_env/bin/activate && python wallet_manager.py"
    else
        echo "❌ No wallet information found. Generate wallets first."
    fi
}

# Function to launch the u.chain TESTNET (multi-machine deployment)
launch_u_chain_testnet() {
    echo "--- u.chain Testnet Deployment ---"
    echo "Launching nodes on dedicated infrastructure via Ansible/K8s..."
    # Placeholder for running a production deployment script
    # ansible-playbook deploy_testnet.yml
    echo "Check the cloud console for node status."
}

# Main menu loop
while true; do
    echo ""
    echo "=================================="
    echo "         u.chain Launch Menu        "
    echo "=================================="
    echo "1) 🚀 Local PoS Devnet (Dynamic Wallets)"
    echo "2) 🎲 Local PoS Devnet (Random Wallets)"
    echo "3) 🏦 Generate Wallets Only"
    echo "4) 🌐 Public Ethereum Testnet (Sepolia/Holesky)"
    echo "5) 🧪 u.chain Testnet (External Deployment)"
    echo "6) 📊 Show Wallet Info"
    echo "7) 🛑 Stop Local Devnet"
    echo "8) 🚪 Exit"
    read -p "Choose an option: " choice

    case $choice in
        1) launch_local_devnet ;;
        2) launch_random_devnet ;;
        3) generate_wallets_only ;;
        4) launch_public_testnet ;;
        5) launch_u_chain_testnet ;;
        6) show_wallet_info ;;
        7) docker compose down ;;
        8) break ;;
        *) echo "Invalid option. Please try again." ;;
    esac
done
