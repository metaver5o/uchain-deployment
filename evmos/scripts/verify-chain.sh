#!/bin/bash

# Set proper permissions
mkdir -p /root/.evmos/config
chmod -R 755 /root/.evmos

# Initialize the chain only if not already initialized
if [ ! -f "/root/.evmos/config/genesis.json" ]; then
    echo "Initializing UChain with chain ID: $CHAIN_ID"
    
    # Initialize with default Evmos local chain ID
    evmosd init $MONIKER --chain-id $CHAIN_ID --home /root/.evmos
    
    # Create client.toml
    cat > /root/.evmos/config/client.toml << EOF
chain-id = "$CHAIN_ID"
keyring-backend = "test"
output = "text"
node = "tcp://localhost:26657"
broadcast-mode = "sync"
EOF

    # Configure minimum gas price
    sed -i 's|minimum-gas-prices = ""|minimum-gas-prices = "0.0001aevmos"|' /root/.evmos/config/app.toml
    
    # Enable all APIs
    sed -i 's|enable = false|enable = true|g' /root/.evmos/config/app.toml
    sed -i 's|swagger = false|swagger = true|g' /root/.evmos/config/app.toml
    
    # Configure JSON-RPC
    sed -i 's|address = "127.0.0.1:8545"|address = "0.0.0.0:8545"|' /root/.evmos/config/app.toml
    sed -i 's|ws-address = "127.0.0.1:8546"|ws-address = "0.0.0.0:8546"|' /root/.evmos/config/app.toml
    sed -i 's|api = \["eth", "net", "web3"\]|api = \["eth", "net", "web3", "personal", "txpool"\]|' /root/.evmos/config/app.toml
    
    # Enable CORS
    sed -i 's|cors_allowed_origins = \[\]|cors_allowed_origins = \["*"\]|g' /root/.evmos/config/config.toml
    
    # Create validator key
    echo "Creating validator key..."
    (echo "validator"; echo "validator") | evmosd keys add validator --keyring-backend test --home /root/.evmos
    
    # Add genesis account
    echo "Adding genesis account..."
    evmosd add-genesis-account validator 1000000000000000000000000aevmos \
        --keyring-backend test \
        --home /root/.evmos
    
    # Create gentx
    echo "Creating gentx..."
    evmosd gentx validator 1000000000000000000000aevmos \
        --chain-id $CHAIN_ID \
        --keyring-backend test \
        --moniker $MONIKER \
        --home /root/.evmos
    
    # Collect gentxs
    echo "Collecting gentxs..."
    evmosd collect-gentxs --home /root/.evmos
    
    # Now modify the genesis to use our custom token AFTER gentx creation
    echo "Modifying genesis to use UCASH token..."
    sed -i 's/"aevmos"/"ucash"/g' /root/.evmos/config/genesis.json
    sed -i 's/"Evmos"/"UCash"/g' /root/.evmos/config/genesis.json
    sed -i 's/"EVMOS"/"UCASH"/g' /root/.evmos/config/genesis.json
    
    # Also update the minimum gas prices
    sed -i 's|minimum-gas-prices = "0.0001aevmos"|minimum-gas-prices = "0.0001ucash"|' /root/.evmos/config/app.toml
    
    # Set proper permissions
    chmod -R 755 /root/.evmos/config
    
    echo "UChain initialization completed!"
    
else
    echo "Chain already initialized, checking configuration..."
    
    # Ensure client.toml exists
    if [ ! -f "/root/.evmos/config/client.toml" ]; then
        cat > /root/.evmos/config/client.toml << EOF
chain-id = "$CHAIN_ID"
keyring-backend = "test"
output = "text"
node = "tcp://localhost:26657"
broadcast-mode = "sync"
EOF
    fi
    
    # Update chain ID in client.toml if it's wrong
    sed -i "s|chain-id = .*|chain-id = \"$CHAIN_ID\"|" /root/.evmos/config/client.toml
    
    # Set proper permissions
    chmod -R 755 /root/.evmos/config
    
    echo "Configuration updated for chain ID: $CHAIN_ID"
fi