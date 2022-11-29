from typing import (
    Union,
)
from typing_extensions import (
    Literal,
    TypedDict,
)

from eth_typing import (
    HexStr
)

class ScryptParams(TypedDict):
    dklen: int
    n: int # 262144 is default factor
    r: int
    p: int
    salt: HexStr

class PBKDF2Params(TypedDict):
    c: int # 1000000 is default factor
    dklen: int
    prf: Literal['hmac-sha256']
    salt: HexStr

class CipherParams(TypedDict):
    iv: HexStr

class CryptoParams(TypedDict):
    cipher: Literal['aes-128-ctr']
    cipherparams: CipherParams
    ciphertext: HexStr
    kdf: Literal["scrypt", "pbkdf2"]
    kdfparams: Union[PBKDF2Params, ScryptParams]
    mac: HexStr

class KeyfileDict(TypedDict):
    address: HexStr
    crypto: CryptoParams
    id: HexStr
    version: Literal[3]
