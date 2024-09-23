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

    pub fn to_response(&self, has_active_timer: bool) -> ResponseUserData {
        ResponseUserData {
            nickname: self.nickname.clone(),
            avatar_url: self.avatar_url.clone(),
            batch_transfer: self.batch_transfer.clone(),
            has_active_timer,
        }
    }

    pub fn set_batch_transfer(&mut self, batch_transfer: BatchTransfer) {
        self.batch_transfer = Some(batch_transfer);
    }

    pub fn get_batch_transfer(&self) -> Option<BatchTransfer> {
        self.batch_transfer.clone()
    }
}

#[derive(CandidType)]
pub struct ResponseUserData {
    nickname: String,
    avatar_url: Option<String>,
    batch_transfer: Option<BatchTransfer>,
    has_active_timer: bool,
}
