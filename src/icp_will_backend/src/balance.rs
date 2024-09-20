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
