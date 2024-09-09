#! /usr/bin/env bash
# feed --network=local identities

# use identity that has much money 
# dfx identity list



current_identity=$(dfx identity whoami)
dfx identity use Alice

echo "\
(
    record {
        to = record {
            owner = principal \"$1\";
            subaccount = null;
        };
        fee = null;
        memo = null;
        from_subaccount = null;
        created_at_time = null;
        amount = 50_000 : nat;
    },
)" > /tmp/argument.txt

dfx canister call mxzaz-hqaaa-aaaar-qaada-cai icrc1_transfer --argument-file /tmp/argument.txt

dfx identity use $current_identity
