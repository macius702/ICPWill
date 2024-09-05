#! /usr/bin/env bash
# feed --network=local identities

# use identity that has much money 
# dfx identity list
# dfx identity use Alice
dfx canister call mxzaz-hqaaa-aaaar-qaada-cai icrc1_transfer 


# Sending the following argument:
# (
#   record {
#     to = record {
#       owner = principal "3pcvf-viyad-4xpxd-33uyu-smucs-yamkh-p2fat-2lzof-6xzox-4afx4-sae";
#       subaccount = null;
#     };
#     fee = null;
#     memo = opt blob "325";
#     from_subaccount = null;
#     created_at_time = null;
#     amount = 1_000_000_000 : nat;
#   },
# )
