from typing import (
    Dict,
    Any,
)
import json
from eth_utils import (
    keccak,
)
from eth_account._utils.structured_data.hashing import (
    encode_data
)

from cfx_account._utils.structured_data.validation import (
    validate_structured_data
)

def load_and_validate_structured_message(structured_json_string_data: str) -> Dict[str, Any]:
    structured_data = json.loads(structured_json_string_data)
    validate_structured_data(structured_data)

    return structured_data

def hash_domain(structured_data: Dict[str, Any]) -> bytes:
    return keccak(
        encode_data(
            "CIP23Domain",
            structured_data["types"],
            structured_data["domain"]
        )
    )