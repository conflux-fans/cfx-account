from collections.abc import (
    Mapping,
)
from typing import (
    Union,
    Optional,
    Any,
    cast,
    Dict,
)

from eth_utils.curried import (
    text_if_str,
    to_bytes,
    to_text,
)
from hexbytes import (
    HexBytes,
)

from cfx_account._utils.structured_data.eth_account_legacy_hashing import (
    hash_cip23_message,
)

from eth_account.messages import (
    SignableMessage
)
from cfx_account._utils.structured_data.hashing import (
    hash_domain,
    load_and_validate_structured_message,
)
from cfx_account._utils.structured_data.validation import (
    validate_structured_data,
)

text_to_bytes = text_if_str(to_bytes)


def encode_structured_data(
    primitive: Optional[Union[bytes, int, Mapping]] = None, # type: ignore
    *,
    hexstr: Optional[str] = None,
    text: Optional[str] = None) -> SignableMessage:
    """
    Encode an CIP-23_ message.

    CIP-23 is the "structured data" approach.

    Supply the message as exactly one of the three arguments:

        - primitive, as a dict that defines the structured data
        - primitive, as bytes
        - text, as a json-encoded string
        - hexstr, as a hex-encoded (json-encoded) string

    :param primitive: the binary message to be signed
    :type primitive: bytes or int or Mapping (eg~ dict )
    :param hexstr: the message encoded as hex
    :param text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The CIP-23 encoded message for typed data, ready for signing

    .. _CIP-23: https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-23.md
    """
    if isinstance(primitive, Mapping):
        validate_structured_data(cast(Dict[str, Any], primitive))
        structured_data = primitive
    else:
        message_string = to_text(primitive, hexstr=hexstr, text=text)
        structured_data = load_and_validate_structured_message(message_string)
    return SignableMessage(
        HexBytes(b'\x01'),
        hash_domain(structured_data), # type: ignore
        hash_cip23_message(structured_data),
    )
    
def encode_defunct(
        primitive: Optional[bytes] = None,
        *,
        hexstr: Optional[str] = None,
        text: Optional[str] = None) -> SignableMessage:
    r"""
    Encode a message for signing, using an old, unrecommended approach.
    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The CIP-23 encoded message for a string, ready for signing
    """
    message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
    msg_length = str(len(message_bytes)).encode('utf-8')

    # Encoding version E is defined by EIP-191 
    # "\x19Ethereum Signed Message:\n" + len(message).
    # There is not a similar definition in CIP-23, so we use C as version to compute, 
    # in which way the computing result is right
    return SignableMessage(
        b'C',
        b'onflux Signed Message:\n' + msg_length,
        message_bytes,
    )
