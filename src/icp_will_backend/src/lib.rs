use std::{cell::RefCell, collections::HashMap};

use candid::Principal;
use ic_cdk::caller;
use ic_cdk_timers::TimerId;
use user::UserData;

pub mod constants;
pub mod user;
pub mod batch_transaction_to_execute;
pub mod transfer;
pub mod balance;

use crate::batch_transaction_to_execute::get_batch_transfer_data;
use crate::batch_transaction_to_execute::schedule_batch_transfer;

thread_local! {
    static CHAT: RefCell<HashMap<[Principal; 2], Vec<String>>> = RefCell::default();
    static USERS: RefCell<HashMap<Principal, UserData>> = RefCell::default();
    static TIMERS: RefCell<HashMap<Principal, TimerId>> = RefCell::default();
    static BATCH_TIMERS: RefCell<HashMap<Principal, TimerId>> = RefCell::default();
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
fn announce_activity() {
    let user = caller();

    ic_cdk::println!("In Rust announce_activity: {:#?}", user);

    if user == Principal::anonymous() {
        panic!("Anonymous Principal!")
    }
    reinstantiate_timer(user);
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


pub fn reinstantiate_timer(user: Principal) {
    ic_cdk::println!("Rust reinstantiate_timer ->>> Starting reinstantiate_timer for user: {}", user.to_text());


    let user_data = USERS.with_borrow(|users| users.get(&user).cloned());

    if let Some(user_data) = user_data {
        ic_cdk::println!("Rust reinstantiate_timer ->>> User data found for user: {}", user.to_text());


        if let Some(batch_transfer) = user_data.get_batch_transfer() {
            ic_cdk::println!("Rust reinstantiate_timer ->>> Batch transfer data retrieved for user: {:?}", batch_transfer);

            if batch_transfer.of_inactivity {
                ic_cdk::println!("Rust reinstantiate_timer ->>> User has been inactive, processing BATCH_TIMER...");


                let batch_timer_removed = BATCH_TIMERS.with_borrow_mut(|timers| timers.remove(&user).is_some());

                if batch_timer_removed {
                    ic_cdk::println!("Rust reinstantiate_timer ->>> Successfully removed BATCH_TIMER for user: {}", user.to_text());

                    // Fetch batch transfer data and proceed
                    match get_batch_transfer_data(user) {
                        Ok(batch_transfer_data) => {
                            ic_cdk::println!("Rust reinstantiate_timer ->>> Scheduling batch transfer: {:?}", batch_transfer_data);
                            schedule_batch_transfer(user, batch_transfer_data);
                        }
                        Err(e) => {
                            ic_cdk::println!("Rust reinstantiate_timer ->>> Error retrieving batch transfer data: {}", e);
                        }
                    }
                } else {
                    ic_cdk::println!("Rust reinstantiate_timer ->>> No active BATCH_TIMER found for user: {}", user.to_text());
                }
            } else {
                ic_cdk::println!("User has been active, no need to reset timer.");
            }
        } else {
            ic_cdk::println!("No batch transfer data available for user: {}", user.to_text());
        }


        ic_cdk::println!("User last activity reset for user: {}", user.to_text());
    }

    ic_cdk::println!("reinstantiate_timer completed for user: {}", user.to_text());
}

