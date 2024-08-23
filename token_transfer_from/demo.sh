#!/usr/bin/env bash
dfx killall
set -e
# trap 'dfx stop' EXIT

echo "===========SETUP========="
dfx start --background --clean
sleep 5
dfx identity list

export LEDGER=icrc1_ledger_canister

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
dfx canister call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx identity --identity Alice get-principal)\";
})"
dfx canister call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx identity --identity Bob get-principal)\";
})"
echo "===========SETUP DONE========="

dfx deploy token_transfer_from_backend

# approve the token_transfer_from_backend canister to spend 100 tokens
dfx canister call --identity Alice $LEDGER icrc2_approve "(
  record {
    spender= record {
      owner = principal \"$(dfx canister id token_transfer_from_backend)\";
    };
    amount = 10_000_000_000: nat;
  }
)"

dfx canister call --identity Alice $LEDGER icrc2_allowance  "(record {
  account = record {
    owner = principal \"$(dfx identity --identity Alice get-principal)\";
  };
  spender = record {
    owner = principal \"$(dfx canister id token_transfer_from_backend)\";
  };
})"

dfx canister call token_transfer_from_backend transfer "(record {
  amount = 100_000_000;
  to_account = record {
    owner = principal \"$(dfx identity --identity Bob get-principal)\";
  };
  from_account = record {
    owner = principal \"$(dfx identity --identity Alice get-principal)\";
  };
})"



dfx canister call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx identity --identity Alice get-principal)\";
})"

dfx canister call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx canister id token_transfer_from_backend)\";
})"
dfx canister call $LEDGER icrc1_balance_of "(record {
  owner = principal \"$(dfx identity --identity Bob get-principal)\";
})"

echo "DONE"