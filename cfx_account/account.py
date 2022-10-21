from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    cast,
)
from eth_account.account import Account as EthAccount
from cfx_address.utils import (
    validate_network_id
)
from cfx_account.signers.local import (
    LocalAccount
)
from eth_utils.crypto import (
    keccak,
)
from collections.abc import (
    Mapping,
)
from cytoolz import (
    dissoc, # type: ignore
)
from hexbytes import (
    HexBytes,
)
from eth_account.datastructures import (
    # SignedMessage,
    SignedTransaction,
)
from cfx_account._utils.signing import (
    sign_transaction_dict,
)
from cfx_account._utils.transactions import (
    Transaction,
    vrs_from,
)
from cfx_address import (
    Base32Address,
    eth_eoa_address_to_cfx_hex
)
from cfx_utils.types import (
    TxParam,
    TxDict,
    HexAddress,
    HexStr,
)
from cfx_utils.decorators import (
    combomethod,
)
from eth_keys.datatypes import (
    PrivateKey,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class Account(EthAccount):
    
    # _default_network_id: Optional[int]=None
    w3: Optional["Web3"] = None 
    
    @combomethod
    def set_w3(self, w3: "Web3") -> None:
        self.w3 = w3
    
    # def set_default_network_id(self, network_id: int):
    #     self._default_network_id = network_id

    @combomethod
    def from_key(
        self, private_key: Union[bytes, str, PrivateKey], network_id: Optional[int]=None
    ) -> LocalAccount:
        """
        returns a LocalAccount object

        :param str private_key: the raw private key
        :param Optional[int] network_id: target network of the account, defaults to None
        :return LocalAccount: object with methods for signing and encrypting

        >>> acct = Account.from_key(
        ... 0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364)
        >>> acct.address
        '0x1ce9454909639d2d17a3f753ce7d93fa0b9ab12e'
        >>> acct.key
        HexBytes('0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')

        # These methods are also available: sign_message(), sign_transaction(), encrypt()
        # They correspond to the same-named methods in Account.*
        # but without the private key argument
        """
        key = self._parsePrivateKey(private_key)
        if network_id is not None:
            validate_network_id(network_id)
            return LocalAccount(key, self, network_id)
        if self.w3:
            w3_network_id = self.w3.cfx.chain_id
            return LocalAccount(key, self, w3_network_id)
        return LocalAccount(key, self)

    @combomethod
    def sign_transaction(
        self, transaction_dict: TxParam, private_key: Union[bytes, str, PrivateKey]
    ) -> SignedTransaction:
        """
        Sign a transaction using a local private key. Produces signature details
        and the hex-encoded transaction suitable for broadcast using
        :meth:`w3.cfx.sendRawTransaction() <web3.client.Cfx.sendRawTransaction>`.

        Create the transaction dict for a contract method with
        `my_contract.functions.my_function().buildTransaction()
        <http://web3py.readthedocs.io/en/latest/contracts.html#methods>`_

        :param TxParam transaction_dict: the transaction with keys:
          nonce, chainId, to, data, value, storageLimit, epochHeight, gas, and gasPrice.
        :param Union[bytes, str, PrivateKey] private_key: private_key to be used for signing
        :raises TypeError: transaction_dict is not a dict-like object
        :raises ValueError: transaction's from field does not match private_key
        :return SignedTransaction: an attribute dict contains various details about the signature - most
          importantly the fields: v, r, and s
    
        >>> transaction = {
                # Note that the address must be in Base32 format or native bytes:
                'to': 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da',
                'nonce': 1,
                'value': 1,
                'gas': 100,
                'gasPrice': 1,
                'storageLimit': 100,
                'epochHeight': 100,
                'chainId': 1
            }
        >>> key = '0xcc7939276283a32f60d2fad7d16cac972300308fe99ec98d0e63765d02e24863'
        >>> signed = Account.sign_transaction(transaction, key)
        {'hash': HexBytes('0x692a0ea530a264f4e80ce39f393233e90638ef929c8706802e15299fd0b042b9'),
            'r': 74715349327018893060702835194036838027583623083228589573427622179540208747230,
            'rawTransaction': HexBytes('0xf861dd0101649413d2ba4ed43542e7c54fbb6c5fccb9f269c1f94c016464018080a0a52f639cbed11262a7b88d0a37aef909aa7dc2c36c40689a3d52b8bd1d9482dea054f3bdeb654f73704db4cbc12451fb4c9830ef62b0f24de1a40e4b6fe10f57b2'),  # noqa: E501
            's': 38424933894051759888751352802050752143518665905311311986258635963723328477106,
            'v': 0}
        >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        """
        if not isinstance(transaction_dict, Mapping):
            raise TypeError("transaction_dict must be dict-like, got %r" % transaction_dict)

        account: LocalAccount = self.from_key(private_key)
        transaction_dict = cast(TxDict, transaction_dict)
        # allow from field, *only* if it matches the private key
        if 'from' in transaction_dict:
            if Base32Address(transaction_dict['from']).hex_address == account.hex_address:
                sanitized_transaction = cast(TxDict, dissoc(transaction_dict, 'from'))
            else:
                raise ValueError("transaction[from] does match key's hex address: "
                    f"from's hex address is{Base32Address(transaction_dict['from']).hex_address}, "
                    f"key's hex address is {account.hex_address}")
                
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            rlp_encoded,
        ) = sign_transaction_dict(account._key_obj, sanitized_transaction) # type: ignore

        transaction_hash = keccak(rlp_encoded)

        return SignedTransaction(
            rawTransaction=HexBytes(rlp_encoded),
            hash=HexBytes(transaction_hash),
            r=r,
            s=s,
            v=v,
        )

    @combomethod
    def recover_transaction(self, serialized_transaction: Union[bytes, HexStr, str]) -> HexAddress:
        """
        Get the address of the account that signed this transaction.

        :param serialized_transaction: the complete signed transaction
        :type serialized_transaction: hex str, bytes or int
        :returns: address of signer, hex-encoded & checksummed
        :rtype: str

        .. doctest:: python

            >>> raw_transaction = '0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'  # noqa: E501
            >>> Account.recover_transaction(raw_transaction)
            '0x1c7536e3605d9c16a7a3d7b1898e529396a65c23'
        """
        txn_bytes = HexBytes(serialized_transaction)
        txn = Transaction.from_bytes(txn_bytes)
        recovered_address = self._recover_hash(txn[0].hash(), vrs=vrs_from(txn)) # type: ignore
        return eth_eoa_address_to_cfx_hex(recovered_address)

    @combomethod
    def create(self, extra_entropy: str='') -> LocalAccount:
        return super().create(extra_entropy)
