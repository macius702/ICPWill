#!/usr/bin/env bash

# we are in Rust basic_bitcoin example 

#### In bitcoind-cli directory ####

### setup regtest bitcoin network in separate directory ###
tar -xzf bitcoin-27.0-x86_64-linux-gnu.tar.gz 
cd bitcoin-27.0/
mkdir data
code .


cat <<EOF >  bitcoin.conf
# Enable regtest mode. This is required to setup a private bitcoin network.
regtest=1

# Dummy credentials that are required by `bitcoin-cli`.
rpcuser=ic-btc-integration
rpcpassword=QPQiNaph19FqUsCrBRN0FII7lyM26B51fAMeBQzCb-E=
rpcauth=ic-btc-integration:cdf2741387f3a12438f69092f0fdad8e$62081498c98bee09a0dce2b30671123fa561932992ce377585e8e08bb0c11dfa

fallbackfee=0.0000002
txindex=1
EOF 

# start daemon
./bin/bitcoind -conf=$(pwd)/bitcoin.conf -datadir=$(pwd)/data --port=18444


### operations in this directory with bitcoin-cli ###

# generate blocks, the BTC reward goes to the address
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress <number-of-blocks> 1 mjdChsJNSDxowKJCtZrchiMNw4bPDNrZwG
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf generatetoaddress 100 mtbZzVBwLnDmhH4pE9QynWAgh6H3aC1E6M

# a wallet needed
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf createwallet "mywallet"
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf loadwallet "mywallet"
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getwalletinfo

# addresses to send BTC to
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf help getnewaddress 
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getnewaddress etykietkaadresu
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getnewaddress etykietkaadresu2 legacy
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getnewaddress p2sh-segwit_address 
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getaddressesbylabel etykietkaadresu2
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf getaddressinfo bcrt1qqe88w3tplky7cpn8zxzhumhcl9tetrhmacf89s

# stop daemon 
./bin/bitcoin-cli -conf=$(pwd)/bitcoin.conf stop


#### In dfx replica directory ####
### start local replica
dfx start --clean --enable-bitcoin --log file --logfile dfx.log 


#### In dfx project directory ####
# build
dfx deploy basic_bitcoin --argument '(variant { regtest })'

# get bitcin address of this canister
dfx canister call basic_bitcoin get_p2pkh_address

dfx canister call basic_bitcoin get_balance '("n1F3JhKAtiCa64S4nypDeanH5LiFmnuxkp")'

# we can generate blocks in bitcon-cli above with generatetoaddress to canister address to have some bitcoins (from rewards)
# we can send bitcoins to other addresses with send_from_p2pkh
dfx canister call basic_bitcoin send_from_p2pkh '(record { destination_address = "n4LgJjsn5VinHvsxXxiZBK5TrPsWrYRpPo"; amount_in_satoshi = 100000000; })'















