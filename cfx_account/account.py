from eth_account.account import Account as EthAccount
from cfx_account.signers.local import LocalAccount
from eth_utils.curried import (
    combomethod,
    keccak,
)
from collections.abc import (
    Mapping,
)
from cytoolz import (
    dissoc,
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
from cfx_address.utils import eth_address_to_cfx
from cfx_address.address import Address

class Account(EthAccount):

    @combomethod
    def from_key(self, private_key):
        r"""
        Returns a convenient object for working with the given private key.

        :param private_key: The raw private key
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :return: object with methods for signing and encrypting
        :rtype: LocalAccount

        .. doctest:: python

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
        return LocalAccount(key, self)

    @combomethod
    def sign_transaction(self, transaction_dict, private_key):
        """
        Sign a transaction using a local private key. Produces signature details
        and the hex-encoded transaction suitable for broadcast using
        :meth:`w3.eth.sendRawTransaction() <web3.eth.Eth.sendRawTransaction>`.

        Create the transaction dict for a contract method with
        `my_contract.functions.my_function().buildTransaction()
        <http://web3py.readthedocs.io/en/latest/contracts.html#methods>`_

        :param dict transaction_dict: the transaction with keys:
          nonce, chainId, to, data, value, gas, and gasPrice.
        :param private_key: the private key to sign the data with
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: AttributeDict

        .. code-block:: python

            >>> transaction = {
                    # Note that the address must be in checksum format or native bytes:
                    'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                    'value': 1000000000,
                    'gas': 2000000,
                    'gasPrice': 234567897654321,
                    'nonce': 0,
                    'chainId': 1
                }
            >>> key = '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
            >>> signed = Account.sign_transaction(transaction, key)
            {'hash': HexBytes('0x6893a6ee8df79b0f5d64a180cd1ef35d030f3e296a5361cf04d02ce720d32ec5'),
             'r': 4487286261793418179817841024889747115779324305375823110249149479905075174044,
             'rawTransaction': HexBytes('0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'),  # noqa: E501
             's': 30785525769477805655994251009256770582792548537338581640010273753578382951464,
             'v': 37}
            >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        """
        if not isinstance(transaction_dict, Mapping):
            raise TypeError("transaction_dict must be dict-like, got %r" % transaction_dict)

        account = self.from_key(private_key)

        # allow from field, *only* if it matches the private key
        if 'from' in transaction_dict:
            if Address.normalize_hex_address(transaction_dict['from']) == account.address:
                sanitized_transaction = dissoc(transaction_dict, 'from')
            else:
                raise TypeError("from field must match key's %s, but it was %s" % (
                    account.address,
                    transaction_dict['from'],
                ))
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            rlp_encoded,
        ) = sign_transaction_dict(account._key_obj, sanitized_transaction)

        transaction_hash = keccak(rlp_encoded)

        return SignedTransaction(
            rawTransaction=HexBytes(rlp_encoded),
            hash=HexBytes(transaction_hash),
            r=r,
            s=s,
            v=v,
        )

    @combomethod
    def recover_transaction(self, serialized_transaction):
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
        recovered_address = self._recover_hash(txn[0].hash(), vrs=vrs_from(txn))
        return eth_address_to_cfx(recovered_address)