dfx identity list | while IFS= read -r line; do
    echo "Processing: $line"
    ./ledger_getbalance.sh "$(dfx identity get-principal --identity $line)"
done