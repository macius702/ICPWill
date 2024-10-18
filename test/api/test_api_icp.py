import pytest
import subprocess
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ICP_WILL_BACKEND = 'icp_will_backend'

@pytest.fixture(scope="function")
def setup_principals():
    principals = [
        create_internet_identity('A1', with_icp_feed=True),
        create_internet_identity('Alice', already_exists=True),
        create_internet_identity('B2'),
        create_internet_identity('C3')
    ]

    # Yield the principals so the test can use them
    yield principals

    # Teardown: remove the identities after the test
    for principal in principals:
        if not principal.keep_me_after_finish:
            remove_internet_identity(principal.name)

def create_internet_identity(name, with_icp_feed=False, already_exists=False):
    # Create the identity
    if not already_exists:
        subprocess.run(["dfx", "identity", "new", name, "--storage-mode=plaintext"], check=True)

    
    # Get the principal
    principal = subprocess.check_output(["dfx", "identity", "--identity", name, "get-principal"], text=True).strip()
    
    # Feed ICP if needed
    if with_icp_feed:
        subprocess.run(["./feed_local.sh", principal], check=True)

    return Principal(name, principal, already_exists)

def remove_internet_identity(name):
    subprocess.run(["dfx", "identity", "remove", name], check=True)

def test_send(setup_principals):
    principals = setup_principals

    # Read balances
    for p in principals:
        logger.info(f"Balance for {p.name}: {p.get_balance()}")
        logger.info(f"Balance2 for {p.name}: {p.get_balance_of_ledger()}")


    assert True

class Principal:
    def __init__(self, name, principal_str, keep_me_after_finish):
        self.name = name
        self.principal = principal_str
        self.keep_me_after_finish = keep_me_after_finish

    def get_balance(self):
        get_balance_returned = subprocess.check_output(
            ["dfx", "canister", "--identity", self.name , "call", ICP_WILL_BACKEND, "get_balance"],
            text=True
        ).strip()
        return get_balance_returned

    def get_balance_of_ledger(self):
        # Construct the Account record in Candid format
        account_candid = f"record {{ owner = principal \"{self.principal}\"; subaccount = null }}"

        get_balance_returned = subprocess.check_output(
            ["dfx", "canister", "call", "mxzaz-hqaaa-aaaar-qaada-cai", "icrc1_balance_of", f"({account_candid})"],
            text=True
        ).strip()

        return get_balance_returned