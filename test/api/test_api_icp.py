import pytest
import subprocess


ICP_WILL_BACKEND = 'icp_will_backend'

@pytest.fixture(scope="function")
def setup_principals():
    return [
        create_internet_identity('A1', with_icp_feed=True),
        create_internet_identity('B2'),
        create_internet_identity('C3')
    ]

def create_internet_identity(name, with_icp_feed=False):

    subprocess.run(["dfx", "identity", "new", name, "--storage-mode=plaintext"], check=True)
    

    principal = subprocess.check_output(["dfx", "identity", "--identity", name, "get-principal"], text=True).strip()
    

    if with_icp_feed:
        subprocess.run(["./feed_local.sh", principal], check=True)

    return Principal(name, principal)

def test_send(setup_principals):
    principals = setup_principals

    # Read balances
    for p in principals:
        print(p.get_balance())

    assert True

class Principal:
    def __init__(self, name, principal_str):
        self.name = name
        self.principal = principal_str

    def get_balance(self):
        get_balance_returned = subprocess.check_output(
            ["dfx", "canister", "call", ICP_WILL_BACKEND, "get_balance"],
            text=True
        ).strip()
        print(get_balance_returned)
        return get_balance_returned
