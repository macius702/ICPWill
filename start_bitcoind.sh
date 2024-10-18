#! /usr/bin/env bash

export BITCOIND_INSTALL_DIR=/home/maciej/bin/Bitcoin/bitcoin-27.0

set -x

# Parse command-line options
STOP_BITCOIN=false

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --stop)
            STOP_BITCOIN=true
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Execute commented lines if --stop is provided
if [ "$STOP_BITCOIN" = true ]; then
    dfx stop
    $BITCOIND_INSTALL_DIR/bin/bitcoin-cli -conf=$BITCOIND_INSTALL_DIR/bitcoin.conf stop
    exit 0
fi
$BITCOIND_INSTALL_DIR/bin/bitcoin-cli -conf=$BITCOIND_INSTALL_DIR/bitcoin.conf stop

rm -rf $BITCOIND_INSTALL_DIR/data
mkdir $BITCOIND_INSTALL_DIR/data

$BITCOIND_INSTALL_DIR/bin/bitcoind -conf=$BITCOIND_INSTALL_DIR/bitcoin.conf -datadir=$BITCOIND_INSTALL_DIR/data --port=18444 2>$BITCOIND_INSTALL_DIR/bitoind.log  &
sleep 2
$BITCOIND_INSTALL_DIR/bin/bitcoin-cli -conf=$BITCOIND_INSTALL_DIR/bitcoin.conf getblockchaininfo

# dfx start --background --clean --enable-bitcoin 2>$BITCOIND_INSTALL_DIR/../unsaved/dfx.log 
