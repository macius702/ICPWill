use candid::{Principal, Nat};
use icrc_ledger_types::icrc1::account::Account;
use icrc_ledger_types::icrc1::transfer::NumTokens;
use ic_cdk::api::call::CallResult;
use crate::constants::LEDGER_CANISTER_ID;



#[ic_cdk::update]
async fn get_balance() -> Result<NumTokens, String> {

    let principal  = ic_cdk::caller();
    //make an account oft of the caller
    let account: Account = Account::from(principal);
    ic_cdk::println!("Getting balance for account which is caller's {}", account);


    // Call the icrc1_balance_of method on the ledger canister
    let result: CallResult<(Nat,)> = ic_cdk::call(
        Principal::from_text(LEDGER_CANISTER_ID)
            .expect("Could not decode the principal."),
        "icrc1_balance_of",
        (account,),
    ).await;


   match result {
    Ok((balance,)) => {
        // Convert Nat to NumTokens (assuming NumTokens is a type alias for Nat)
        ic_cdk::println!("Got balance {} for account which is caller's {}", balance, account);
        Ok(balance.into())
    },
    Err((rejection_code, msg)) => Err(format!(
        "Failed to call ledger canister. Rejection code: {:?}, message: {}",
        rejection_code, msg
    )),
}
}






// use candid::{CandidType, Deserialize, Principal};
// use icrc_ledger_types::icrc1::account::Account;
// use icrc_ledger_types::icrc1::transfer::NumTokens;
// use ic_cdk::api::call::CallResult;
// use serde::Serialize;


// const LEDGER_CANISTER_ID: &'static str = env!("LEDGER_CANISTER_ID");

// #[derive(CandidType, Deserialize, Serialize)]
// pub struct BalanceOfArgs {
//     account: Account,
// }

// #[ic_cdk::query]
// async fn get_balance(args: BalanceOfArgs) -> Result<NumTokens, String> {
//     ic_cdk::println!("Getting balance for account {}", &args.account);

//     // 1. Asynchronously call another canister function using `ic_cdk::call`.
//     let result: CallResult<(Result<NumTokens, String>,)> = ic_cdk::call(
//         // 2. Convert a textual representation of a Principal into an actual `Principal` object.
//         Principal::from_text(LEDGER_CANISTER_ID)
//             .expect("Could not decode the principal."),
//         // 3. Specify the method name on the target canister to be called, in this case, "icrc1_balance_of".
//         "icrc1_balance_of",
//         // 4. Provide the arguments for the call in a tuple, here `args.account` is encapsulated as a single-element tuple.
//         (args.account,),
//     )
//     .await
//     // 5. Apply `map_err` to transform any network or system errors encountered during the call into a more readable string format.
//     .map_err(|e| format!("failed to call ledger: {:?}", e))?;

//     // 6. Access the first element of the tuple, which is the `Result<NumTokens, String>`, for further processing.
//     result.0
//     // 7. Use `map_err` again to transform any specific errors into a readable string format.
//     .map_err(|e| format!("ledger balance query error: {:?}", e))
// }

// // Enable Candid export (see https://internetcomputer.org/docs/current/developer-docs/backend/rust/generating-candid)







// // use candid::{CandidType, Deserialize, Nat, Principal};

// // //use ic_cdk::export::Principal;
// // use ic_cdk::api::call::{CallResult, call};
// // //use ic_cdk::call_raw;
// // use std::future::Future;

// // use icrc_ledger_types::icrc1::account::Account;

// // const LEDGER_CANISTER_ID: &'static str = env!("LEDGER_CANISTER_ID");



// // // pub struct Account {
// // //     pub owner: Principal,
// // //     pub subaccount: Option<Subaccount>,
// // // }


// // // Define Tokens type (example)
// // #[derive(CandidType, Deserialize)]
// // struct Tokens {
// //     amount: Nat,  // Assuming Tokens is a wrapper for Nat
// // }

// // #[ic_cdk::query]
// // pub async fn get_balance(account: Account) -> Result<Tokens, (RejectionCode, String)> {
// //     let ledger_canister_id = Principal::from_text(LEDGER_CANISTER_ID)
// //         .expect("Could not decode the principal.");

// //         let result: CallResult<Tokens> = ic_cdk::call::<(Account,), Tokens>(
// //             ledger_canister_id,
// //             "icrc1_balance_of",
// //             (account,)
// //         ).await;
// //                                     // ic_cdk::call::<(TransferArg,), (Result<BlockIndex, TransferError>,)>(


//     // pub async fn fee(&self) -> Result<Nat, (i32, String)> {
//     //     self.runtime
//     //         .call(self.ledger_canister_id, "icrc1_fee", ())
//     //         .await
//     //         .map(untuple)
//     // }    

// //     match result {
// //         Ok(tokens) => Ok(tokens),
// //         Err((code, msg)) => {
// //             ic_cdk::println!("Error getting balance: {} - {}", code as u8, msg);
// //             Err((code, msg))
// //         }
// //     }
// // }


// // use candid::Principal;
// // use icrc_ledger_types::icrc1::account::Account;
// // //use icrc_ledger_types::icrc1::transfer::NumTokens;
// // use icrc_ledger_types::icrc1::transfer::NumTokens as Tokens;


// // const LEDGER_CANISTER_ID: &'static str = env!("LEDGER_CANISTER_ID");


// // //pub type Tokens = NumTokens;


// // #[ic_cdk::query]
// // async fn balance_of(account: Account) -> candid::Nat {
// //     ic_cdk::println!("Getting balance of account {}", &account);

// //     // Asynchronously call another canister function using `ic_cdk::call`.
// //     let result: Result<candid::Nat, (RejectionCode, String)> = ic_cdk::call(
// //         // Convert a textual representation of a Principal into an actual `Principal` object.
// //         Principal::from_text(LEDGER_CANISTER_ID)
// //             .expect("Could not decode the principal."),
// //         // Specify the method name on the target canister to be called.
// //         "icrc1_balance_of",
// //         // Provide the arguments for the call in a tuple.
// //         (account,),
// //     )
// //     .await // Await the completion of the asynchronous call.
// //     // Transform any network or system errors encountered during the call into a more readable string format.
// //     ;
// //     // Return the result.
// //     result
// // }



// // async fn fetch_wallet_address(staking_pool_canister: CanisterId) -> Result<String, Error> {
// //     let resp: Result<(String,), _> =
// //         ic_cdk::call(staking_pool_canister, "p2wsh_multisig22_address", ((),))
// //             .await
// //             .map_err(|msg| Error::GetStakingPoolAddressFailed {
// //                 msg: format!("{msg:?}"),
// //             });

// //     resp.map(|(address,)| address)
// // }
