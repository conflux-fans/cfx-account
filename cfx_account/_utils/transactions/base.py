from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from typing_extensions import Self
from cfx_utils.types import TxParam
from toolz import (
    assoc,
)

class TransactionImplementation(ABC):
    """
    Abstract class that every type of transaction must implement.
    Should not be imported or used by clients of the library.
    """
    
    transaction_type: int

    # blob_data: Optional[BlobPooledTransactionData] = None
    
    @abstractmethod
    def __init__(self, transaction_dict: TxParam):
        ...

    @abstractmethod
    def hash(self) -> bytes:
        pass

    @abstractmethod
    def payload(self) -> bytes:
        pass

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def vrs(self) -> Tuple[int, int, int]:
        pass
    
    @abstractmethod
    def is_signed(self) -> bool:
        pass
    
    @abstractmethod
    def append_signature(self, *, v: int, r: int, s: int) -> Self:
        pass
    
    @abstractmethod
    def encode(self) -> bytes:
        pass

# returns a copy of the transaction dict with the 'type' field converted to int
def copy_ensuring_int_transaction_type(transaction_dict: Dict[str, Any]) -> Dict[str, Any]:
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

