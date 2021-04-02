from cfx_account.account import Account
from cfx_address.address import Address
from hexbytes import (
    HexBytes,
)

key = '0xcc7939276283a32f60d2fad7d16cac972300308fe99ec98d0e63765d02e24863'
address = '0x1b981f81568edd843dcb5b407ff0dd2e25618622'
base32_address = Address.encode_hex_address(address, 1)
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
    # data: '0x',
    'gas': 100,
    'gasPrice': 1,
    'storageLimit': 100,
    'epochHeight': 100,
    'chainId': 1
}

def test_sign_and_recover():
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

def test_account():
    # account = Account.create()
    account = Account.from_key('0x1d7390934e46ffa0e7d6216841b58fa0c3624f3e19925508fbb55eec9a93f37f')
    # print(account.key.hex())
    print(account.address)