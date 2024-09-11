#!/usr/bin/env bash

#source ~/.nvm/nvm.sh

# from my bash src
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
nvm use 20
npm i 


dfx identity new Alice || true


MODE=${1:-local}
CLEAN=${2}


PATTERN1="========================================"
PATTERN2="----------------------------------------"
if [ "$MODE" = "nonlocal" ]; then
  echo -e "${PATTERN2}\nBuilding in non-local mode\n${PATTERN2}"
else
  echo -e "${PATTERN1}\nBuilding in local mode\n${PATTERN1}"
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
if [ "$MODE" = "local" ]; then
  if [ "$CLEAN" == "--clean" ]; then
    dfx start --background --clean
  else
    dfx start --background
  fi
else
  dfx start --background
fi

sleep 5
dfx identity list

PUSH_RED="\e[31m"
PUSH_GREEN="\e[32m"
PUSH_YELLOW="\e[33m"
POP="\e[0m"


if [ "$MODE" == "local" ]; then
    export VITE_LEDGER_CANISTER_ID=mxzaz-hqaaa-aaaar-qaada-cai
    export LEDGER=icrc1_ledger_canister
    export VITE_IDENTITY_PROVIDER=http://br5f7-7uaaa-aaaaa-qaaca-cai.localhost:4943/
    export NETWORK=
    export PLAYGROUND=
    export VITE_AGENT_HOST=http://127.0.0.1:4943
else
    export VITE_LEDGER_CANISTER_ID=ryjl3-tyaaa-aaaaa-aaaba-cai
    export LEDGER=$LEDGER_CANISTER_ID
    export VITE_IDENTITY_PROVIDER=https://identity.ic0.app/#authorize
    export NETWORK=--ic
    export PLAYGROUND=--ic
    export VITE_AGENT_HOST=https://ic0.app
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
        record {
          record {
            owner = principal \"bd3sg-teaaa-aaaaa-qaaba-cai\";
          };
          12_000_000_000;  // Set the initial balance for this principal
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


fi

# generate typescript types for rust backend
dfx generate icp_will_backend

# npm install
dfx deploy $PLAYGROUND icp_will_backend

export BACKEND_CANISTER_ID=$(dfx canister $PLAYGROUND id icp_will_backend)

echo -e "${PUSH_YELLOW}BACKEND_CANISTER_ID: $BACKEND_CANISTER_ID$POP"


dfx deploy $PLAYGROUND icp_will_frontend
#fx deploy $PLAYGROUND icp_will_frontend

python3.10 ./test/e2e/first_selenium.py # python3 collision with python3.8 that is needed to launch gnome-terminal

echo DONE.



# google-chrome 'https://v3x57-gaaaa-aaaab-qadmq-cai.icp0.io/'
