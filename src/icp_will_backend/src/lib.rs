use std::{cell::RefCell, collections::HashMap};

use basic_bitcoin;
use basic_bitcoin::SendRequest;
use candid::Principal;
use ic_cdk::api::management_canister::bitcoin::BitcoinNetwork;
use ic_cdk::caller;
use ic_cdk_timers::TimerId;
use user::{UserData, ResponseUserData};

pub mod constants;
pub mod user;
pub mod batch_transaction_to_execute;
pub mod transfer;
pub mod balance;

use crate::batch_transaction_to_execute::get_batch_transfer_data;
use crate::batch_transaction_to_execute::schedule_batch_transfer;

use icrc_ledger_types::icrc1::transfer::NumTokens;
use crate::batch_transaction_to_execute::BatchTransfer;
use crate::transfer::TransferArgs;
use icrc_ledger_types::icrc1::transfer::BlockIndex;

thread_local! {
    static CHAT: RefCell<HashMap<[Principal; 2], Vec<String>>> = RefCell::default();
    static USERS: RefCell<HashMap<Principal, UserData>> = RefCell::default();
    static TIMERS: RefCell<HashMap<Principal, TimerId>> = RefCell::default();
    static BATCH_TIMERS: RefCell<HashMap<Principal, TimerId>> = RefCell::default();
}

#[ic_cdk::update]
async fn register(nick: String) {
    
    ic_cdk::println!("logmtlk register {nick}");

    ic_cdk::println!("Entering function: fn register");

    let user = caller();

    if user == Principal::anonymous() {
        panic!("Anonymous Principal!")
    }

    // Convert the Principal to a Vec<Vec<u8>> format.
    let mut user_bytes_vec = Vec::new();
    let user_bytes = user.as_slice().to_vec();
    user_bytes_vec.push(user_bytes);

    ic_cdk::println!("fn register Derivation Path: {:?}", user_bytes_vec);

    let user_btc_addres = btc_get_p2pkh_address(user_bytes_vec).await;
    ic_cdk::println!("fn register user_btc_addres: {}", user_btc_addres);

    USERS.with_borrow_mut(|users| users.insert(user, UserData::new(nick, user_btc_addres)));
}

#[ic_cdk::query]
fn get_users() -> HashMap<Principal, ResponseUserData> {
    ic_cdk::println!("logmtlk get_users");
    USERS.with_borrow(|users| {
        users.iter().map(|(principal, user_data)| {
            let has_active_timer = check_for_active_timer(principal);
            let response_user_data = user_data.to_response(has_active_timer); // Use the factory method
            (*principal, response_user_data) // Return the Principal and ResponseUserData
        }).collect()
    })
}

#[ic_cdk::query]
fn get_user(user: Principal) -> Option<ResponseUserData> {
    ic_cdk::println!("logmtlk get_user {}", user.to_text());

    USERS.with_borrow(|users| {
        users.get(&user).map(|user_data| {
            user_data.to_response(check_for_active_timer(&user))
        })
    })
}

fn check_for_active_timer(user: &Principal) -> bool {
    if *user == Principal::anonymous() {
        return false;
    }

    BATCH_TIMERS.with_borrow(|batch_timers| {
        batch_timers.contains_key(user)
    })
}

#[ic_cdk::query]
fn get_chat(mut chat_path: [Principal; 2]) -> Option<Vec<String>> {
    ic_cdk::println!("logmtlk get_chat");
    chat_path.sort();    

    ic_cdk::println!("{:?}", chat_path);    
    let result = CHAT.with_borrow(|chats| chats.get(&chat_path).cloned());
    ic_cdk::println!("{:?}", result);
    return result;
}


#[ic_cdk::update]
fn announce_activity() {
    ic_cdk::println!("logmtlk announce_activity");
    let user = caller();
    if user == Principal::anonymous() {
        panic!("Anonymous Principal!")
    }
    reinstantiate_timer(user);
}



#[ic_cdk::update]
fn add_chat_msg(msg: String, user2: Principal) {
    ic_cdk::println!("logmtlk add_chat_msg {} {}", msg, user2.to_text());
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
    let user_data = USERS.with_borrow(|users| users.get(&user).cloned());

    if let Some(user_data) = user_data {
        if let Some(batch_transfer) = user_data.get_batch_transfer() {
            if batch_transfer.of_inactivity {

                let batch_timer_removed = BATCH_TIMERS.with_borrow_mut(|timers| {
                    if let Some(timer_id) = timers.get(&user) {
                        // Clear the timer before removing it
                        ic_cdk_timers::clear_timer(*timer_id);
                        ic_cdk::println!("Rust reinstantiate_timer ->>> Cleared timer for user: {}", user.to_text());
                    }
                    timers.remove(&user).is_some()
                });

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
                }
            } else {
            }
        } else {
        }


    }
}


pub fn btc_get_user_address(recipient_principal: &Principal) -> String {
    USERS.with(|users| {
        let users = users.borrow();

        if let Some(user_data) = users.get(recipient_principal) {
            return user_data.get_btc_address().clone();
        }

        String::new()
    })
}

use hex;


fn format_derivation_path(derivation_path: &Vec<Vec<u8>>) -> Vec<String> {
    derivation_path
        .iter()
        .map(|segment| hex::encode(segment))
        .collect()
}

#[ic_cdk::update]
async fn btc_get_p2pkh_address(
    derivation_path: Vec<Vec<u8>>,
) -> String {
    let formatted_path = format_derivation_path(&derivation_path);
    ic_cdk::println!(
        "logmtlk btc_get_p2pkh_address from Principal: {:?}",
        formatted_path
    );

    basic_bitcoin::get_p2pkh_address(Some(derivation_path)).await
}



#[ic_cdk::update]
async fn btc_send_from_p2pkh(destination_address: String, amount_in_satoshi: u64, derivation_path : Vec<Vec<u8>>) -> String
{
    let request = SendRequest {
        destination_address,
        amount_in_satoshi,
    };

    return basic_bitcoin::send_from_p2pkh(request, Some(derivation_path)).await;
}


#[ic_cdk::update]
async fn btc_get_balance(address: String) -> u64 {
    ic_cdk::println!("logmtlk btc_get_balance {address}");
    return basic_bitcoin::get_balance(address).await;
}

#[ic_cdk::init]
fn init(network: BitcoinNetwork) {
    basic_bitcoin::init(network);
}

ic_cdk::export_candid!();
