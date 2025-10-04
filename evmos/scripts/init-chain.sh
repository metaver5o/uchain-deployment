#!/bin/bash
set -euo pipefail

CHAIN_ID="${CHAIN_ID:-evmos_9000-1}"
MONIKER="${MONIKER:-uchain-validator}"
KEY_NAME="${KEY_NAME:-validator}"
KEYRING_BACKEND="${KEYRING_BACKEND:-test}"
HOME_DIR="/root/.evmos"

# Clean up existing data
if [ -d "$HOME_DIR" ]; then
    echo "Cleaning up existing data..."
    rm -rf "$HOME_DIR"/* 2>/dev/null || true
    rm -rf "$HOME_DIR"/.* 2>/dev/null || true
fi

# Initialize with default genesis
echo "Initializing chain $CHAIN_ID..."
evmosd init "$MONIKER" --chain-id "$CHAIN_ID" --home "$HOME_DIR" --overwrite

# Create validator key
echo "Creating validator key..."
echo "$KEY_NAME" | evmosd keys add "$KEY_NAME" --keyring-backend "$KEYRING_BACKEND" --home "$HOME_DIR" >/dev/null 2>&1

VALIDATOR_ADDRESS=$(evmosd keys show "$KEY_NAME" -a --keyring-backend "$KEYRING_BACKEND" --home "$HOME_DIR")
echo "Validator address: $VALIDATOR_ADDRESS"

# Add genesis account
evmosd add-genesis-account "$VALIDATOR_ADDRESS" 1000000000000000000000000ucash \
  --keyring-backend "$KEYRING_BACKEND" --home "$HOME_DIR"

# Fix the staking and mint parameters to use ucash instead of stake/aevmos
echo "Fixing staking and mint parameters in genesis..."
jq '
.app_state.staking.params.bond_denom = "ucash" |
.app_state.mint.params.mint_denom = "ucash" |
.app_state.mint.minter.annual_provisions = "0" |
.app_state.mint.minter.inflation = "0" |
.app_state.gov.params.min_deposit[0].denom = "ucash" |
.app_state.crisis.constant_fee.denom = "ucash" |
.app_state.evm.params.evm_denom = "ucash" |
.consensus = {"validators":[],"params":{"block":{"max_bytes":"22020096","max_gas":"-1","time_iota_ms":"1000"},"evidence":{"max_age_num_blocks":"100000","max_age_duration":"172800000000000","max_bytes":"1048576"},"validator":{"pub_key_types":["ed25519"]},"version":{}}}
' "$HOME_DIR/config/genesis.json" > "$HOME_DIR/config/genesis_temp.json" && \
mv "$HOME_DIR/config/genesis_temp.json" "$HOME_DIR/config/genesis.json"

# Create gentx (now using ucash which matches the bond_denom)
evmosd gentx "$KEY_NAME" 1000000000000000000000ucash \
  --chain-id "$CHAIN_ID" \
  --keyring-backend "$KEYRING_BACKEND" \
  --moniker "$MONIKER" \
  --home "$HOME_DIR" \
  --commission-rate "0.1" \
  --commission-max-rate "0.2" \
  --commission-max-change-rate "0.01" \
  --min-self-delegation "1"

evmosd collect-gentxs --home "$HOME_DIR"

echo "Validating genesis..."
evmosd validate-genesis --home "$HOME_DIR"

echo "UChain initialization completed successfully!"