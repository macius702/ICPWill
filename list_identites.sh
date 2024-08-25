#!/bin/bash

# Define the identities
identities=("Alice" "Bob" "ControllerExample" "DevJourney" "ForDeployment" "Matiki" "alice_token_transfer" "anonymous" "default" "minter")

# Print the table header
echo -e "Label\tPrincipal\tAccount\tBalance"

# Loop over the identities
for identity in "${identities[@]}"; do
    # Get the principal
    principal=$(dfx identity get-principal --identity "$identity")

    # Get the account
    account=$(dfx ledger account-id --ic --identity "$identity")

    # Get balance on --ic mainnet
    balance=$(dfx ledger balance  --ic "$account" )


    # Print the row
    echo -e "$identity\t$principal\t$account\t$balance"
done


declare -A principals=(
    ["2435207"]="zgcr3-w3e7h-6okfu-e5dke-k66xm-kadri-lvnuw-kipko-mysl7-r6p53-xae"
    ["2592343"]="agt74-uhoi3-3eolc-fwiby-qcr6q-b2w7a-gcy7v-t3bpi-rpie2-6yqai-aae"
)


# Loop over the labels and principals
for label in "${!principals[@]}"; do
    # Get the principal
    principal=${principals[$label]}

    # Get the account
    account=$(dfx ledger account-id --of-principal "$principal")

    # Get balance on --ic mainnet
    balance=$(dfx ledger balance  --ic "$account" )

    # Print the row
    echo -e "$label\t$principal\t$account\t$balance"
done

