use candid::CandidType;

use crate::batch_transaction_to_execute::BatchTransfer;

#[derive(Clone, CandidType)]
pub struct UserData {
    nickname: String,
    avatar_url: Option<String>,
    batch_transfer: Option<BatchTransfer>,
}

impl UserData {
    pub fn new(nickname: String) -> Self {
        Self {
            nickname,
            avatar_url: None,
            batch_transfer: None,
        }
    }

    pub fn set_batch_transfer(&mut self, batch_transfer: BatchTransfer) {
        self.batch_transfer = Some(batch_transfer);
    }
}
