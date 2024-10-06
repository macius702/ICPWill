use candid::Principal;
use ic_cdk::api::management_canister::bitcoin::{
    bitcoin_get_balance, bitcoin_get_current_fee_percentiles, bitcoin_get_utxos,
    bitcoin_send_transaction, BitcoinNetwork, GetBalanceRequest, GetCurrentFeePercentilesRequest,
    GetUtxosRequest, GetUtxosResponse, MillisatoshiPerByte, SendTransactionRequest,
};
use crate::{GetBlockHeadersRequest, GetBlockHeadersResponse};

/// Returns the balance of the given bitcoin address.
///
/// Relies on the `bitcoin_get_balance` endpoint.
/// See https://internetcomputer.org/docs/current/references/ic-interface-spec/#ic-bitcoin_get_balance
pub async fn get_balance(network: BitcoinNetwork, address: String) -> u64 {
    let min_confirmations = None;
    ic_cdk::println!("In bitcoin_api::get_balance address: {address} network: {:?} min_confirmations: {:?}",  network, min_confirmations);
    let balance_res = bitcoin_get_balance(GetBalanceRequest {
        address,
        network,
        min_confirmations,
    })
    .await;

    ic_cdk::println!("In bitcoin_api::get_balance balance_res: {:?}", balance_res);

    balance_res.unwrap().0
}

/// Returns the UTXOs of the given bitcoin address.
///
/// NOTE: Relies on the `bitcoin_get_utxos` endpoint.
/// See https://internetcomputer.org/docs/current/references/ic-interface-spec/#ic-bitcoin_get_utxos
pub async fn get_utxos(network: BitcoinNetwork, address: String) -> GetUtxosResponse {
    let filter = None;
    let utxos_res = bitcoin_get_utxos(GetUtxosRequest {
        address,
        network,
        filter,
    })
    .await;

    utxos_res.unwrap().0
}

/// Returns the block headers in the given height range.
pub(crate) async fn get_block_headers(network: BitcoinNetwork, start_height: u32, end_height: Option<u32>) -> GetBlockHeadersResponse{
    let cycles = match network {
        BitcoinNetwork::Mainnet => 10_000_000_000,
        BitcoinNetwork::Testnet => 10_000_000_000,
        BitcoinNetwork::Regtest => 0,
    };

    let request = GetBlockHeadersRequest{
        start_height,
        end_height,
        network
    };

    let res = ic_cdk::api::call::call_with_payment128::<(GetBlockHeadersRequest,), (GetBlockHeadersResponse,)>(
        Principal::management_canister(),
        "bitcoin_get_block_headers",
        (request,),
        cycles,
    )
    .await;

    res.unwrap().0
}

/// Returns the 100 fee percentiles measured in millisatoshi/byte.
/// Percentiles are computed from the last 10,000 transactions (if available).
///
/// Relies on the `bitcoin_get_current_fee_percentiles` endpoint.
/// See https://internetcomputer.org/docs/current/references/ic-interface-spec/#ic-bitcoin_get_current_fee_percentiles
pub async fn get_current_fee_percentiles(network: BitcoinNetwork) -> Vec<MillisatoshiPerByte> {
    let res =
        bitcoin_get_current_fee_percentiles(GetCurrentFeePercentilesRequest { network }).await;

    res.unwrap().0
}

/// Sends a (signed) transaction to the bitcoin network.
///
/// Relies on the `bitcoin_send_transaction` endpoint.
/// See https://internetcomputer.org/docs/current/references/ic-interface-spec/#ic-bitcoin_send_transaction
pub async fn send_transaction(network: BitcoinNetwork, transaction: Vec<u8>) {
    let res = bitcoin_send_transaction(SendTransactionRequest {
        network,
        transaction,
    })
    .await;

    res.unwrap();
}

