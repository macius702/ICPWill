#! /usr/bin/env bash

DUMMY_ADDRESS=mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn

pushd /home/maciej/bin/Bitcoin/bitcoin-27.0

./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 101 $DUMMY_ADDRESS >/dev/null

popd

