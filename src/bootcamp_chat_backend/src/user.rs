use candid::CandidType;

#[derive(Clone, CandidType)]
pub struct UserData {
    nickname: String,
    pub source_btc_address: Option<String>,
    pub target_btc_address: Vec<String>,
    avatar_url: Option<String>,
}

impl UserData {
    pub fn new(nickname: String) -> Self {
        Self {
            nickname,
            source_btc_address: None,
            target_btc_address: Vec::new(),
            avatar_url: None,
        }
    }
}
