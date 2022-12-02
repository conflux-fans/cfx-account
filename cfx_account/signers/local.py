from typing import TYPE_CHECKING, Any, Optional, Union, Type
from typing_extensions import Literal
from eth_utils.address import to_checksum_address
from eth_account.signers.local import LocalAccount as EthLocalAccount
from eth_account.datastructures import (
    SignedMessage,
    SignedTransaction,
)
from eth_account.messages import (
    SignableMessage
)
from cfx_address import (
    eth_eoa_address_to_cfx_hex,
    Base32Address
)
from cfx_address.utils import (
    validate_network_id
)
from cfx_utils.types import (
    TxParam,
    ChecksumAddress,
)
from cfx_account.types import (
    KeyfileDict,
)


if TYPE_CHECKING:
    from cfx_account import Account


class LocalAccount(EthLocalAccount):
    def __init__(self, key: Any, account: Union["Account", Type["Account"]], network_id: Optional[int]=None):
        if network_id is not None:
            validate_network_id(network_id)
        self._network_id = network_id
        
        super().__init__(key, account)

    @property
    def network_id(self) -> Union[int, None]:
        return self._network_id
    
    @network_id.setter
    def network_id(self, new_network_id: Union[int, None]) -> None:
        if new_network_id is not None:
            validate_network_id(new_network_id)
        self._network_id = new_network_id
        
    # def reset_network_id(self):
    #     self._network_id = None

    @property
    def address(self) -> Union[Base32Address, ChecksumAddress]:
        """
        returns the address of the account

        :return Union[Base32Address, ChecksumAddress]: _description_
        """
        hex_address = self.hex_address
        if not self._network_id:
            return hex_address
        return Base32Address(hex_address, self._network_id)

    @property
    def hex_address(self) -> ChecksumAddress:
        return to_checksum_address(eth_eoa_address_to_cfx_hex(super().address))
    
    @property
    def key(self) -> bytes:
        """
        Get the private key.
        """
        return super().key
    
    def get_base32_address(self, specific_network_id: int) -> Base32Address:
        return Base32Address(self.address, specific_network_id)
    
    # add type hint
    def sign_transaction(self, transaction_dict: TxParam) -> SignedTransaction:
        return super().sign_transaction(transaction_dict)
    
    def sign_message(self, signable_message: SignableMessage) -> SignedMessage:
        return super().sign_message(signable_message)
    
    def encrypt(self, password: str, kdf: Optional[Literal['scrypt', 'pbkdf2']]=None, iterations: Optional[int]=None) -> KeyfileDict:
        return super().encrypt(password, kdf, iterations)
    
    def __bytes__(self) -> bytes:
        return self.key
