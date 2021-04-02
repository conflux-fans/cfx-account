from eth_account.signers.local import LocalAccount as EthLocalAccount
from cfx_address.utils import eth_address_to_cfx

class LocalAccount(EthLocalAccount):

    @property
    def address(self):
        return eth_address_to_cfx(super().address)