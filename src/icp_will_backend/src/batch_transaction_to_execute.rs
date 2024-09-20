//use candid::CandidType;

use std::time::Duration;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk::caller;
use crate::{BATCH_TIMERS, USERS};
use crate::transfer::handle_timer_event;
use icrc_ledger_types::icrc1::transfer::NumTokens;
use icrc_ledger_types::icrc1::account::Account;


#[derive(Clone, CandidType, Deserialize, Debug)]
pub struct Beneficiary {
    pub beneficiary_principal: Principal,
    pub nickname: String,
    pub amount_icp: u64,
}

#[derive(Clone, CandidType, Deserialize, Debug)]
pub struct BatchTransfer {
    pub beneficiaries: Vec<Beneficiary>,
    pub execution_delay_seconds: u64,
}

#[ic_cdk::update]
fn register_batch_transfer(batch_transfer_data: BatchTransfer) -> Result<(), String> {
    ic_cdk::println!("Entering register_batch_transfer" );
    let user = caller();

    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    USERS.with_borrow_mut(|users| {
        let user_data = users.get_mut(&user).ok_or("User not found!")?;
        user_data.reset_last_activity();
        ic_cdk::println!("Registering batch transfer: batch_transfer_data {:?}", batch_transfer_data);
        user_data.set_batch_transfer(batch_transfer_data);
        Ok(())
    })
}



async fn batch_transfer_timer_handler(caller : &Principal, batch: BatchTransfer) -> Result<(), String> {
    for beneficiary in batch.beneficiaries.iter() {
        let to_account = Account {
            owner: beneficiary.beneficiary_principal,
            subaccount: None, 
        };
        let amount = NumTokens::from(beneficiary.amount_icp);
        
        
        ic_cdk::println!("Handling timer event for user: {}", caller.to_text());
               
        handle_timer_event(*caller, to_account, amount).await;
    }

    // Remove the timer once the batch transfer completes
    BATCH_TIMERS.with_borrow_mut(|timers| {
        if timers.remove(caller).is_some() {
            ic_cdk::println!("Successfully removed BATCH_TIMER for user: {}", caller.to_text());
        } else {
            ic_cdk::println!("No active BATCH_TIMER found for user: {}", caller.to_text());
        }
    });        
    Ok(())
}

// mtlk genereally we should not react to errors. resulting in partially non successfull batch transfer
// we will repeat repeat the remainging transfers the next time, according to the repeat ratio then fallback recipient
#[ic_cdk::update]
async fn execute_batch_transfers() -> Result<(), String> {
    ic_cdk::println!("Entering execute_batch_transfers");
    let user = ic_cdk::caller();

    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    let batch_transfer_data = USERS.with_borrow_mut(|users| {
        let user_data = users.get_mut(&user).ok_or("User not found!")?;
        user_data.reset_last_activity();        
        Ok::<_, &'static str>(user_data.get_batch_transfer().clone().ok_or("No batch transfer data found")?)
    })?;

    ic_cdk::println!("Scheduling batch transfer: batch_transfer_data {:?}", batch_transfer_data);

    let secs = Duration::from_secs(batch_transfer_data.execution_delay_seconds);
    
    // Schedule the timer to execute batch transfer after the delay
    let timer_id = ic_cdk_timers::set_timer(secs, move || {
        let user_clone = user.clone();
        let batch_transfer_data_clone = batch_transfer_data.clone();

        ic_cdk::spawn(async move {
            ic_cdk::println!("Executing batch transfer for user: {}", user_clone.to_text());

            match batch_transfer_timer_handler(&user_clone, batch_transfer_data_clone).await {
                Ok(_) => ic_cdk::println!("Batch transfer successful for user: {}", user_clone.to_text()),
                Err(e) => ic_cdk::println!("Batch transfer failed for user {}: {}", user_clone.to_text(), e),
            }
        });
    });

    USERS.with_borrow_mut(|_users| {
        ic_cdk::println!("Storing timer_id for possible cancellation later: {:?}", timer_id);
        BATCH_TIMERS.with_borrow_mut(|timers| timers.insert(user, timer_id));
    });

    Ok(())
}

