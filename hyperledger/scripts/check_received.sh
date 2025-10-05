#!/bin/bash
# Quick check for received transactions

RECEIVER_ADDRESS="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

echo "=== Checking Received Transactions ==="
echo "Address: $RECEIVER_ADDRESS"
echo

# Get current balance
echo "Current Balance:"
curl -s -X POST -H "Content-Type: application/json" \
  --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBalance\",\"params\":[\"$RECEIVER_ADDRESS\",\"latest\"],\"id\":1}" \
  http://localhost:8545 | jq -r '.result' | xargs -I {} printf "  %.4f UCASH\n" $(echo "scale=4; {} / 10^18" | bc -l)

echo
echo "Recent blocks with transactions:"

# Check last 20 blocks for transactions
CURRENT_BLOCK=$(curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' http://localhost:8545 | jq -r '.result')
CURRENT_BLOCK_DEC=$(printf "%d" $CURRENT_BLOCK)

for i in {0..19}; do
  BLOCK_NUM=$((CURRENT_BLOCK_DEC - i))
  BLOCK_HEX=$(printf "0x%x" $BLOCK_NUM)
  
  # Get block with transactions
  BLOCK_DATA=$(curl -s -X POST -H "Content-Type: application/json" \
    --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[\"$BLOCK_HEX\",true],\"id\":1}" \
    http://localhost:8545)
  
  # Check if block has transactions involving our address
  echo "$BLOCK_DATA" | jq -r --arg addr "$RECEIVER_ADDRESS" '
    .result | 
    if .transactions | length > 0 then
      .transactions[] | 
      select(.to == $addr or .from == $addr) |
      "  Block \(.blockNumber): \(if .from == $addr then "SENT" else "RECEIVED" end) \(.value | tonumber / 1000000000000000000) UCASH"
    else
      empty
    end
  '
done

echo
echo "=== Summary ==="
echo "If you see transactions above, they ARE happening on the blockchain."
echo "MetaMask only shows transactions SENT from your wallet, not RECEIVED."
echo "Use this script or a block explorer to see received transactions."
