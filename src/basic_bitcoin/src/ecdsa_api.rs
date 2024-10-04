use ic_cdk::api::management_canister::ecdsa::{
    ecdsa_public_key, sign_with_ecdsa, EcdsaCurve, EcdsaKeyId, EcdsaPublicKeyArgument,
    SignWithEcdsaArgument,
};

/// Returns the ECDSA public key of this canister at the given derivation path.
pub async fn get_ecdsa_public_key(key_name: String, derivation_path: Vec<Vec<u8>>) -> Vec<u8> {
    // Retrieve the public key of this canister at the given derivation path
    // from the ECDSA API.
    ic_cdk::println!("Entering get_ecdsa_public_key");

    // Print the input parameters
    ic_cdk::println!("key_name: {:?}", key_name);
    ic_cdk::println!("derivation_path: {:?}", derivation_path);    

    let canister_id = None;
    let key_id = EcdsaKeyId {
        curve: EcdsaCurve::Secp256k1,
        name: key_name,
    };

    // Print the key_id and canister_id
    ic_cdk::println!("key_id: {:?}", key_id);
    ic_cdk::println!("canister_id: {:?}", canister_id);

    let res = ecdsa_public_key(EcdsaPublicKeyArgument {
        canister_id,
        derivation_path,
        key_id,
    })
    .await;

    // Print the result
    ic_cdk::println!("ECDSA Public Key Result: {:?}", res);    

    res.unwrap().0.public_key
}

pub async fn get_ecdsa_signature(
    key_name: String,
    derivation_path: Vec<Vec<u8>>,
    message_hash: Vec<u8>,
) -> Vec<u8> {
    let key_id = EcdsaKeyId {
        curve: EcdsaCurve::Secp256k1,
        name: key_name,
    };

    let res = sign_with_ecdsa(SignWithEcdsaArgument {
        message_hash,
        derivation_path,
        key_id,
    })
    .await;

    res.unwrap().0.signature
}
