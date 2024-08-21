#!/usr/bin/env bash
dfx killall
dfx stop
# set -e
# trap 'dfx stop' EXIT

echo "===========SETUP========="
dfx start --background --clean
sleep 5

deploy_ledger_canister() {
  local initial_balance=$1
  local minter=$2
  local default=$3
  dfx deploy icrc1_ledger_canister --argument "(variant { Init =
  record {
     token_symbol = \"ICRC1\";
     token_name = \"L-ICRC1\";
     minting_account = record { owner = principal \"${minter}\" };
     transfer_fee = 0_000;
     metadata = vec {};
     initial_balances = vec { record { record { owner = principal \"${default}\"; }; ${initial_balance}; }; };
     archive_options = record {
       num_blocks_to_archive = 1000;
       trigger_threshold = 2000;
       controller_id = principal \"${minter}\";
     };
   }
  })"
}

get_balance() {
  local default=$1
  result=$(dfx canister call icrc1_ledger_canister icrc1_balance_of "(record { owner = principal \"${default}\"; })")
  echo $result
}

balances() {
  echo "++++++++Balance of  default identity $DEFAULT_PRINCIPAL_ID" $(get_balance $DEFAULT_PRINCIPAL_ID)
  echo "++++++++Balance of  Matiki identity $(dfx --identity Matiki identity get-principal)" $(get_balance $(dfx --identity Matiki identity get-principal))
  echo "++++++++Balance of canister token_transfer_backend $(dfx canister id token_transfer_backend)" $(get_balance "$(dfx canister id token_transfer_backend)")
}

ledger_transfer_to() {
    local to=$1
    local amount=$2
    dfx canister call icrc1_ledger_canister icrc1_transfer "(record {
      to = record {
        owner = principal \"${to}\";
      };
      amount = ${amount};
    })"
}

canister_transfer_to() {
    local amount=$1
    local to_account=$2
    dfx canister call token_transfer_backend transfer "(record {
      amount = ${amount};
      to_account = record {
        owner = principal \"${to_account}\";
      };
    })"
}

dfx identity new alice_token_transfer --storage-mode plaintext --force
export MINTER_PRINCIPAL_ID=$(dfx --identity anonymous identity get-principal)
export DEFAULT_PRINCIPAL_ID=$(dfx identity get-principal)
deploy_ledger_canister 10_000_000_000 $MINTER_PRINCIPAL_ID $DEFAULT_PRINCIPAL_ID

echo "++++++++Balance of  default identity $DEFAULT_PRINCIPAL_ID" $(get_balance $DEFAULT_PRINCIPAL_ID)

dfx deploy token_transfer_backend
echo "===========SETUP DONE========="
balances

echo "===========ledger TRANSFER========="
ledger_transfer_to "$(dfx canister id token_transfer_backend)" "9_000_000_000"
balances

echo "===========canister TRANSFER========="
canister_transfer_to 1_000_000_000 "$(dfx identity get-principal)"
balances

echo "===========canister TRANSFER========="
canister_transfer_to 1_000_000_000 "$(dfx --identity Matiki identity get-principal)"
balances

echo "DONE"