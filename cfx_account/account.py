from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    cast,
    Dict,
    Any,
    Tuple,
    TypeVar,
)
from typing_extensions import Literal
from eth_keys import (
    keys,
)
from eth_keys.datatypes import (
    PrivateKey,
)
from eth_account.hdaccount import (
    key_from_seed,
    seed_from_mnemonic,
)
from eth_account.account import (
    Account as EthAccount,
)
from eth_account.datastructures import (
    SignedMessage,
    SignedTransaction,
)
from eth_account.messages import (
    SignableMessage,
)
from cfx_account.signers.local import LocalAccount
from eth_utils.crypto import (
    keccak,
)
from collections.abc import (
    Mapping,
)
from cytoolz import (
    dissoc,  # type: ignore
)
from hexbytes import (
    HexBytes,
)
from eth_utils.address import to_checksum_address
from eth_account.datastructures import (
    # SignedMessage,
    SignedTransaction,
)
from cfx_account._utils.signing import (
    sign_transaction_dict,
)
from cfx_account.transactions.legacy_transactions import (
    LegacyTransaction,
)
from cfx_address import (
    Base32Address,
    eth_eoa_address_to_cfx_hex,
)
from cfx_address.utils import (
    normalize_to,
)
from cfx_utils.types import (
    TxParam,
    TxDict,
    ChecksumAddress,
    HexStr,
)
from cfx_utils.decorators import (
    combomethod,
)
from cfx_account.types import (
    KeyfileDict,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

CONFLUX_DEFAULT_PATH = "m/44'/503'/0'/0/0"
VRS = TypeVar("VRS", bytes, HexStr, int)


class Account(EthAccount):

    # _default_network_id: Optional[int]=None
    w3: Optional["Web3"] = None

    _use_unaudited_hdwallet_features = True

    @combomethod
    def set_w3(self, w3: "Web3") -> None:
        self.w3 = w3

    # def set_default_network_id(self, network_id: int):
    #     self._default_network_id = network_id

    @combomethod
    def from_key(
        self,
        private_key: Union[bytes, str, PrivateKey],
        network_id: Optional[int] = None,
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
        key = self._parse_private_key(private_key)
        return LocalAccount(
            key,
            self,
            # use network_id is it is not None
            # then use None if self.w3 is not set
            # if self.w3 is set, use self.w3.cfx.chain_id
            network_id or (self.w3 and self.w3.cfx.chain_id),
        )

    @combomethod
    def sign_transaction(
        self, transaction_dict: TxParam, private_key: Union[bytes, str, PrivateKey],
        blobs: Optional[Any] = None,
    ) -> SignedTransaction:
        """
        Sign a transaction using a local private key. Produces signature details
        and the hex-encoded transaction suitable for broadcast using
        :meth:`w3.cfx.send_raw_transaction() <conflux_web3.client.ConfluxClient.send_raw_transaction>`.

        Refer to `Interact with a Contract
        <https://python-conflux-sdk.readthedocs.io/en/latest/examples/10-send_raw_transaction.html#interact-with-a-contract>`_
        to see how to sign for a contract method using `build_transaction`

        :param TxParam transaction_dict: the transaction with keys:
          nonce, chainId, to, data, value, storageLimit, epochHeight, gas, and gasPrice.
        :param Union[bytes,str,PrivateKey] private_key: private_key to be used for signing
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
            'raw_transaction': HexBytes('0xf861dd0101649413d2ba4ed43542e7c54fbb6c5fccb9f269c1f94c016464018080a0a52f639cbed11262a7b88d0a37aef909aa7dc2c36c40689a3d52b8bd1d9482dea054f3bdeb654f73704db4cbc12451fb4c9830ef62b0f24de1a40e4b6fe10f57b2'),  # noqa: E501
            's': 38424933894051759888751352802050752143518665905311311986258635963723328477106,
            'v': 0}
        >>> w3.cfx.sendRawTransaction(signed.raw_transaction)
        """
        if not isinstance(transaction_dict, Mapping):
            raise TypeError(
                "transaction_dict must be dict-like, got %r" % transaction_dict
            )

        account: LocalAccount = self.from_key(private_key)
        transaction_dict = cast(TxDict, transaction_dict)
        # allow from field, *only* if it matches the private key
        if "from" in transaction_dict:
            if normalize_to(transaction_dict["from"], None) == normalize_to(
                account.address, None
            ):
                sanitized_transaction = cast(TxDict, dissoc(transaction_dict, "from"))
            else:
                raise ValueError(
                    "transaction[from] does match key's hex address: "
                    f"from's hex address is {Base32Address(transaction_dict['from']).hex_address}, "
                    f"key's hex address is {account.hex_address}"
                )

        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            raw_transaction,
        ) = sign_transaction_dict(
            account._key_obj, sanitized_transaction
        )  # type: ignore

        transaction_hash = keccak(raw_transaction)

        return SignedTransaction(
            raw_transaction=HexBytes(raw_transaction),
            hash=HexBytes(transaction_hash),
            r=r,
            s=s,
            v=v,
        )

    @combomethod
    def from_mnemonic(
        self,
        mnemonic: str,
        passphrase: str = "",
        account_path: str = CONFLUX_DEFAULT_PATH,
        network_id: Optional[int] = None,
    ) -> LocalAccount:
        """
        Generate an account from a mnemonic.

        :param str mnemonic: space-separated list of BIP39 mnemonic seed words
        :param str passphrase: Optional passphrase used to encrypt the mnemonic, defaults to ""
        :param str account_path: pecify an alternate HD path for deriving the seed using
            BIP32 HD wallet key derivation, defaults to CONFLUX_DEFAULT_PATH(m/44'/503'/0'/0/0)
        :param Optional[int] network_id: the network id of returned account, defaults to None
        :return LocalAccount: a LocalAccount object

        :examples:

        >>> from cfx_account import Account
        >>> acct = Account.from_mnemonic('faint also eye industry survey unhappy boil public lemon myself cube sense', network_id=1)
        >>> acct.address
        'cfxtest:aargrnff46pmuy2g1mmrntctkhr5mzamh6nmg361n0'
        """
        # acct: LocalAccount = super().from_mnemonic(mnemonic, passphrase, account_path)
        seed = seed_from_mnemonic(mnemonic, passphrase)
        private_key = key_from_seed(seed, account_path)
        key = self._parse_private_key(private_key)
        return LocalAccount(key, self, network_id or (self.w3 and self.w3.cfx.chain_id))

    @combomethod
    def create_with_mnemonic(
        self,
        passphrase: str = "",
        num_words: int = 12,
        language: str = "english",
        account_path: str = CONFLUX_DEFAULT_PATH,
        network_id: Optional[int] = None,
    ) -> Tuple[LocalAccount, str]:
        """
        Create mnemonic and derive an account using parameters

        :param str passphrase: Extra passphrase to encrypt the seed phrase, defaults to ""
        :param int num_words: Number of words to use with seed phrase. Default is 12 words.
                              Must be one of [12, 15, 18, 21, 24].
        :param str language: Language to use for BIP39 mnemonic seed phrase, defaults to "english"
        :param str account_path: Specify an alternate HD path for deriving the seed using
            BIP32 HD wallet key derivation, defaults to CONFLUX_DEFAULT_PATH(m/44'/503'/0'/0/0)
        :param Optional[int] network_id: the network id of returned account, defaults to None
        :return Tuple[LocalAccount, str]: a LocalAccount object and related mnemonic
        """
        acct, mnemonic = super().create_with_mnemonic(
            passphrase, num_words, language, account_path
        )
        if network_id is not None:
            acct.network_id = network_id
        return acct, mnemonic

    @classmethod
    def encrypt(  # type: ignore
        cls,
        private_key: Union[bytes, str, PrivateKey],
        password: str,
        kdf: Optional[Literal["scrypt", "pbkdf2"]] = None,
        iterations: Optional[int] = None,
    ) -> KeyfileDict:
        return super().encrypt(private_key, password, kdf, iterations)  # type: ignore

    @staticmethod
    def decrypt(
        keyfile_json: Union[Dict[str, Any], str, KeyfileDict], password: str
    ) -> HexBytes:
        """
        Decrypts a keyfile and returns the secret key.

        :param Union[Dict[str,Any],str,KeyfileDict] keyfile_json: encrypted keyfile
        :param str password: the password that was used to encrypt the key
        :return HexBytes: the hex private key
        """
        return EthAccount.decrypt(keyfile_json, password)

    @combomethod
    def recover_transaction(
        self, serialized_transaction: Union[bytes, HexStr, str]
    ) -> ChecksumAddress:
        """
        Get the address of the account that signed this transaction.

        :param Union[bytes,HexStr,str] serialized_transaction: the complete signed transaction
        :return ChecksumAddress: address of signer, hex-encoded & checksummed

        :example:

        >>> raw_transaction = '0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'  # noqa: E501
        >>> Account.recover_transaction(raw_transaction)
        '0x1c7536e3605d9c16a7a3d7b1898e529396a65c23'
        """
        txn_bytes = HexBytes(serialized_transaction)
        # TODO: replace with Transaction.from_bytes()
        txn = LegacyTransaction.from_bytes(txn_bytes)
        recovered_address = self._recover_hash(txn.hash(), vrs=txn.vrs())  # type: ignore
        return to_checksum_address(eth_eoa_address_to_cfx_hex(recovered_address))

    @combomethod
    def create(
        self, extra_entropy: str = "", network_id: Optional[int] = None
    ) -> LocalAccount:
        """
        Creates a new private key, and returns it as a :class:`~cfx_account.signers.local.LocalAccount`.

        :param str extra_entropy: Add extra randomness to the randomness provided by your OS, defaults to ''
        :param Optional[int] network_id: the network id of the generated account, which determines the address encoding, defaults to None
        :return LocalAccount: an object with private key and convenience methods

        :examples:

        >>> from cfx_account import Account
        >>> acct = Account.create()
        >>> acct.address
        '0x187EE3Cb948fFb5a34417344f7fA01c638aa2F96'
        >>> Account.create(network_id=1029).address
        'cfx:aapapvutg83zauuexwdrgjp4v6xm3dkbm2vevh1rub'
        """
        acct: LocalAccount = super().create(extra_entropy)
        if network_id is not None:
            acct.network_id = network_id
        return acct

    @combomethod
    def sign_message(
        self,
        signable_message: SignableMessage,
        private_key: Union[bytes, HexStr, int, keys.PrivateKey],
    ) -> SignedMessage:
        """
        Sign the provided encoded message. The message is encoded according to CIP-23_

        :param SignableMessage signable_message: an encoded message generated by `encode_defunct` or `encode_structured_data`
        :param Union[bytes,HexStr,int,keys.PrivateKey] private_key: the private key used to sign message
        :return SignedMessage: a signed message object

        :examples:

        >>> from from cfx_account import Account
        >>> from cfx_account.messages import encode_structured_data, encode_defunct
        >>> encoded_message = encode_defunct(text=message)
        >>> acct = Account.create()
        >>> signed = acct.sign_message(encoded_message)
        >>> signed.signature
        '0xd72ea2020802d6dfce0d49fc1d92a16b43baa58fc152d6f437d852a014e0c5740b3563375b0b844a835be4f1521b4ae2a691048622f70026e0470acc5351043a01'
        >>> assert acct.hex_address == Account.recover_message(encoded_message, signature=signed.signature)

        >>> # https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-23.md#typed-data
        >>> typed_data = { "types": { "CIP23Domain": [ ... ] }, ... }
        >>> encoded_data = encode_structured_data(typed_data)
        >>> signed = acct.sign_message(encoded_data)
        >>> signed.signature
        '0xd7fb6dca3b084ae3a9bf1ea3527de7a9bc2bd40e0c38d3faf9da214f1d5637ab2944a8a993dc59365c1e74e18a1589b358e3fb81bd03892d159f221e8ac765c701'
        >>> assert acct.hex_address == Account.recover_message(encoded_data, signature=signed.signature)

        .. _CIP-23: https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-23.md
        """
        return super().sign_message(signable_message, private_key)

    @combomethod
    def recover_message(
        self,
        signable_message: SignableMessage,
        vrs: Optional[Tuple[VRS, VRS, VRS]] = None,
        signature: Optional[bytes] = None,
    ) -> ChecksumAddress:
        """
        Get the address of the account that signed the given message.
        Must specify exactly one of vrs or signature.
        Refer to :meth:`~cfx_account.account.Account.sign_message` for usage examples.

        :param SignableMessage signable_message: an encoded message generated by `encode_defunct` or `encode_structured_data`
        :param Optional[Tuple[VRS,VRS,VRS]] vrs: the three pieces generated by an elliptic curve signature, defaults to None
        :param Optional[bytes] signature: signature bytes concatenated as r+s+v, defaults to None
        :return ChecksumAddress: the checksum address of the account that signed the given message
        """
        recovered_address = super().recover_message(signable_message, vrs, signature)
        return to_checksum_address(eth_eoa_address_to_cfx_hex(recovered_address))
