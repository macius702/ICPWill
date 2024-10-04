#! /usr/bin/env bash

set -x

# ./bin/bitcoind -conf=$(pwd)/bitcoin.conf -datadir=$(pwd)/data --port=18444 -deprecatedrpc=create_bdb &


WALLET=mywalletold11

cd /home/maciej/bin/Bitcoin/bitcoin-27.0

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf createwallet "$WALLET" false false "" false false false
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 100 n3CLLv9XHZdDHsKPT3eS4dkecoi1KDWzyA
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 100 mtbZzVBwLnDmhH4pE9QynWAgh6H3aC1E6M
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET importaddress n3CLLv9XHZdDHsKPT3eS4dkecoi1KDWzyA "" false
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET rescanblockchain
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET getreceivedbyaddress n3CLLv9XHZdDHsKPT3eS4dkecoi1KDWzyA 4

# ./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET  getwalletinfo
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET listaddressgroupings

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf -rpcwallet=$WALLET listreceivedbyaddress 1 false true