#!/bin/bash
# Quick Blockchain Test Commands

echo "=== Quick Blockchain Health Check ==="

# 1. Check if nodes are running
echo "1. Docker containers status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep besu

# 2. Check current block number
echo -e "\n2. Current block number:"
curl -s -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  http://localhost:8545 | jq '.result' | xargs -I {} printf "Block: %d\n" {}

# 3. Check chain ID
echo -e "\n3. Chain ID:"
curl -s -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  http://localhost:8545 | jq '.result' | xargs -I {} printf "Chain ID: %d\n" {}

# 4. Check account balance (replace with your address)
echo -e "\n4. Account balance:"
curl -s -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266","latest"],"id":1}' \
  http://localhost:8545 | jq -r '.result' | xargs -I {} printf "Balance: %.4f UCASH\n" $(echo "scale=4; {} / 10^18" | bc -l)

# 5. Check recent blocks for transactions
echo -e "\n5. Recent block transaction count:"
for i in {0..2}; do
  block_hex=$(printf "0x%x" $(($(curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' http://localhost:8545 | jq -r '.result' | xargs -I {} printf "%d" {}) - i)))
  tx_count=$(curl -s -X POST -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockTransactionCountByNumber\",\"params\":[\"$block_hex\"],\"id\":1}" http://localhost:8545 | jq -r '.result' | xargs -I {} printf "%d" {})
  echo "  Block $block_hex: $tx_count transactions"
done

# 6. Watch recent logs for transaction activity
echo -e "\n6. Recent node logs (showing transaction activity):"
docker logs besu-server-node --tail=5 | grep -E "(tx|gas)" || echo "No recent transaction logs"

echo -e "\n=== Health Check Complete ==="
