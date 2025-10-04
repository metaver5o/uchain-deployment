#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running UChain Network Tests${NC}\n"

# Test 1: Check if both nodes are running and synced
echo -e "${YELLOW}Test 1: Checking Node Status${NC}"
echo "Primary Node Status:"
if output=$(docker-compose exec -T uchain-node curl -s http://localhost:26657/status 2>/dev/null); then
    echo "$output" | jq '.result | {
        catching_up: .sync_info.catching_up,
        latest_block_height: .sync_info.latest_block_height
    }' 2>/dev/null || echo "Node may not be running"
else
    echo "Failed to get primary node status"
fi

echo -e "\nSecondary Node Status:"
if output=$(docker-compose -f docker-compose.secondary.yml exec -T uchain-secondary curl -s http://localhost:26657/status 2>/dev/null); then
    echo "$output" | jq '.result | {
        catching_up: .sync_info.catching_up,
        latest_block_height: .sync_info.latest_block_height
    }' 2>/dev/null || echo "Node may not be running"
else
    echo "Failed to get secondary node status"
fi

# Test 2: List all validators
echo -e "\n${YELLOW}Test 2: Listing Validators${NC}"
docker-compose exec -T uchain-node evmosd query staking validators --output json 2>/dev/null | jq '.validators[] | {moniker, status, tokens}'

# Test 3: Check validator voting power
echo -e "\n${YELLOW}Test 3: Checking Validator Voting Power${NC}"
docker-compose exec -T uchain-node evmosd query tendermint-validator-set --output json 2>/dev/null | jq '.validators[].voting_power'

# Test 4: List delegations for the primary validator
echo -e "\n${YELLOW}Test 4: Checking Delegations${NC}"
# Get validator address in bech32 format
if PRIMARY_VALIDATOR=$(docker-compose exec -T uchain-node evmosd query staking validators --output json 2>/dev/null | jq -r '.validators[0].operator_address'); then
    if [ ! -z "$PRIMARY_VALIDATOR" ] && [ "$PRIMARY_VALIDATOR" != "null" ]; then
        if output=$(docker-compose exec -T uchain-node evmosd query staking delegations-to $PRIMARY_VALIDATOR --output json 2>/dev/null); then
            echo "$output" | jq . || echo "No delegations found"
        else
            echo "Failed to query delegations"
        fi
    else
        echo "Failed to get validator address"
    fi
else
    echo "Failed to get validator address"
fi

# Test 5: Check node connections
echo -e "\n${YELLOW}Test 5: Checking Node Connections${NC}"
echo "Primary Node Peers:"
docker-compose exec -T uchain-node evmosd query tendermint-validator-set --output json 2>/dev/null | jq '.validators[] | {address, voting_power}'

# Test 6: Check balance of validator accounts
echo -e "\n${YELLOW}Test 6: Checking Validator Balances${NC}"
echo "Primary Validator Balance:"
# Get validator's delegator (account) address from delegations
if PRIMARY_VALIDATOR=$(docker-compose exec -T uchain-node evmosd query staking validators --output json 2>/dev/null | jq -r '.validators[0].operator_address'); then
    if [ "$PRIMARY_VALIDATOR" != "null" ] && [ ! -z "$PRIMARY_VALIDATOR" ]; then
        if PRIMARY_ADDR=$(docker-compose exec -T uchain-node evmosd query staking delegations-to $PRIMARY_VALIDATOR --output json 2>/dev/null | jq -r '.delegation_responses[0].delegation.delegator_address'); then
            if [ "$PRIMARY_ADDR" != "null" ] && [ ! -z "$PRIMARY_ADDR" ]; then
                if output=$(docker-compose exec -T uchain-node evmosd query bank balances $PRIMARY_ADDR --output json 2>/dev/null); then
                    echo "$output" | jq . || echo "No balance found"
                else
                    echo "Failed to query balance"
                fi
            else
                echo "Failed to get delegator address"
            fi
        else
            echo "Failed to get delegations"
        fi
    else
        echo "Failed to get validator address"
    fi
else
    echo "Failed to get validator info"
fi

echo -e "\nSecondary Validator Balance:"
if SECONDARY_VALIDATOR=$(docker-compose -f docker-compose.secondary.yml exec -T uchain-secondary evmosd query staking validators --output json 2>/dev/null | jq -r '.validators[0].operator_address'); then
    if [ "$SECONDARY_VALIDATOR" != "null" ] && [ ! -z "$SECONDARY_VALIDATOR" ]; then
        if SECONDARY_ADDR=$(docker-compose -f docker-compose.secondary.yml exec -T uchain-secondary evmosd query staking delegations-to $SECONDARY_VALIDATOR --output json 2>/dev/null | jq -r '.delegation_responses[0].delegation.delegator_address'); then
            if [ "$SECONDARY_ADDR" != "null" ] && [ ! -z "$SECONDARY_ADDR" ]; then
                if output=$(docker-compose -f docker-compose.secondary.yml exec -T uchain-secondary evmosd query bank balances $SECONDARY_ADDR --output json 2>/dev/null); then
                    echo "$output" | jq . || echo "No balance found"
                else
                    echo "Failed to query balance"
                fi
            else
                echo "Failed to get delegator address"
            fi
        else
            echo "Failed to get delegations"
        fi
    else
        echo "Failed to get validator address"
    fi
else
    echo "Failed to get validator info"
fi

# Test 7: Check network parameters
echo -e "\n${YELLOW}Test 7: Checking Network Parameters${NC}"
echo "Staking Parameters:"
docker-compose exec -T uchain-node evmosd query staking params --output json 2>/dev/null | jq

echo -e "\nGov Parameters:"
docker-compose exec -T uchain-node evmosd query gov params --output json 2>/dev/null | jq

# Test 8: Check active proposals if any
echo -e "\n${YELLOW}Test 8: Checking Active Proposals${NC}"
docker-compose exec -T uchain-node evmosd query gov proposals --output json 2>/dev/null | jq '.proposals // "No active proposals"'

# Test 9: Check chain info
echo -e "\n${YELLOW}Test 9: Chain Information${NC}"
if output=$(docker-compose exec -T uchain-node curl -s http://localhost:26657/status 2>/dev/null); then
    echo "$output" | jq '.result | {
        node_info: {
            id: .node_info.id,
            moniker: .node_info.moniker,
            network: .node_info.network
        },
        sync_info: {
            latest_block_height: .sync_info.latest_block_height,
            catching_up: .sync_info.catching_up,
            earliest_block_height: .sync_info.earliest_block_height
        },
        validator_info: {
            address: .validator_info.address,
            voting_power: .validator_info.voting_power
        }
    }' || echo "Failed to parse chain info"
else
    echo "Failed to get chain status"
fi
