import pytest
from cfx_account.account import (
    Account
)
from cfx_utils.exceptions import (
    InvalidNetworkId
)
from cfx_utils.types import (
    Drip,
    CFX
)
from hexbytes import (
    HexBytes,
)
from conflux_web3.dev import get_testnet_web3

key = '0xcc7939276283a32f60d2fad7d16cac972300308fe99ec98d0e63765d02e24863'
address = '0x1b981f81568eDD843DcB5b407ff0DD2e25618622'
base32_address = 'cfxtest:aar3uh6bm4hr5bb73rrya99u5y1cm2pgeja196rfeb'
expected_raw_tx = '0xf861dd0101649413d2ba4ed43542e7c54fbb6c5fccb9f269c1f94c016464018080a0a52f639cbed11262a7b88d0a37aef909aa7dc2c36c40689a3d52b8bd1d9482dea054f3bdeb654f73704db4cbc12451fb4c9830ef62b0f24de1a40e4b6fe10f57b2'
v = 0
r = '0xa52f639cbed11262a7b88d0a37aef909aa7dc2c36c40689a3d52b8bd1d9482de'
s = '0x54f3bdeb654f73704db4cbc12451fb4c9830ef62b0f24de1a40e4b6fe10f57b2'
signed_tx_hash = '0x692a0ea530a264f4e80ce39f393233e90638ef929c8706802e15299fd0b042b9'

transaction = {
    # 'from': '0x1b981f81568edd843dcb5b407ff0dd2e25618622'.lower(),
    'from': base32_address,
    'to': 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da',
    'nonce': 1,
    'value': 1,
    'gas': 100,
    'gasPrice': 1,
    'storageLimit': 100,
    'epochHeight': 100,
    'chainId': 1
}

transaction_value_in_token = {
    # 'from': '0x1b981f81568edd843dcb5b407ff0dd2e25618622'.lower(),
    'from': base32_address,
    'to': 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da',
    'nonce': 1,
    'value': CFX(1)/10**18,
    'gas': 100,
    'gasPrice': Drip(1),
    'storageLimit': 100,
    'epochHeight': 100,
    'chainId': 1
}

def test_sign_and_recover():
    account = Account.from_key(key)
    assert account.address == address
    signed_tx = Account.sign_transaction(transaction, key)
    # signed_tx = account.sign_transaction(transaction)
    assert v == signed_tx.v
    assert r == HexBytes(signed_tx.r).hex()
    assert s == HexBytes(signed_tx.s).hex()
    assert signed_tx_hash == signed_tx.hash.hex()
    assert expected_raw_tx == signed_tx.rawTransaction.hex()
    recovered_address = Account.recover_transaction(expected_raw_tx)
    assert recovered_address == address

def test_sign_and_recover_in_token():
    transaction = transaction_value_in_token
    account = Account.from_key(key)
    assert account.address == address
    signed_tx = Account.sign_transaction(transaction, key)
    assert v == signed_tx.v
    assert r == HexBytes(signed_tx.r).hex()
    assert s == HexBytes(signed_tx.s).hex()
    assert signed_tx_hash == signed_tx.hash.hex()
    assert expected_raw_tx == signed_tx.rawTransaction.hex()
    recovered_address = Account.recover_transaction(expected_raw_tx)
    assert recovered_address == address

def test_local_account():
    assert Account.from_key(key).address == address
    assert Account.from_key(key, network_id=1).address == base32_address
    assert Account.from_key(key, network_id=1).hex_address == address
    assert Account.from_key(key).get_base32_address(1) == base32_address
    
    local_account = Account.from_key(key)
    local_account.network_id = 1
    assert local_account.network_id == 1
    with pytest.raises(InvalidNetworkId):
        local_account.network_id = 0
    assert local_account.address == base32_address
    local_account.network_id = None
    assert local_account.address == address

def test_set_network_id():
    assert Account.create().address.startswith("0x")
    assert Account.create(network_id=1029).network_id == 1029
    w3 = get_testnet_web3()
    Account.set_w3(w3)
    assert Account.create().network_id == 1
    Account.set_w3(None) # type: ignore
