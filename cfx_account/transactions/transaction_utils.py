from typing import Any, Dict

from cfx_address import Base32Address
from cfx_utils.types import TxDict, TxParam
from eth_account._utils.validation import VALID_EMPTY_ADDRESSES, is_none
from eth_utils.conversions import to_bytes, to_int
from eth_utils.curried import (
    apply_formatter_to_array,
    apply_formatters_to_dict,
    apply_one_of_formatters,
    hexstr_if_str,
)
from eth_utils.types import is_bytes, is_string
from hexbytes import HexBytes
from rlp.sedes import BigEndianInt, Binary, CountableList
from rlp.sedes import List as ListSedesClass
from toolz import assoc, identity, merge


def is_empty_or_valid_base32_address(val: Any) -> bool:
    if val in VALID_EMPTY_ADDRESSES:
        return True
    else:
        return Base32Address.is_valid_base32(val)


LEGACY_TRANSACTION_FORMATTERS = {
    "nonce": hexstr_if_str(to_int),
    "gasPrice": hexstr_if_str(to_int),
    "gas": hexstr_if_str(to_int),
    "to": apply_one_of_formatters(
        (
            (Base32Address.is_valid_base32, lambda val: HexBytes(Base32Address(val).hex_address)),  # type: ignore
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
                            (Base32Address.is_valid_base32, lambda val: HexBytes(Base32Address(val).hex_address)),  # type: ignore
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


# returns a copy of the transaction dict with the 'type' field converted to int
def copy_ensuring_int_transaction_type(transaction_dict: TxParam) -> Dict[str, Any]:
    if "type" not in transaction_dict:
        if "gasPrice" in transaction_dict:
            if "accessList" in transaction_dict:
                # access list txn - type 1
                return assoc(transaction_dict, "type", 1)
            else:
                return assoc(transaction_dict, "type", 0)
        # elif any(
        #     type_2_arg in transaction_dict
        #     for type_2_arg in ("maxFeePerGas", "maxPriorityFeePerGas")
        # ):
        else:
            return assoc(transaction_dict, "type", 2)
    cpy = transaction_dict.copy()
    if isinstance(cpy["type"], str):
        cpy["type"] = int(cpy["type"], 16)
    return cpy
