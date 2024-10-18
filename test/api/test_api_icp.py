import pytest


@pytest.fixture(scope="function")
def setup_principals():
    principals = []



    with open('principals.txt', 'rt') as f:
        principals_read_back = [line.strip() for line in f]
    print(principals_read_back)

    for principal_str in principals_read_back:
        Principal(principal_str)
        principals.append(p)


def test_send(setup_principals):
    principals = setup_principals

    # read_balances
    for p in principals:
        print(p.get_balance())


class Principal:
    def __init__(self, principal_str):
        self.name = principal_str
    def get_balance(self):
        dfx(


