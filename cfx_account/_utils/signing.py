from typing import (
    Tuple,
)
from cfx_utils.types import (
    TxDict
)
from eth_keys.datatypes import (
    PrivateKey
)

from .transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)

from cfx_utils.token_unit import (
    to_int_if_drip_units,
)
    

def sign_transaction_dict(eth_key: PrivateKey, transaction_dict: TxDict) -> Tuple[int, int, int, bytes]:
    transaction_dict['gasPrice'] = to_int_if_drip_units(transaction_dict['gasPrice']) # type: ignore
    transaction_dict['value'] = to_int_if_drip_units(transaction_dict['value']) # type: ignore
    # generate RLP-serializable transaction, with defaults filled
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)

    transaction_hash = unsigned_transaction.hash()

    # sign with private key
    (v, r, s) = sign_transaction_hash(eth_key, transaction_hash)

    # serialize transaction with rlp
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    return (v, r, s, encoded_transaction)

def sign_transaction_hash(key: PrivateKey, transaction_hash: bytes) -> Tuple[int, int, int]:
    signature = key.sign_msg_hash(transaction_hash)
    return signature.vrs
