from typing import Any, ClassVar, Dict, Tuple

import rlp
from eth_account._utils.transaction_utils import transaction_rpc_to_rlp_structure
from eth_rlp import HashableRLP
from eth_utils import keccak
from eth_utils.curried import apply_formatters_to_dict
from hexbytes import HexBytes
from rlp.sedes import Binary, big_endian_int, binary
from toolz import dissoc, merge, partial, pipe
from typing_extensions import Self

from cfx_account.transactions.base import TransactionImplementation
from cfx_account.transactions.transaction_utils import access_list_sede_type

from .transaction_utils import TYPED_TRANSACTION_FORMATTERS


class CIP1559Transaction(TransactionImplementation):

    transaction_type: ClassVar[int] = 2

    unsigned_transaction_fields = (
        ("nonce", big_endian_int),
        ("maxPriorityFeePerGas", big_endian_int),
        ("maxFeePerGas", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("storageLimit", big_endian_int),
        ("epochHeight", big_endian_int),
        ("chainId", big_endian_int),
        ("data", binary),
        ("accessList", access_list_sede_type),
    )

    signature_fields = (
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    )

    transaction_field_defaults = {
        # "type": b"0x2",
        "chainId": 0,
        "to": b"",
        "value": 0,
        "data": b"",
        "accessList": [],
    }

    _unsigned_transaction_serializer = type(
        "_unsigned_transaction_serializer",
        (HashableRLP,),
        {
            "fields": unsigned_transaction_fields,
        },
    )

    signed_fields = (
        ("tx_meta", _unsigned_transaction_serializer),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    )

    _signed_transaction_serializer = type(
        "_signed_transaction_serializer",
        (HashableRLP,),
        {"fields": signed_fields},
    )

    # Noting that the transaction validity is not checked here
    def __init__(self, transaction_dict: Dict[str, Any]):
        if "type" in transaction_dict:
            transaction_dict.pop("type")
        self.__class__.ensure_no_fields_missing(transaction_dict)
        self.__class__.ensure_no_fields_extra(transaction_dict)

        sanitized_dictionary = pipe(
            transaction_dict,
            dict,
            partial(merge, self.__class__.transaction_field_defaults),
            apply_formatters_to_dict(TYPED_TRANSACTION_FORMATTERS),
        )

        self._dictionary = sanitized_dictionary

    def hash(self) -> bytes:
        """
        Noting: this is not the transaction hash
        Hashes this DynamicFeeTransaction to prepare it for signing.
        As per the CIP-1559 specifications, the signature is a secp256k1 signature over
        ``keccak256(b'cfx' || 0x02 || rlp([nonce, maxPriorityFeePerGas,
        maxFeePerGas, gas, to, value, data, storageLimit, epochHeight, accessList]))``
        """
        return keccak(self._encode_unsigned())

    def as_dict(self) -> Dict[str, Any]:
        return self._dictionary

    def vrs(self) -> Tuple[int, int, int]:
        """Returns (v, r, s) if they exist."""
        if not self.is_signed():
            raise ValueError("attempting to encode an unsigned transaction")
        return (self._dictionary["v"], self._dictionary["r"], self._dictionary["s"])

    def is_signed(self) -> bool:
        return "v" in self._dictionary

    def append_signature(self, *, v: int, r: int, s: int) -> Self:
        if self.is_signed():
            raise ValueError("attempting to sign a signed transaction")
        self._dictionary.update({"v": v, "r": r, "s": s})
        return self
    
    def _encode_unsigned(self) -> bytes:
        transaction_without_signature_fields = dissoc(self._dictionary, "v", "r", "s")
        rlp_structured_txn_without_sig_fields = transaction_rpc_to_rlp_structure(
            transaction_without_signature_fields
        )
        rlp_serializer = self.__class__._unsigned_transaction_serializer
        return pipe(
            rlp_serializer.from_dict(rlp_structured_txn_without_sig_fields),  # type: ignore  # noqa: E501
            lambda val: rlp.encode(val),  # type: ignore
            # (b'cfx' || 0x02 || rlp([...]))
            lambda val: HexBytes(b"cfx") + HexBytes("0x02") + HexBytes(val),  # type: ignore
        )

    def encode(self, *, allow_unsigned: bool = False) -> bytes:
        """
        Returns this raw transaction as bytes.

        The raw transaction is
            b'cfx' || 0x02 || TransactionPayload

        The transaction payload is:

            TransactionPayload = rlp([ nonce, maxPriorityFeePerGas,
            maxFeePerGas, gasLimit, to, value, storageLimit, epochHeight
            data, accessList, signatureYParity, signatureR, signatureS])
        """
        if not self.is_signed():
            if not allow_unsigned:
                raise ValueError("attempting to encode an unsigned transaction without allow_unsigned=True")
            return self._encode_unsigned()
        rlp_serializer = self.__class__._signed_transaction_serializer
        rlp_structured_dict = transaction_rpc_to_rlp_structure(self._dictionary)
        tx_meta = dissoc(rlp_structured_dict, "v", "r", "s")
        payload = rlp.encode(
            rlp_serializer(
                tx_meta=self._unsigned_transaction_serializer(**tx_meta),
                v=self._dictionary["v"],
                r=self._dictionary["r"],
                s=self._dictionary["s"],
            )
        )
        return HexBytes(b"cfx") + HexBytes("0x02") + payload

    @classmethod
    def ensure_no_fields_missing(cls, dictionary: Dict[str, Any]):
        # add default fields
        for fields in cls.transaction_field_defaults:
            if fields not in dictionary:
                dictionary[fields] = cls.transaction_field_defaults[fields]
        # check unsigned fields
        for field, _ in cls.unsigned_transaction_fields:
            if field not in dictionary:
                raise ValueError(f"{field} is missing in {dictionary}")
        # if this is a dictionary with signed fields
        if "v" in dictionary or "r" in dictionary or "s" in dictionary:
            for field, _ in cls.signature_fields:
                if field not in dictionary:
                    raise ValueError(f"{field} is missing in {dictionary}")

    @classmethod
    def ensure_no_fields_extra(cls, dictionary: Dict[str, Any]):
        expected_fields = [
            field
            for field, _ in (cls.unsigned_transaction_fields + cls.signature_fields)
        ]
        for field in dictionary:
            if field not in expected_fields:
                raise ValueError(
                    f"{field} is not a valid field: expecting fields - {expected_fields}"
                )
