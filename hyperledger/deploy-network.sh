#!/bin/bash

# UCASH Network Deployment Script
# Configures nodes for distributed network connection

set -e

echo "🚀 UCASH Network Deployment Configuration"
echo "=========================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Function to show menu
show_menu() {
    echo ""
    echo "Select deployment type:"
    echo "1) 🏠 Home Node (Connect to UCASH network)"
    echo "2) 🖥️  Server Node (Act as bootnode/validator)" 
    echo "3) 🔧 Local Development (Isolated testing)"
    echo "4) ❓ Help - Understanding the network"
    echo "5) 🚪 Exit"
    echo ""
}

# Function to configure home node
setup_home_node() {
    echo "🏠 Setting up Home Node to connect to UCASH network..."
    
    # Copy network environment
    if [ -f ".env.network" ]; then
        cp .env.network .env
        echo "✅ Network configuration loaded"
    else
        echo "❌ Network configuration file missing. Creating default..."
        cat > .env << EOF
NETWORK_ID=1337
CHAIN_NAME=UCASH
UCASH_BOOTNODES=enode://YOUR_NODE_ID@YOUR_SERVER_IP:30303
VALIDATOR_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
BESU_P2P_PORT=30303
BESU_RPC_PORT=8545
BESU_WS_PORT=8546
ENABLE_HOME_MINING=false
EOF
    fi
    
    # Use home node configuration
    if [ -f "docker-compose.home.yml" ]; then
        echo "🔄 Starting UCASH home node..."
        docker compose -f docker-compose.home.yml up -d
        
        echo "✅ Home node started!"
        echo ""
        echo "📱 MetaMask Configuration:"
        echo "   Network Name: UCASH Network"
        echo "   RPC URL: http://localhost:8545"
        echo "   Chain ID: 1337"
        echo "   Currency: UCASH"
        echo ""
        echo "🔗 Your node is connecting to the UCASH network..."
        echo "📊 Check status: docker compose -f docker-compose.home.yml logs -f"
    else
        echo "❌ Home node configuration missing!"
    fi
}

# Function to configure server node  
setup_server_node() {
    echo "🖥️  Setting up Server Node (Bootnode/Validator)..."
    
    echo "⚠️  Server nodes require:"
    echo "   - Public IP address"
    echo "   - Open ports 30303 (P2P) and 8545 (RPC)"
    echo "   - Validator private key"
    echo ""
    
    read -p "Do you have a public IP and open ports? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "❌ Server setup cancelled. Configure networking first."
        return
    fi
    
    # Use server configuration
    if [ -f "docker-compose.server.yml" ]; then
        echo "🔄 Starting UCASH server node..."
        docker compose -f docker-compose.server.yml up -d
        
        echo "✅ Server node started!"
        echo ""
        echo "📡 Your node is now accepting connections from home users"
        echo "🔧 Get your node ID: docker compose -f docker-compose.server.yml exec besu_el besu --help | grep node-id"
        echo "📊 Check status: docker compose -f docker-compose.server.yml logs -f"
    else
        echo "❌ Server node configuration missing!"
    fi
}

# Function for local development
setup_local_dev() {
    echo "🔧 Setting up Local Development Environment..."
    
    # Use original local configuration
    echo "🔄 Starting local UCASH blockchain..."
    docker compose up -d
    
    echo "✅ Local development blockchain started!"
    echo ""
    echo "📱 MetaMask Configuration:"
    echo "   Network Name: uchain-local"
    echo "   RPC URL: http://localhost:8545"
    echo "   Chain ID: 1337"
    echo "   Currency: UCASH"
    echo ""
    echo "💡 This is isolated for testing only"
    echo "📊 Check status: docker compose logs -f"
}

# Function to show help
show_help() {
    echo "❓ Understanding UCASH Network Deployment"
    echo "========================================"
    echo ""
    echo "🏠 HOME NODE:"
    echo "   - Connects to existing UCASH network"
    echo "   - Downloads blockchain from server nodes"
    echo "   - Provides local RPC for MetaMask"
    echo "   - Can optionally participate in mining"
    echo ""
    echo "🖥️  SERVER NODE:"
    echo "   - Acts as bootnode for network discovery"
    echo "   - Validates transactions and creates blocks"
    echo "   - Provides public RPC endpoint"
    echo "   - Requires public IP and open ports"
    echo ""
    echo "🔧 LOCAL DEVELOPMENT:"
    echo "   - Isolated blockchain for testing"
    echo "   - No network connections"
    echo "   - Pre-funded test accounts"
    echo "   - Fast development iteration"
    echo ""
    echo "🌐 NETWORK TOPOLOGY:"
    echo "   Server Nodes ←→ Server Nodes"
    echo "        ↑              ↑"
    echo "   Home Nodes     Home Nodes"
    echo ""
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            setup_home_node
            break
            ;;
        2)
            setup_server_node
            break
            ;;
        3)
            setup_local_dev
            break
            ;;
        4)
            show_help
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-5."
            ;;
    esac
done
