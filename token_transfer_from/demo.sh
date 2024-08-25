#!/usr/bin/env bash
#  If you run the script without any arguments, `MODE` will be set to `local`.
# can be run with `local` or `nonlocal` as a script argument
MODE=${1:-local}

# in nonllocal mode feed Alice with some ICP first:
# dfx ledger --ic transfer --identity Matiki --amount 0.01 --memo 9 $(dfx ledger account-id  --identity Alice)

if [ "$MODE" = "local" ]; then
  echo "Building in local mode"
else
  echo "Building in non-local mode"
fi

dfx killall
set -e

echo "===========SETUP========="
dfx start --background --clean
sleep 5
dfx identity list

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

function balance() {
  local identity=$1
  # --identity Matiki is only to silence a warning about the identity 'default'
  dfx canister $NETWORK call --identity Matiki $LEDGER icrc1_balance_of "(record {
      owner = principal \"$(dfx identity --identity $identity get-principal)\";
    })"
}

function balance_of_canister() {
  local canister_name=$1
  dfx canister $NETWORK call $LEDGER icrc1_balance_of "(record {
      owner = principal \"$(dfx canister id $canister_name)\";
    })"
}
PUSH_RED="\e[31m"
PUSH_GREEN="\e[32m"
PUSH_YELLOW="\e[33m"
POP="\e[0m"

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

fi

balance Matiki
MatikiBalanceBefore=$(balance Matiki)

balance Alice
balance Bob
BobBalanceBefore=$(balance Bob)

echo "===========SETUP DONE========="

balance Alice

dfx deploy $PLAYGROUND token_transfer_from_backend
export BACKEND_CANISTER_ID=$(dfx canister $PLAYGROUND id token_transfer_from_backend)

echo -e "${PUSH_YELLOW}BACKEND_CANISTER_ID: $BACKEND_CANISTER_ID$POP"

echo "===========APPROVE========="
# approve the token_transfer_from_backend canister to spend 300 + transfer fee tokens
dfx canister $NETWORK call --identity Alice $LEDGER icrc2_approve "(
  record {
    spender= record {
      owner = principal \"$BACKEND_CANISTER_ID\";
    };
    amount = 10_300: nat;
  }
)"

echo =========ALLOWANCE is what is approved
dfx canister $NETWORK call --identity Alice $LEDGER icrc2_allowance "(
  record {
    account = record {
      owner = principal \"$(dfx identity --identity Alice get-principal)\";
    };
    spender = record {
      owner = principal \"$BACKEND_CANISTER_ID\";
  };
})"

balance Alice

echo "===========TRANSFER========="
dfx canister $NETWORK call $BACKEND_CANISTER_ID transfer "(record {
  amount = 300;
  to_account = record {
    owner = principal \"$(dfx identity $NETWORK --identity Bob get-principal)\";
  };
  from_account = record {
    owner = principal \"$(dfx identity $NETWORK --identity Alice get-principal)\";
  };
  delay_in_seconds = 20;
})"
balance Alice
balance Bob

dfx canister $NETWORK call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx canister $PLAYGROUND id token_transfer_from_backend)\";
})"

function check_bob_balance_increase {
  local BobBalanceAfter=$(balance Bob)

  # BoB balances are in the form (3_300 : nat), so we need to parse them before subtraction
  BobBalanceBefore=$(echo $BobBalanceBefore | tr -d '_' | sed 's/.*(\([0-9]*\).*/\1/')
  BobBalanceAfter=$(echo $BobBalanceAfter | tr -d '_' | sed 's/.*(\([0-9]*\).*/\1/')
  if [ $((BobBalanceAfter - BobBalanceBefore)) -ne 300 ]; then
    echo -e "${PUSH_RED}Error: Bob's balance hasn't increased by 300$POP"
  else
    echo -e "${PUSH_GREEN}OK: Bob's balance has increased by 300$POP"
  fi
}

check_bob_balance_increase

sleep 20

balance Alice
balance Bob
balance Matiki

MatikiBalanceAfter=$(balance Matiki)
if [ "$MatikiBalanceBefore" == "$MatikiBalanceAfter" ]; then
  echo "Matiki balance hasn't changed."
else
  echo "${PUSH_RED}Error: Matiki balance has changed !!!$POP"
fi

check_bob_balance_increase

echo "DONE"
