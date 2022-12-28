import json, pytest
from hexbytes import HexBytes

from eth_utils.exceptions import (
    ValidationError,
)
from cfx_account import Account
from cfx_account.messages import encode_structured_data, encode_defunct

private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
typed_data = json.load(open("tests/typed-data.json"))
typed_data_without_chainId = json.load(open("tests/typed-data-without-chainid.json"))
message = "Hello World"

# signature from js-conflux-sdk
message_signature = "0xd72ea2020802d6dfce0d49fc1d92a16b43baa58fc152d6f437d852a014e0c5740b3563375b0b844a835be4f1521b4ae2a691048622f70026e0470acc5351043a01"
typed_data_signature = "0xd7fb6dca3b084ae3a9bf1ea3527de7a9bc2bd40e0c38d3faf9da214f1d5637ab2944a8a993dc59365c1e74e18a1589b358e3fb81bd03892d159f221e8ac765c701"

def test_encode_defunct():
    encoded_message = encode_defunct(text=message)
    address = Account.recover_message(encoded_message, signature=HexBytes(message_signature))
    assert address == Account.from_key(private_key).address

def test_encode_structured_data():
    encoded_data = encode_structured_data(typed_data)
    address = Account.recover_message(encoded_data, signature=HexBytes(typed_data_signature))
    assert address == Account.from_key(private_key).address

def test_sign_message():
    encoded_message = encode_defunct(text=message)
    acct = Account.from_key(private_key)
    signed = acct.sign_message(encoded_message)
    address = Account.recover_message(encoded_message, signature=signed.signature)
    assert address == acct.address

def test_sign_structured_data():
    encoded_data = encode_structured_data(typed_data)
    acct = Account.from_key(private_key)
    signed = acct.sign_message(encoded_data)
    address = Account.recover_message(encoded_data, signature=signed.signature)
    assert address == acct.address

def test_sign_structured_data_without_chainId():
    with pytest.raises(ValidationError):
        encode_structured_data(typed_data_without_chainId)
