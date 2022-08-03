from eth_account.signers.local import LocalAccount as EthLocalAccount
from cfx_address.utils import eth_address_to_cfx
from cfx_address import Address

class LocalAccount(EthLocalAccount):
    def __init__(self, key, account, chain_id=None):
        self._chain_id = chain_id
        super().__init__(key, account)

    @property
    def address(self):
        hex40_addr = eth_address_to_cfx(super().address)
        if not self._chain_id:
            return hex40_addr
        return Address.encode_hex_address(hex40_addr, self._chain_id)
    
    def get_base32_address(self, specific_chain_id=None):
        if not specific_chain_id:
            return self.address
        hex40_addr = eth_address_to_cfx(super().address)
        return Address.encode_hex_address(hex40_addr, specific_chain_id)