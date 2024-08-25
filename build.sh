#!/usr/bin/env bash

MODE=${1:-local}

PATTERN1="========================================"
PATTERN2="----------------------------------------"
if [ "$MODE" = "local" ]; then
  echo -e "${PATTERN1}\nBuilding in local mode\n${PATTERN1}"
else
  echo -e "${PATTERN2}\nBuilding in non-local mode\n${PATTERN2}"
fi


# Run dfx stop in the background
dfx stop &
# Get the PID of the last background command
DFX_PID=$!
# Use a subshell to wait for dfx stop to finish for up to the timeout value
if ! timeout 30s bash -c -- "(while kill -0 $DFX_PID; do sleep 1; done)"; then
    echo "dfx stop did not finish in time, killing it..."
    dfx killall
fi

set -eu

echo "===========SETUP========="
dfx start --background --clean
sleep 5
dfx identity list

PUSH_RED="\e[31m"
PUSH_GREEN="\e[32m"
PUSH_YELLOW="\e[33m"
POP="\e[0m"


if [ "$MODE" == "local" ]; then
    export LEDGER_CANISTER_ID=mxzaz-hqaaa-aaaar-qaada-cai
    export LEDGER=icrc1_ledger_canister
    export NETWORK=
    export PLAYGROUND=
else
    export LEDGER_CANISTER_ID=ryjl3-tyaaa-aaaaa-aaaba-cai
    export LEDGER=$LEDGER_CANISTER_ID
    export NETWORK=--ic
    export PLAYGROUND=--playground
fi


if [ "$MODE" == "local" ]; then
  dfx deploy $LEDGER --argument "(variant {
    Init = record {
      token_symbol = \"ICRC1\";
      token_name = \"L-ICRC1\";
      minting_account = record {
        owner = principal \"$(dfx identity --identity anonymous get-principal)\"
      };
      transfer_fee = 10_000;
      metadata = vec {};
      initial_balances = vec {
        record {
          record {
            owner = principal \"$(dfx identity --identity Alice get-principal)\";
          };
          10_000_000_000;
        };
      };
      archive_options = record {
        num_blocks_to_archive = 1000;
        trigger_threshold = 2000;
        controller_id = principal \"$(dfx identity --identity anonymous get-principal)\";
      };
      feature_flags = opt record {
        icrc2 = true;
      };
    }
  })"

  dfx deploy $PLAYGROUND bootcamp_chat_frontend  

fi


# npm install
dfx deploy $PLAYGROUND bootcamp_chat_backend
export BACKEND_CANISTER_ID=$(dfx canister $PLAYGROUND id bootcamp_chat_backend)

echo -e "${PUSH_YELLOW}BACKEND_CANISTER_ID: $BACKEND_CANISTER_ID$POP"


dfx deploy $PLAYGROUND bootcamp_chat_frontend





# google-chrome 'https://v3x57-gaaaa-aaaab-qadmq-cai.icp0.io/'
