from typing import Any, Callable, ClassVar, Dict, Tuple, cast

import rlp
from cfx_utils.types import TxParam
from cytoolz import dissoc  # type: ignore
from cytoolz import merge  # type: ignore
from cytoolz import pipe  # type: ignore
from cytoolz import partial
from eth_account._utils.legacy_transactions import TRANSACTION_DEFAULTS
from eth_account._utils.validation import is_int_or_prefixed_hexstr
from eth_rlp import HashableRLP
from eth_utils.curried import apply_formatters_to_dict
from hexbytes import HexBytes
from rlp.sedes import Binary, big_endian_int, binary

from cfx_account._utils.transactions.transaction_utils import (
    LEGACY_TRANSACTION_FORMATTERS,
    is_empty_or_valid_base32_address,
)

from .base import TransactionImplementation  # type: ignore

LEGACY_UNSIGNED_TRANSACTION_FIELDS = (
    ("nonce", big_endian_int),
    ("gasPrice", big_endian_int),
    ("gas", big_endian_int),
    ("to", Binary.fixed_length(20, allow_empty=True)),
    ("value", big_endian_int),
    ("storageLimit", big_endian_int),
    ("epochHeight", big_endian_int),
    ("chainId", big_endian_int),
    ("data", binary),
)


class UnsignedLegacyTransactionImpl(HashableRLP):
    fields = LEGACY_UNSIGNED_TRANSACTION_FIELDS


class LegacyTransactionImpl(HashableRLP):
    fields = (
        ("tx_meta", UnsignedLegacyTransactionImpl),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    )


class LegacyTransaction(TransactionImplementation):

    # ImplType: Type[HashableRLP]
    # impl: HashableRLP

    transaction_type: ClassVar[int] = 0

    def __init__(self, tx_dict: TxParam):
        if "type" in tx_dict:
            tx_dict.pop("type")  # type: ignore

        # signed
        if "v" in tx_dict:
            self.ImplType = LegacyTransactionImpl
            chain_naive_transaction = dissoc(tx_dict, "v", "r", "s")
            self.impl = LegacyTransactionImpl(
                tx_meta=UnsignedLegacyTransactionImpl(**chain_naive_transaction),
                v=tx_dict["v"],
                r=tx_dict["r"],
                s=tx_dict["s"],
            )
            # self.impl = LegacyTransaction(tx_dict)
        else:
            # Unsigned
            self.ImplType = UnsignedLegacyTransactionImpl
            self.impl = serializable_unsigned_transaction_from_dict(tx_dict)

    def hash(self) -> bytes:
        if self.ImplType is UnsignedLegacyTransactionImpl:
            return self.impl.hash()
        else:
            return self.impl[0].hash() # type: ignore

    def from_dict(self, tx_dict: TxParam) -> "LegacyTransaction":
        return LegacyTransaction(tx_dict)

    def as_dict(self) -> Dict[str, Any]:
        if self.ImplType is UnsignedLegacyTransactionImpl:
            return self.impl.as_dict()  # type: ignore
        else:
            vrs = self.vrs()
            return {
                **self.impl.as_dict()[0].as_dict(),  # type: ignore
                "v": vrs[0],
                "r": vrs[1],
                "s": vrs[2],
            }  # type: ignore

    def append_signature(self, *, v: int, r: int, s: int) -> "LegacyTransaction":
        if self.is_signed():
            raise ValueError("Transaction is already signed")
        else:
            self.ImplType = LegacyTransactionImpl
            self.impl = LegacyTransactionImpl(tx_meta=self.impl, v=v, r=r, s=s)
        return self

    def is_signed(self) -> bool:
        return self.ImplType is LegacyTransactionImpl

    def encode(self) -> bytes:
        if not self.is_signed():
            raise ValueError("Transaction is not signed")
        else:
            return rlp.encode(self.impl)

    def vrs(self) -> Tuple[int, int, int]:
        if self.ImplType is LegacyTransactionImpl:
            return vrs_from(self.impl)
        else:
            raise ValueError("Unsigned transaction does not have vrs")

    @classmethod
    def from_bytes(cls, encoded_transaction: HexBytes) -> "LegacyTransaction":
        impl = cast(
            LegacyTransactionImpl, LegacyTransactionImpl.from_bytes(encoded_transaction)
        )
        return LegacyTransaction(
            {
                **impl[0].as_dict(), # type: ignore
                "v": impl.v,
                "r": impl.r,
                "s": impl.s,
            }
        )


def serializable_unsigned_transaction_from_dict(
    transaction_dict: TxParam,
) -> UnsignedLegacyTransactionImpl:
    assert_valid_fields(transaction_dict)
    filled_transaction = pipe(
        transaction_dict,
        dict,
        partial(merge, TRANSACTION_DEFAULTS),
        apply_formatters_to_dict(LEGACY_TRANSACTION_FORMATTERS),
    )
    serializer = UnsignedLegacyTransactionImpl
    return serializer.from_dict(filled_transaction)


def encode_transaction(
    unsigned_transaction: UnsignedLegacyTransactionImpl, vrs: Tuple[int, int, int]
) -> bytes:
    (v, r, s) = vrs
    chain_naive_transaction = dissoc(unsigned_transaction.as_dict(), "v", "r", "s")
    signed_transaction = LegacyTransactionImpl(
        tx_meta=UnsignedLegacyTransactionImpl(**chain_naive_transaction), v=v, r=r, s=s
    )
    return rlp.encode(signed_transaction)  # type: ignore


TRANSACTION_VALID_VALUES: Dict[str, Callable[[Any], bool]] = {
    "nonce": is_int_or_prefixed_hexstr,
    "gasPrice": is_int_or_prefixed_hexstr,
    "gas": is_int_or_prefixed_hexstr,
    "to": is_empty_or_valid_base32_address,
    "value": is_int_or_prefixed_hexstr,
    "storageLimit": is_int_or_prefixed_hexstr,
    "epochHeight": is_int_or_prefixed_hexstr,
    "chainId": is_int_or_prefixed_hexstr,
    "data": lambda val: isinstance(val, (int, str, bytes, bytearray)),  # type: ignore
}

ALLOWED_TRANSACTION_KEYS = {
    "nonce",
    "gasPrice",
    "gas",
    "to",
    "value",
    "storageLimit",
    "epochHeight",
    "chainId",
    "data",
}

REQUIRED_TRANSACITON_KEYS = ALLOWED_TRANSACTION_KEYS.difference(
    TRANSACTION_DEFAULTS.keys()
)


def assert_valid_fields(transaction_dict: Any) -> None:
    # check if any keys are missing
    missing_keys = REQUIRED_TRANSACITON_KEYS.difference(transaction_dict.keys())
    if missing_keys:
        raise TypeError("Transaction must include these fields: %r" % missing_keys)

    # check if any extra keys were specified
    superfluous_keys = set(transaction_dict.keys()).difference(ALLOWED_TRANSACTION_KEYS)
    if superfluous_keys:
        raise TypeError(
            "Transaction must not include unrecognized fields: %r" % superfluous_keys
        )

    # check for valid types in each field
    valid_fields: Dict[str, bool]
    valid_fields = apply_formatters_to_dict(TRANSACTION_VALID_VALUES, transaction_dict)
    if not all(valid_fields.values()):
        invalid = {
            key: transaction_dict[key]
            for key, valid in valid_fields.items()
            if not valid
        }
        raise TypeError("Transaction had invalid fields: %r" % invalid)


def vrs_from(transaction: LegacyTransactionImpl) -> Tuple[int, int, int]:
    return (transaction.v, transaction.r, transaction.s)  # type: ignore
