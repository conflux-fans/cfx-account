from cfx_address import Base32Address
from cfx_account._utils.transactions.cip1559_transactions import CIP1559Transaction
from hexbytes import HexBytes

cip1559_transaction_dict = {
    "type": 2,
    "nonce": 100,
    "maxPriorityFeePerGas": 100,
    "maxFeePerGas": 100,
    "gas": 100,
    "to": "0x19578CF3c71eaB48cF810c78B5175d5c9E6Ef441",
    "value": 100,
    "data": "Hello, World".encode('utf-8'),
    "storageLimit": 100,
    "epochHeight": 100,
    "chainId": 100,
    "accessList": [
        {
            "address": "0x19578CF3c71eaB48cF810c78B5175d5c9E6Ef441",
            "storageKeys": [
                "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            ],
        }
    ],
    "r": 1,
    "s": 1,
    "v": 0,
    # "hash_without_sig": "0x3da56dbe2b76c41135c2429f3035cd79b1abb68902cf588075c30d4912e71cf3",
    # "raw": "63667802f869f864646464649419578cf3c71eab48cf810c78b5175d5c9e6ef441646464648c48656c6c6f2c20576f726c64f838f79419578cf3c71eab48cf810c78b5175d5c9e6ef441e1a01234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef800101",
}


def test_cip1559_transaction_hashing_and_encoding():
    cip1559_transaction = CIP1559Transaction(cip1559_transaction_dict)
    assert (
        cip1559_transaction.hash().hex()
        == "3da56dbe2b76c41135c2429f3035cd79b1abb68902cf588075c30d4912e71cf3"
    )
    assert cip1559_transaction.encode().hex() == "63667802f869f864646464649419578cf3c71eab48cf810c78b5175d5c9e6ef441646464648c48656c6c6f2c20576f726c64f838f79419578cf3c71eab48cf810c78b5175d5c9e6ef441e1a01234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef800101"