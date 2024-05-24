from typing import Type

from cfx_utils.types import TxParam
from hexbytes import HexBytes

from .base import TransactionImplementation
from .cip1559_transactions import CIP1559Transaction
from .legacy_transactions import LegacyTransaction
from .transaction_utils import copy_ensuring_int_transaction_type


class Transaction:
    """
    Represents Conflux Transaction including legacy transaction or typed transactions.
    The currently supported Transaction Types are:

     * type 0: LegacyTransaction
     * type 1: CIP-2930's AccessListTransaction
     * type 2: CIP-1559's DynamicFeeTransaction

    """

    transaction_impl: TransactionImplementation

    # def __init__(self, transaction_type: int, transaction: TransactionImplementation):
    #     """Should not be called directly. Use instead the 'from_dict' method."""
    #     if not isinstance(transaction, TransactionImplementation):
    #         raise TypeError(
    #             f"expected _TransactionImplementation, got {type(transaction)}"
    #         )
    #     if not transaction_type == transaction.transaction_type:
    #         raise ValueError(
    #             f"expected transaction type {repr(transaction_type)}, got {repr(transaction.transaction_type)}"
    #         )
    #     self.transaction = transaction

    # @property
    # def blob_data(self) -> Optional[BlobPooledTransactionData]:
    #     """Returns the blobs associated with this transaction."""
    #     return self.transaction.blob_data

    @classmethod
    def from_dict(
        cls,
        dictionary: TxParam,  # blobs: List[bytes] = None
    ) -> "TransactionImplementation":
        """
        Builds a TypedTransaction from a dictionary.
        Verifies the dictionary is well formed.
        """
        dict_copy = copy_ensuring_int_transaction_type(dictionary)
        # if not is_int_or_prefixed_hexstr(dict_copy["type"]):
        #     raise ValueError("incorrect transaction type")
        # Switch on the transaction type to choose the correct constructor.
        transaction_type: int = dict_copy["type"]
        transaction: Type[TransactionImplementation]
        if transaction_type == LegacyTransaction.transaction_type:
            transaction = LegacyTransaction
        elif transaction_type == CIP1559Transaction.transaction_type:
            transaction = CIP1559Transaction
        # elif transaction_type == AccessListTransaction.transaction_type:
        #     transaction = AccessListTransaction
        # elif transaction_type == BlobTransaction.transaction_type:
        #     transaction = BlobTransaction
        else:
            raise TypeError(f"Unknown Transaction type: {transaction_type}")
        return transaction(dict_copy)

    @classmethod
    def from_bytes(cls, encoded_transaction: HexBytes) -> "TransactionImplementation":
        """Builds a TypedTransaction from a signed encoded transaction."""

        if not isinstance(encoded_transaction, HexBytes):
            raise TypeError(f"expected Hexbytes, got {type(encoded_transaction)}")
        return LegacyTransaction.from_bytes(encoded_transaction)

        # if not (len(encoded_transaction) > 0 and encoded_transaction[0] <= 0x7F):
        #     raise ValueError("unexpected input")

        # transaction: Union[
        #     "DynamicFeeTransaction", "AccessListTransaction", "BlobTransaction"
        # ]

        # if encoded_transaction[0] == AccessListTransaction.transaction_type:
        #     transaction_type = AccessListTransaction.transaction_type
        #     transaction = AccessListTransaction.from_bytes(encoded_transaction)
        # elif encoded_transaction[0] == DynamicFeeTransaction.transaction_type:
        #     transaction_type = DynamicFeeTransaction.transaction_type
        #     transaction = DynamicFeeTransaction.from_bytes(encoded_transaction)
        # elif encoded_transaction[0] == BlobTransaction.transaction_type:
        #     transaction_type = BlobTransaction.transaction_type
        #     transaction = BlobTransaction.from_bytes(encoded_transaction)
        # else:
        #     # The only known transaction types should be explicit if/elif branches.
        #     raise TypeError(
        #         f"typed transaction has unknown type: {encoded_transaction[0]}"
        #     )
        # return cls(
        #     transaction_type=transaction_type,
        #     transaction=transaction,
        # )
        raise NotImplementedError

    # def hash(self) -> bytes:
    #     """
    #     Hashes this transaction to prepare it for signing,
    #     noting this is not the hash of the raw transaction as the signature is not included.
    #     """
    #     return self.unsigned_hash()

    # def unsigned_hash(self):
    #     """
    #     Hashes this transaction to prepare it for signing,
    #     noting this is not the hash of the raw transaction as the signature is not included.
    #     """
    #     return self.transaction.hash()

    # def append_signature(self, *, v: int, r: int, s: int):
    #     self.transaction.append_signature(v=v, r=r, s=s)
    #     return self

    # def encode(self) -> bytes:
    #     """
    #     Encodes this Transaction and returns it as bytes.
    #     Exception will be raised if signature is not attached.

    #     The transaction format follows EIP-2718's typed transaction
    #     format (TransactionType || TransactionPayload).
    #     Note that we delegate to a transaction type's payload() method as
    #     the EIP-2718 does not prescribe a TransactionPayload format,
    #     leaving types free to implement their own encoding.
    #     """
    #     if self.transaction_type != 0:
    #         return bytes([self.transaction_type]) + self.transaction.payload()
    #     return self.transaction.encode()

    # def as_dict(self) -> Dict[str, Any]:
    #     """Returns this transaction as a dictionary."""
    #     # return normalize_transaction_dict(self.transaction.as_dict())
    #     return self.transaction.as_dict()

    # def vrs(self) -> Tuple[int, int, int]:
    #     """Returns (v, r, s) if they exist."""
    #     return self.transaction.vrs()
