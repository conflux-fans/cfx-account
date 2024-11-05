from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from typing_extensions import Self
from cfx_utils.types import TxParam

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
    def encode(self, *, allow_unsigned: bool = False) -> bytes:
        pass
