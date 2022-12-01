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

from eth_account._utils.structured_data.hashing import (
    hash_message as hash_eip712_message,
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
    Encode an EIP-712_ message.

    EIP-712 is the "structured data" approach (ie~ version 1 of an EIP-191 message).

    Supply the message as exactly one of the three arguments:

        - primitive, as a dict that defines the structured data
        - primitive, as bytes
        - text, as a json-encoded string
        - hexstr, as a hex-encoded (json-encoded) string

    .. WARNING:: Note that this code has not gone through an external audit, and
        the test cases are incomplete.
        Also, watch for updates to the format, as the EIP is still in DRAFT.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int or Mapping (eg~ dict )
    :param hexstr: the message encoded as hex
    :param text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The EIP-191 encoded message, ready for signing

    .. _EIP-712: https://eips.ethereum.org/EIPS/eip-712
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
        hash_eip712_message(structured_data),
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
    :returns: The EIP-191 encoded message, ready for signing
    """
    message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
    msg_length = str(len(message_bytes)).encode('utf-8')

    # Encoding version E defined by EIP-191
    return SignableMessage(
        b'C',
        b'onflux Signed Message:\n' + msg_length,
        message_bytes,
    )
