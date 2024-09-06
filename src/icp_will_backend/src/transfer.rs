use std::time::Duration;

use candid::{CandidType, Deserialize, Principal};
use icrc_ledger_types::icrc1::account::Account;
use icrc_ledger_types::icrc1::transfer::{BlockIndex, NumTokens, TransferArg, TransferError};

use serde::Serialize;




use crate::constants::LEDGER_CANISTER_ID;




#[derive(CandidType, Deserialize, Serialize)]
pub struct TransferArgs {
    pub amount: NumTokens,
    pub to_account: Account,
    pub delay_in_seconds: u64,
}

#[ic_cdk::update]
pub async fn transfer(args: TransferArgs) -> Result<BlockIndex, String> {
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


        let transfer_args = TransferArg {
            memo: None,
            amount: amount.clone(),

            from_subaccount: None,
            fee: None,
            to: to_account.clone(),
            created_at_time: None,
        };  

    

        ic_cdk::spawn(async {
            ic_cdk::println!("Timer canister: in spawned async block");
        
            let result =ic_cdk::call::<(TransferArg,), (Result<BlockIndex, TransferError>,)>(
                Principal::from_text(LEDGER_CANISTER_ID)
                    .expect("Could not decode the principal."),
                "icrc1_transfer",
                (transfer_args,),
            )
            .await
            .map_err(|e| format!("failed to call ledger: {:?}", e))
            .and_then(|response| response.0.map_err(|e| format!("ledger transfer error {:?}", e)));
        
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

