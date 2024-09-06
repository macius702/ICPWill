//use candid::CandidType;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk::caller;
use crate::USERS;
use crate::transfer::TransferArgs;
use icrc_ledger_types::icrc1::transfer::NumTokens;
use icrc_ledger_types::icrc1::account::Account;
use crate::transfer::transfer;


#[derive(Clone, CandidType, Deserialize)]
pub struct Beneficiary {
    pub beneficiary_principal: Principal,
    pub nickname: Option<String>,
    pub amount_icp: u64,
}

#[derive(Clone, CandidType, Deserialize)]
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
        user_data.set_batch_transfer(batch_transfer_data);
        Ok(())
    })
}



async fn batch_transfer(batch: BatchTransfer) -> Result<(), String> {
    for beneficiary in batch.beneficiaries.iter() {
        let account = Account {
            owner: beneficiary.beneficiary_principal,
            subaccount: None, 
        };
        let transfer_args = TransferArgs {
            amount: NumTokens::from(beneficiary.amount_icp),
            to_account: account,
            delay_in_seconds: batch.execution_delay_seconds,
        };

        match transfer(transfer_args).await {
            Ok(block_index) => {
                // Log or handle successful transfer
                ic_cdk::println!("Transfer to {} succeeded, BlockIndex: {}", beneficiary.nickname.as_deref().unwrap_or("Unknown"), block_index);
            },
            Err(e) => {
                // Handle transfer failure
                ic_cdk::println!("Transfer to {} failed: {}", beneficiary.nickname.as_deref().unwrap_or("Unknown"), e);
                return Err(format!("Failed to transfer to {}: {}", beneficiary.nickname.as_deref().unwrap_or("Unknown"), e));
            }
        }
    }
    Ok(())
}


#[ic_cdk::update]
// mtlk genereally we should not react to errors. resulting in partially non successfull batch transfer
// we will repeat repeat the remainging transfers in the next time, according to the repeat ratio then fallback recipient
async fn execute_batch_transfer() -> Result<(), String> {
    ic_cdk::println!("Entering execute_batch_transfer" );
    let user = caller();

    if user == Principal::anonymous() {
        return Err("Anonymous Principal!".to_string());
    }

    let batch_transfer_data = USERS.with_borrow_mut(|users| {
        let user_data = users.get_mut(&user).ok_or("User not found!")?;
        Ok::<_, &'static str>(user_data.batch_transfer.clone().ok_or("No batch transfer data found")?)
    })?;
    


    batch_transfer(batch_transfer_data).await;
    Ok(())
}

