#!/usr/bin/env bash
dfx killall
set -e
# trap 'dfx stop' EXIT

echo "===========SETUP========="
dfx start --background --clean
sleep 5
dfx identity list

# export LEDGER=icrc1_ledger_canister
# export NETWORK=

# export LEDGER=icrc1_ledger_canister
# export NETWORK=
export LEDGER=ryjl3-tyaaa-aaaaa-aaaba-cai
export NETWORK=--ic


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



# dfx deploy $LEDGER --argument "(variant {
#   Init = record {
#     token_symbol = \"ICRC1\";
#     token_name = \"L-ICRC1\";
#     minting_account = record {
#       owner = principal \"$(dfx identity --identity anonymous get-principal)\"
#     };
#     transfer_fee = 10_000;
#     metadata = vec {};
#     initial_balances = vec {
#       record {
#         record {
#           owner = principal \"$(dfx identity --identity Alice get-principal)\";
#         };
#         10_000_000_000;
#       };
#     };
#     archive_options = record {
#       num_blocks_to_archive = 1000;
#       trigger_threshold = 2000;
#       controller_id = principal \"$(dfx identity --identity anonymous get-principal)\";
#     };
#     feature_flags = opt record {
#       icrc2 = true;
#     };
#   }
# })"

balance Matiki
MatikiBalanceBefore=$(balance Matiki)

balance Alice
balance Bob

echo "===========SETUP DONE========="

dfx deploy --playground token_transfer_from_backend
balance Alice


export BACKEND_CANISTER_ID=$(dfx canister --playground id token_transfer_from_backend)
echo -e "\e[33mBACKEND_CANISTER_ID on playground: $BACKEND_CANISTER_ID\e[0m"


echo "===========APPROVE========="
# approve the token_transfer_from_backend canister to spend 100 tokens
dfx canister $NETWORK call --identity Alice $LEDGER icrc2_approve "(
  record {
    spender= record {
      owner = principal \"$BACKEND_CANISTER_ID\";
    };
    amount = 10_300: nat;
  }
)"

balance Alice


echo -e "\e[31mPerhaps this backend canister does not have enough cycles??\e[0m"





echo "===========TRANSFER========="
dfx canister $NETWORK call $BACKEND_CANISTER_ID transfer "(record {
  amount = 300;
  to_account = record {
    owner = principal \"$(dfx identity $NETWORK --identity Bob get-principal)\";
  };
  from_account = record {
    owner = principal \"$(dfx identity $NETWORK --identity Alice get-principal)\";
  };
})"
balance Alice
balance Bob



dfx canister $NETWORK call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx canister --playground id token_transfer_from_backend)\";
})"

balance Matiki

MatikiBalanceAfter=$(balance Matiki)
if [ "$MatikiBalanceBefore" == "$MatikiBalanceAfter" ]; then
    echo "Matiki balance hasn't changed."
else
    echo "\e[31mMatiki balance has changed !!!\e[0m"
fi


echo "DONE"