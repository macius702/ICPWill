use candid::CandidType;

#[derive(Clone, CandidType)]
pub struct UserData {
    nickname: String,
    avatar_url: Option<String>,
}

impl UserData {
    pub fn new(nickname: String) -> Self {
        Self {
            nickname,
            avatar_url: None,
        }
    }
}
