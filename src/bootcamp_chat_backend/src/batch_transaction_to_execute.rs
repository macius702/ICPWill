//use candid::CandidType;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk::caller;
use crate::USERS;

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
