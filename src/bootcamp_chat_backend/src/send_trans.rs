use bitcoin::blockdata::transaction::{TxIn, TxOut, OutPoint};
use bitcoin::blockdata::script::Builder;
use bitcoin::network::constants::Network;
use bitcoin::util::address::Address;
use bitcoin::util::key::PrivateKey;
use bitcoin::secp256k1::Secp256k1;
use bitcoin::blockdata::transaction::Transaction;
use bitcoin::hash_types::Txid;
use bitcoin::hashes::hex::FromHex;
use std::str::FromStr;

fn main() {
    let secp = Secp256k1::new();

    // Replace these with your own values
    let private_key = PrivateKey::from_wif("your-private-key").unwrap();
    let source_address = Address::from_str("source-address").unwrap();
    let target_address = Address::from_str("target-address").unwrap();
    let amount = 10000; // Amount to send in satoshis

    let public_key = private_key.public_key(&secp);
    assert_eq!(source_address.script_pubkey(), Builder::build_p2pkh(&public_key.key));

    // Create a fake transaction id for the input
    let txid = Txid::from_hex("0000000000000000000000000000000000000000000000000000000000000000").unwrap();
    let vout = 0;

    // Create the input
    let input = TxIn {
        previous_output: OutPoint { txid, vout },
        script_sig: Builder::build_p2pkh(&public_key.key).into(),
        sequence: 0xFFFFFFFF,
        witness: vec![],
    };

    // Create the output
    let output = TxOut {
        script_pubkey: target_address.script_pubkey(),
        value: amount,
    };

    // Create the transaction
    let transaction = Transaction {
        version: 1,
        lock_time: 0,
        input: vec![input],
        output: vec![output],
    };

    // Sign the transaction
    let sighash = transaction.signature_hash(0, &source_address.script_pubkey(), bitcoin::blockdata::transaction::SigHashType::All);
    let sig = secp.sign(&sighash.into(), &private_key.key);
    transaction.input[0].witness.push(sig.serialize_der().to_vec());
    transaction.input[0].witness[0].push(01); // append SIGHASH_ALL
    transaction.input[0].witness.push(public_key.key.serialize().to_vec());

    // Serialize the transaction into raw format
    let raw_transaction = bitcoin::consensus::encode::serialize(&transaction);

    println!("{:?}", raw_transaction);
}