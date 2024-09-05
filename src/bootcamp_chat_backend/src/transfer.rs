use std::time::Duration;

use candid::{CandidType, Deserialize, Principal};
use icrc_ledger_types::icrc1::account::Account;
use icrc_ledger_types::icrc1::transfer::{BlockIndex, NumTokens, TransferArg, TransferError};

use serde::Serialize;




use crate::constants::LEDGER_CANISTER_ID;




#[derive(CandidType, Deserialize, Serialize)]
pub struct MyTransferArgs {
    amount: NumTokens,
    to_account: Account,
    delay_in_seconds: u64,
}

#[ic_cdk::update]
async fn transfer(args: MyTransferArgs) -> Result<BlockIndex, String> {
    ic_cdk::println!(
        "Transferring {} tokens to account {} \nafter {} seconds",
        &args.amount,
        &args.to_account,
        &args.delay_in_seconds,
        );

    let secs = Duration::from_secs(
        args.delay_in_seconds
    );
    let amount = args.amount.clone();
    let to_account = args.to_account.clone();

    ic_cdk::println!("Timer canister: Starting a new timer with {secs:?} interval...");
    // Schedule a new periodic task to increment the counter.
    let _timer_id = ic_cdk_timers::set_timer(secs, move || {
        ic_cdk::println!("Timer canister: in set_timer closure");
        // To drive an async function to completion inside the timer handler,
        // use `ic_cdk::spawn()`, for example:
        // ic_cdk_timers::set_timer_interval(interval, || ic_cdk::spawn(async_function()));


        let transfer_args = TransferArg {
            // the account we want to transfer tokens from (in this case we assume the caller approved the canister to spend funds on their behalf)
            // can be used to distinguish between transactions
            memo: None,
            // the amount we want to transfer
            amount: amount.clone(),

            from_subaccount: None,
            // the subaccount we want to spend the tokens from (in this case we assume the default subaccount has been approved)
            // if not specified, the default fee for the canister is used
            fee: None,
            // the account we want to transfer tokens to
            to: to_account.clone(),
            // a timestamp indicating when the transaction was created by the caller; if it is not specified by the caller then this is set to the current ICP time
            created_at_time: None,
        };  

    

        ic_cdk::spawn(async {
            // Your async code here
            ic_cdk::println!("Timer canister: in spawned async block");
        
            // 1. Asynchronously call another canister function using `ic_cdk::call`.
            let result =ic_cdk::call::<(TransferArg,), (Result<BlockIndex, TransferError>,)>(
                // 2. Convert a textual representation of a Principal into an actual `Principal` object. The principal is the one we specified in `dfx.json`.
                //    `expect` will panic if the conversion fails, ensuring the code does not proceed with an invalid principal.
                Principal::from_text(LEDGER_CANISTER_ID)
                    .expect("Could not decode the principal."),
                // 3. Specify the method name on the target canister to be called, in this case, "icrc1_transfer".
                "icrc1_transfer",
                // 4. Provide the arguments for the call in a tuple, here `transfer_args` is encapsulated as a single-element tuple.
                (transfer_args,),
            )
            .await // 5. Await the completion of the asynchronous call, pausing the execution until the future is resolved.
            // 6. Apply `map_err` to transform any network or system errors encountered during the call into a more readable string format.
            //    The `?` operator is then used to propagate errors: if the result is an `Err`, it returns from the function with that error,
            //    otherwise, it unwraps the `Ok` value, allowing the chain to continue.
            .map_err(|e| format!("failed to call ledger: {:?}", e))
            .and_then(|response| response.0.map_err(|e| format!("ledger transfer error {:?}", e)));
        
                        // 7. Access the first element of the tuple, which is the `Result<BlockIndex, TransferError>`, for further processing.
            // 8. Use `map_err` again to transform any specific ledger transfer errors into a readable string format, facilitating error handling and debugging.
            ic_cdk::println!("Timer canister: in spawned async block after call");
    
            match result {
                Ok(block_index) => {
                    ic_cdk::println!("Transfer successful. Block index: {}", block_index);
                }
                Err(e) => {
                    ic_cdk::println!("Transfer failed: {:?}", e);
                }
            }

        });
    });

    ic_cdk::println!("Timer canister: returning from transfer");

    Ok(BlockIndex::from(0 as u32))
}


// Enable Candid export (see https://internetcomputer.org/docs/current/developer-docs/backend/rust/generating-candid)

