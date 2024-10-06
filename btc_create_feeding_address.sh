#! /usr/bin/env bash

set -x

DUMMY_ADDRESS=mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn

pushd /home/maciej/bin/Bitcoin/bitcoin-27.0

if [ ! -d /home/maciej/bin/Bitcoin/bitcoin-27.0/data/regtest/wallets/feeding_wallet ]
then
    ./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf createwallet "feeding_wallet"
# else
#     ./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf loadwallet "feeding_wallet"
fi

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getwalletinfo

FEEDING_ADDRESS=$(./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getnewaddress feeding_address)

echo FEEDING_ADDRESS: $FEEDING_ADDRESS


./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 5 $FEEDING_ADDRESS

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 101 $DUMMY_ADDRESS >/dev/null

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf sendtoaddress "$1" 6.0

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 101 $DUMMY_ADDRESS >/dev/null

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf scantxoutset start "[{\"desc\": \"addr($1)\"}]"


popd