#!/bin/bash

# command line arguments are --ic optional and optional BALANCEOF
# if --ic is not provided, then LEDGER is ryjl3-tyaaa-aaaaa-aaaba-cai else mxzaz-hqaaa-aaaar-qaada-cai
# if BALANCEOF is not provided, then BALANCEOF is bd3sg-teaaa-aaaaa-qaaba-cai

function getbalance() {
    LEDGER=mxzaz-hqaaa-aaaar-qaada-cai
    NETWORK=
    BALANCEOF=bd3sg-teaaa-aaaaa-qaaba-cai

    # check command line
    while [ $# -gt 0 ]; do
        if [ "$1" == "--ic" ]; then
            LEDGER=ryjl3-tyaaa-aaaaa-aaaba-cai
            NETWORK=--ic
        else
            BALANCEOF=$1
        fi
        shift
    done

    echo "LEDGER: $LEDGER"
    echo "BALANCEOF: $BALANCEOF"

    echo "\
(record {
    owner = principal \"$BALANCEOF\";
    subaccount = null
})" >/tmp/argument.txt
    output=$(dfx canister $NETWORK call $LEDGER icrc1_balance_of --argument-file /tmp/argument.txt)
    echo $output
}
getbalance
