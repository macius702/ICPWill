use std::time::Duration;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk::{caller, id};
use icrc_ledger_types::icrc1::account::Account;
use icrc_ledger_types::icrc1::transfer::{BlockIndex, NumTokens};
use icrc_ledger_types::icrc2::transfer_from::{TransferFromArgs, TransferFromError};
use serde::Serialize;




use crate::constants::LEDGER_CANISTER_ID;
use crate::{btc_send_from_p2pkh, BATCH_TIMERS, TIMERS, USERS};




#[derive(CandidType, Deserialize, Serialize, Debug)]
pub struct TransferArgs {
    pub amount: NumTokens,
    pub to_account: Account,
    pub delay_in_seconds: u64,
    pub from_account: Account,
}

#[ic_cdk::update]
pub async fn transfer(args: TransferArgs) -> Result<BlockIndex, String> {
    ic_cdk::println!("logmtlk transfer {:?}", args);

    ic_cdk::println!(
        "Transferring {} tokens to account {} \nafter {} seconds from account {}",
        &args.amount,
        &args.to_account,
        &args.delay_in_seconds,
        &args.from_account,
        );



    let user = ic_cdk::caller();

    ic_cdk::println!("User is {:#?}", user.to_text());

    ic_cdk::println!("This id: {:#?}", id().to_text());


    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    let secs = Duration::from_secs(
        args.delay_in_seconds
    );
    let amount = args.amount.clone();
    let to_account = args.to_account.clone();

    ic_cdk::println!("Timer canister: Starting a new timer with {secs:?} interval...");
    // Schedule a new periodic task to increment the counter.
    let timer_id = ic_cdk_timers::set_timer(secs, move || {
        let user_clone = user.clone();
        let to_account_clone = to_account.clone();
        let amount_clone = amount.clone();
        ic_cdk::spawn(async move {
            handle_timer_event(user_clone, to_account_clone, amount_clone).await;
        });
    });
    
    USERS.with_borrow_mut(|_users| {
        ic_cdk::println!("Storing timer_id  for possible cancellation later: {:?}", timer_id);

        //add timer_id to TIMERS
        TIMERS.with_borrow_mut(|timers| timers.insert(user, timer_id));

        
    });
    
    ic_cdk::println!("Timer canister: returning from transfer");

    Ok(BlockIndex::from(0 as u32))
}


// TODO(mtlk) implement a button in gui and test
#[ic_cdk::update]
pub fn cancel_activation() -> Result<(), String> {
    ic_cdk::println!("logmtlk cancel_activation");
    let user = caller();

    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    TIMERS.with_borrow_mut(|timers| {
        if let Some(timer_id) = timers.get(&user) {
            ic_cdk_timers::clear_timer(*timer_id);
            timers.remove(&user);
        }
    });

    Ok(())
}


// TODO(mtlk) implement a button in gui and test
#[ic_cdk::update]
pub fn cancel_batch_activation() -> Result<(), String> {
    ic_cdk::println!("logmtlk cancel_batch_activation");
    ic_cdk::println!("Entering cancel_batch_activation");
    let user = caller();

    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    BATCH_TIMERS.with_borrow_mut(|batch_timers| {
        if let Some(&timer_id) = batch_timers.get(&user) {
            ic_cdk_timers::clear_timer(timer_id);
            batch_timers.remove(&user);
            ic_cdk::println!("Successfully cancelled BATCH_TIMER {:?} for user: {}", timer_id, user.to_text());
        }
    });

    ic_cdk::println!("Leaving cancel_batch_activation");

    Ok(())
}

pub async fn btc_handle_timer_event(user : &Principal, target_btc_address: String, amount: u64) {
    ic_cdk::println!("Entering btc_handle_timer_event");

    let user = *user;

    ic_cdk::spawn(async move {
        ic_cdk::println!("btc_handle_timer_event in spawned async block");

        // remove from TIMERS
        //TIMERS.with_borrow_mut(|timers| timers.remove(&user));

        if user == Principal::anonymous() {
            panic!("Anonymous Principal!")
        }

        ic_cdk::println!("btc_handle_timer_event in spawned async block User is {:#?}", user.to_text());

        ic_cdk::println!("btc_handle_timer_event in spawned async block This id: {:#?}", id().to_text());
    
    
        // Convert the Principal to a Vec<Vec<u8>> format.
        let mut user_bytes_vec = Vec::new();
        let user_bytes = user.as_slice().to_vec();
        user_bytes_vec.push(user_bytes);


        ic_cdk::println!("btc_handle_timer_event in spawned async calling btc_send_from_p2pkh {}, {}, {:?}", target_btc_address, amount, user_bytes_vec);

        let result = btc_send_from_p2pkh(target_btc_address, amount, user_bytes_vec).await;

        ic_cdk::println!("btc_handle_timer_event in spawned async AFTER calling btc_send_from_p2pkh result: {result}");

    });

}



pub async fn handle_timer_event(user: Principal, to_account: Account, amount: NumTokens) {
    ic_cdk::println!("Timer canister: in set_timer closure");

    let transfer_args = TransferFromArgs {
        to: to_account.clone(),
        fee: None,
        spender_subaccount: None,
        from: Account {
            owner: user,
            subaccount: None,
        },
        memo: None,
        created_at_time: None,
        amount: amount.clone(),
    };

    let user = user.clone();

    ic_cdk::spawn(async move {
        ic_cdk::println!("Timer canister: in spawned async block");

        // remove from TIMERS
        TIMERS.with_borrow_mut(|timers| timers.remove(&user));

        let result = ic_cdk::call::<(TransferFromArgs,), (Result<BlockIndex, TransferFromError>,)>(
            Principal::from_text(LEDGER_CANISTER_ID)
                .expect("Could not decode the principal."),
            "icrc2_transfer_from",
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
}

// Enable Candid export (see https://internetcomputer.org/docs/current/developer-docs/backend/rust/generating-candid)

