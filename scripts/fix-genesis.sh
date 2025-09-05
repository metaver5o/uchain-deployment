#!/bin/bash

GENESIS_FILE="/root/.evmos/config/genesis.json"

echo "Comprehensively fixing genesis file for ucash denomination..."

# Use jq to update ALL necessary fields
jq '
.app_state.staking.params.bond_denom = "ucash" |
.app_state.mint.params.mint_denom = "ucash" |
.app_state.crisis.constant_fee.denom = "ucash" |
.app_state.gov.deposit_params.min_deposit[0].denom = "ucash" |
.app_state.evm.params.evm_denom = "ucash" |
.app_state.bank.supply[0].denom = "ucash" |
(.app_state.bank.denom_metadata[0].base = "ucash") |
(.app_state.bank.denom_metadata[0].denom_units[0].denom = "ucash") |
(.app_state.bank.denom_metadata[0].denom_units[1].denom = "UCASH")
' $GENESIS_FILE > /tmp/genesis.tmp && mv /tmp/genesis.tmp $GENESIS_FILE

echo "Genesis file comprehensively updated!"