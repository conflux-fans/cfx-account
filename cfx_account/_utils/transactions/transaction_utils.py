from cfx_address import Base32Address
from cfx_utils.types import TxDict
from eth_account._utils.validation import VALID_EMPTY_ADDRESSES


from typing import Any


def is_empty_or_valid_base32_address(val: Any) -> bool:
    if val in VALID_EMPTY_ADDRESSES:
        return True
    else:
        return Base32Address.is_valid_base32(val)


def hexstr_if_base32(transaction_dict: TxDict) -> TxDict:
    to = transaction_dict.get("to", None)
    if not (to in VALID_EMPTY_ADDRESSES):
        address = Base32Address(to)  # type: ignore
        transaction_dict["to"] = address.hex_address
    return transaction_dict