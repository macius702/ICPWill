#!/bin/bash

# Default values
LEDGER=mxzaz-hqaaa-aaaar-qaada-cai
BALANCEOF=bd3sg-teaaa-aaaaa-qaaba-cai

# Help message
help_message() {
        cat << EOF
Usage: $0 [BALANCEOF] [--ledger LEDGER]

Optional arguments:
    BALANCEOF   The balanceof value (default: bd3sg-teaaa-aaaaa-qaaba-cai)
    --ledger    The ledger value (default: mxzaz-hqaaa-aaaar-qaada-cai)
    --help      Show this help message and exit

The script ledger_getbalance.sh is a command-line utility that interacts with a ledger canister's balanceof method.
The balanceof method is a function provided by the ledger canister that allows you to query the balance of a specific account.

The script accepts two optional arguments:
    BALANCEOF: This argument represents the principal of the account whose balance you want to query.
    It can be either an identity principal or a canister principal.
    If this argument is not provided, the script uses a default value of bd3sg-teaaa-aaaaa-qaaba-cai.

    --ledger: This argument represents the ledger canister that the script will interact with.
    If this argument is not provided, the script uses a default value of mxzaz-hqaaa-aaaar-qaada-cai.

When run, the script constructs a record with the BALANCEOF principal and a null subaccount,
and writes this record to a temporary file.
This file can then be used as input to the balanceof method of the ledger canister.
EOF
}
# Parse command line options
while (( "$#" )); do
    case "$1" in
        --ledger)
            if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
                LEDGER=$2
                shift 2
            else
                echo "Error: Argument for $1 is missing" >&2
                exit 1
            fi
            ;;
        --help)
            help_message
            exit 0
            ;;
        -*|--*=) # unsupported flags
            echo "Error: Unsupported flag $1" >&2
            exit 1
            ;;
        *) # preserve positional arguments
            BALANCEOF=${1:-bd3sg-teaaa-aaaaa-qaaba-cai}
            shift
            ;;
    esac
done

echo "LEDGER: $LEDGER"
echo "BALANCEOF: $BALANCEOF"


echo "\
(record {
    owner = principal \"$BALANCEOF\";
    subaccount = null
})" > /tmp/argument.txt
dfx canister call $LEDGER icrc1_balance_of --argument-file /tmp/argument.txt