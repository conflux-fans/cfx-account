from .transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)

def sign_transaction_dict(eth_key, transaction_dict):
    # generate RLP-serializable transaction, with defaults filled
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)

    transaction_hash = unsigned_transaction.hash()

    # sign with private key
    (v, r, s) = sign_transaction_hash(eth_key, transaction_hash)

    # serialize transaction with rlp
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    return (v, r, s, encoded_transaction)

def sign_transaction_hash(key, transaction_hash):
    signature = key.sign_msg_hash(transaction_hash)
    return signature.vrs