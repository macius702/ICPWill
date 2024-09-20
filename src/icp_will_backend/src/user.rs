use candid::CandidType;
use ic_cdk::api::time;

use crate::batch_transaction_to_execute::BatchTransfer;

#[derive(Clone, CandidType)]
pub struct UserData {
    nickname: String,
    avatar_url: Option<String>,
    batch_transfer: Option<BatchTransfer>,
    last_activity: u64,
}

impl UserData {
    pub fn new(nickname: String) -> Self {
        Self {
            nickname,
            avatar_url: None,
            batch_transfer: None,
            last_activity: time(),
        }
    }

    pub fn set_batch_transfer(&mut self, batch_transfer: BatchTransfer) {
        self.batch_transfer = Some(batch_transfer);
    }

    pub fn get_batch_transfer(&self) -> Option<BatchTransfer> {
        self.batch_transfer.clone()
    }

    pub fn reset_last_activity(&mut self) {
        self.last_activity = time(); // Updates the last_activity field to current timestamp
    }

    pub fn get_last_activity(&self) -> u64 {
        self.last_activity
    }    
}
