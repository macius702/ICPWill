use std::{cell::RefCell, collections::HashMap};

use candid::Principal;
use ic_cdk::caller;
use user::UserData;

pub mod user;
pub mod transfer;

thread_local! {
    static CHAT: RefCell<HashMap<[Principal; 2], Vec<String>>> = RefCell::default();
    static USERS: RefCell<HashMap<Principal, UserData>> = RefCell::default();
}

#[ic_cdk::update]
fn register(nick: String) {
    let user = caller();

    if user == Principal::anonymous() {
        panic!("Anonymous Principal!")
    }

    USERS.with_borrow_mut(|users| users.insert(user, UserData::new(nick)));
}

#[ic_cdk::query]
fn get_users() -> HashMap<Principal, UserData> {
    USERS.with_borrow(|users| users.clone())
}

#[ic_cdk::query]
fn get_user(user: Principal) -> Option<UserData> {
    USERS.with_borrow(|users| users.get(&user).cloned())
}

#[ic_cdk::query]
fn get_chat(mut chat_path: [Principal; 2]) -> Option<Vec<String>> {
    chat_path.sort();    

    ic_cdk::println!("{:?}", chat_path);    
    let result = CHAT.with_borrow(|chats| chats.get(&chat_path).cloned());
    ic_cdk::println!("{:?}", result);
    return result;
}

#[ic_cdk::update]
fn add_chat_msg(msg: String, user2: Principal) {
    let user1 = caller();

    ic_cdk::println!("In add_chat_msg user1: {:#?}", user1);

    if user1 == Principal::anonymous() {
        panic!("Anonymous Principal!")
    }

    let is_user_registered = USERS.with_borrow(|users| users.contains_key(&user1));

    ic_cdk::println!("In add_chat_msg is_user_registered: {:#?}", is_user_registered);

    if !is_user_registered {
        panic!("Not registered!")
    }

    let mut principals = [user1, user2];
    principals.sort();
    ic_cdk::println!("sorted principals {:#?}",   principals);
    

    CHAT.with_borrow_mut(|chats| {
        let mut_chat = chats.get_mut(&principals);
        ic_cdk::println!("mut_char {:#?}", mut_chat);

        if let Some(chat_msgs) = mut_chat {
            ic_cdk::println!("not first {:#?}", chat_msgs);            

            chat_msgs.push(msg);
            ic_cdk::println!("{:#?}", chat_msgs);            
        } else {
            chats.insert(principals, vec![msg]);
            ic_cdk::println!("first {:#?}", chats);            

        }
        ic_cdk::println!("In add_chat_msg  After insertin {:#?}", chats);
    })
}
