#!/bin/bash
# Transaction Monitor - Focus on incoming transactions only
# Watches both nodes for new transactions in real-time

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Node endpoints
SERVER_RPC="http://localhost:8545"
HOME_RPC="http://localhost:8547"

echo -e "${BLUE}� Transaction Monitor${NC}"
echo "============================="
echo -e "🖥️  Server Node: ${GREEN}$SERVER_RPC${NC}"
echo -e "🏠 Home Node:   ${YELLOW}$HOME_RPC${NC}"
echo ""
echo "Watching for incoming transactions..."
echo ""

# Function to check for transactions in latest block
check_transactions() {
    local rpc_url=$1
    local node_name=$2
    local color=$3
    
    # Get latest block with transactions
    local response=$(curl -s -X POST -H "Content-Type: application/json" \
        --data '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}' \
        $rpc_url)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ $node_name: Connection failed${NC}"
        return 1
    fi
    
    # Parse response
    local block_num=$(echo "$response" | jq -r '.result.number' 2>/dev/null)
    local tx_count=$(echo "$response" | jq -r '.result.transactions | length' 2>/dev/null)
    local timestamp=$(echo "$response" | jq -r '.result.timestamp' 2>/dev/null)
    
    if [ "$block_num" = "null" ] || [ -z "$block_num" ]; then
        echo -e "${RED}❌ $node_name: No response${NC}"
        return 1
    fi
    
    # Convert hex to decimal
    local block_dec=$(printf "%d" "$block_num" 2>/dev/null)
    local timestamp_dec=$(printf "%d" "$timestamp" 2>/dev/null)
    local time_str=$(date -r "$timestamp_dec" "+%H:%M:%S" 2>/dev/null || echo "N/A")
    
    # Show node status
    printf "${color}%-10s${NC} Block: %6d | Time: %s" "$node_name" "$block_dec" "$time_str"
    
    # Show transactions if any
    if [ "$tx_count" -gt 0 ]; then
        printf " | ${GREEN}📥 %d TXs${NC}\n" "$tx_count"
        
        # Show transaction details
        echo "$response" | jq -r '.result.transactions[] | 
            "    � \(.hash[0:12])... | \(.from[0:10])...→\(.to[0:10])... | \((.value | tonumber) / 1000000000000000000) UCASH"' 2>/dev/null
    else
        printf " | No transactions\n"
    fi
    
    return 0
}

# Function to send test transaction
send_test_tx() {
    echo ""
    echo -e "${BLUE}🧪 Sending test transaction...${NC}"
    
    # Create simple Python transaction sender
    cat > /tmp/send_tx.py << 'EOF'
from web3 import Web3
import sys

try:
    # Setup Web3 with PoA middleware
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    
    # Add PoA middleware
    try:
        from web3.middleware import ExtraDataToPOAMiddleware
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    except:
        pass
    
    # Test connection
    if not w3.is_connected():
        print("❌ Cannot connect to server node")
        sys.exit(1)
    
    # Account setup
    private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    account = w3.eth.account.from_key(private_key)
    to_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
    
    # Get current nonce
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Create transaction
    transaction = {
        'to': to_address,
        'value': w3.to_wei(0.005, 'ether'),  # 0.005 UCASH
        'gas': 21000,
        'gasPrice': w3.to_wei(2000, 'gwei'),
        'nonce': nonce,
        'chainId': 1337
    }
    
    # Sign and send
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"✅ Transaction sent: {tx_hash.hex()}")
    print(f"   From: {account.address}")
    print(f"   To: {to_address}")
    print(f"   Amount: 0.005 UCASH")
    print(f"   Nonce: {nonce}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

    python3 /tmp/send_tx.py
    rm -f /tmp/send_tx.py
    echo ""
}

# Store last seen block numbers to detect new transactions
last_server_block=0
last_home_block=0

echo "Starting transaction monitoring... (Press 'q' to quit, 't' to send test transaction)"
echo ""

# Main monitoring loop
while true; do
    # Get current timestamp
    echo -e "${BLUE}$(date '+%H:%M:%S')${NC} - Checking for transactions:"
    
    # Check both nodes
    check_transactions "$SERVER_RPC" "SERVER" "$GREEN"
    check_transactions "$HOME_RPC" "HOME" "$YELLOW"
    
    echo ""
    
    # Check for user input (non-blocking)
    if read -t 3 -n 1 input 2>/dev/null; then
        case $input in
            t|T)
                send_test_tx
                ;;
            q|Q)
                echo -e "\n${BLUE}👋 Transaction monitoring stopped${NC}"
                exit 0
                ;;
        esac
    fi
    
    # Clear screen for next iteration (optional)
    # tput clear
    
done
