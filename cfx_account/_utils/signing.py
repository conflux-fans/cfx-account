from typing import (
    Tuple,
)
from cfx_utils.types import TxDict
from eth_keys.datatypes import PrivateKey

from cfx_utils.token_unit import (
    to_int_if_drip_units,
)

from .transactions.transactions import (
    Transaction,
)


def sign_transaction_dict(
    eth_key: PrivateKey, transaction_dict: TxDict
) -> Tuple[int, int, int, bytes]:
    if not transaction_dict.get("gasPrice") is None:
        transaction_dict["gasPrice"] = to_int_if_drip_units(transaction_dict["gasPrice"])  # type: ignore
    if not transaction_dict.get("value") is None:
        transaction_dict["value"] = to_int_if_drip_units(transaction_dict["value"])  # type: ignore
    # generate RLP-serializable transaction, with defaults filled
    transaction = Transaction.from_dict(transaction_dict)

    transaction_hash = transaction.hash()

    # sign with private key
    (v, r, s) = sign_transaction_hash(eth_key, transaction_hash)

    # serialize transaction with rlp
    raw_transaction = transaction.append_signature(v=v,r=r,s=s).encode()

    return (v, r, s, raw_transaction)


def sign_transaction_hash(
    key: PrivateKey, transaction_hash: bytes
) -> Tuple[int, int, int]:
    signature = key.sign_msg_hash(transaction_hash)
    return signature.vrs
