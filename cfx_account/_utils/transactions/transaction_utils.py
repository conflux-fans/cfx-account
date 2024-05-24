from typing import Any

from cfx_address import Base32Address
from cfx_utils.types import TxDict
from eth_account._utils.validation import VALID_EMPTY_ADDRESSES, is_none
from eth_utils.conversions import to_bytes, to_int
from eth_utils.curried import (
    apply_formatter_to_array,
    apply_formatters_to_dict,
    apply_one_of_formatters,
    hexstr_if_str,
)
from eth_utils.types import is_bytes, is_string
from rlp.sedes import BigEndianInt, Binary, CountableList
from rlp.sedes import List as ListSedesClass
from toolz import identity, merge


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


LEGACY_TRANSACTION_FORMATTERS = {
    "nonce": hexstr_if_str(to_int),
    "gasPrice": hexstr_if_str(to_int),
    "gas": hexstr_if_str(to_int),
    "to": apply_one_of_formatters(
        (
            (is_string, hexstr_if_str(to_bytes)),
            (is_bytes, identity),
            (is_none, lambda val: b""),  # type: ignore
        )
    ),
    "value": hexstr_if_str(to_int),
    "storageLimit": hexstr_if_str(to_int),
    "epochHeight": hexstr_if_str(to_int),
    "chainId": hexstr_if_str(to_int),
    "data": hexstr_if_str(to_bytes),
    "v": hexstr_if_str(to_int),
    "r": hexstr_if_str(to_int),
    "s": hexstr_if_str(to_int),
}

TYPED_TRANSACTION_FORMATTERS = merge(
    LEGACY_TRANSACTION_FORMATTERS,
    {
        "chainId": hexstr_if_str(to_int),
        "type": hexstr_if_str(to_int),
        "accessList": apply_formatter_to_array(
            apply_formatters_to_dict(
                {
                    "address": apply_one_of_formatters(
                        (
                            (is_string, hexstr_if_str(to_bytes)),
                            (is_bytes, identity),
                        )
                    ),
                    "storageKeys": apply_formatter_to_array(hexstr_if_str(to_int)),
                }
            ),
        ),
        "maxPriorityFeePerGas": hexstr_if_str(to_int),
        "maxFeePerGas": hexstr_if_str(to_int),
        "maxFeePerBlobGas": hexstr_if_str(to_int),
        "blobVersionedHashes": apply_formatter_to_array(hexstr_if_str(to_bytes)),
    },
)
access_list_sede_type = CountableList(
    ListSedesClass(
        [
            Binary.fixed_length(20, allow_empty=False),
            CountableList(BigEndianInt(32)),
        ]
    ),
)
