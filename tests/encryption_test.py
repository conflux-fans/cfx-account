from cfx_account import Account
from tests.test_utils import assert_hex_equal

private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
keystore = {
    "version": 3,
    "id": "db029583-f1bd-41cc-aeb5-b2ed5b33227b",
    "address": "1cad0b19bb29d4674531d6f115237e16afce377c",
    "crypto": {
        "ciphertext": "3198706577b0880234ecbb5233012a8ca0495bf2cfa2e45121b4f09434187aba",
        "cipherparams": {"iv": "a9a1f9565fd9831e669e8a9a0ec68818"},
        "cipher": "aes-128-ctr",
        "kdf": "scrypt",
        "kdfparams": {
            "dklen": 32,
            "salt": "3ce2d51bed702f2f31545be66fa73d1467d24686059776430df9508407b74231",
            "n": 8192,
            "r": 8,
            "p": 1,
        },
        "mac": "cf73832f328f3d5d1e0ec7b0f9c220facf951e8bba86c9f26e706d2df1e34890",
    },
}


def test_decrypt():
    assert_hex_equal(Account.decrypt(keystore, "password"), private_key)

def test_encrypt():
    encrypted = Account.encrypt(private_key, "password")
    assert_hex_equal(Account.decrypt(encrypted, "password"), private_key)
