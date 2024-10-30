from typing import (
    Dict,
    Any,
)

from eth_utils.exceptions import (
    ValidationError,
)
from cfx_account._utils.structured_data.eth_account_legacy_validation import (
    used_header_fields,
    validate_types_attribute,
    validate_primaryType_attribute,
    validate_has_attribute,
    validate_field_declared_only_once_in_struct,
)

def validate_CIP23Domain_schema(structured_data: Dict[str, Any]):
    # Check that the `types` attribute contains `CIP23Domain` schema declaration
    if "CIP23Domain" not in structured_data["types"]:
        raise ValidationError("`CIP23Domain struct` not found in types attribute")
    # Check that the names and types in `CIP23Domain` are what are mentioned in the CIP-23
    # and they are declared only once (if defined at all)
    CIP23Domain_data = structured_data["types"]["CIP23Domain"]
    header_fields = used_header_fields(CIP23Domain_data)
    # CIP-23 requires `chainId` field
    if "chainId" not in header_fields:
        raise ValidationError(f"Field 'chainId' must be defined in {structured_data}")
    for field in header_fields:
        validate_field_declared_only_once_in_struct(field, CIP23Domain_data, "CIP23Domain")


def validate_structured_data(structured_data: Dict[str, Any]):
    # validate the `types` attribute
    validate_types_attribute(structured_data)
    # validate the `CIP23Domain` struct of `types` attribute
    validate_CIP23Domain_schema(structured_data)
    # validate the `primaryType` attribute
    validate_primaryType_attribute(structured_data)
    # Check that there is a `domain` attribute in the structured data
    validate_has_attribute("domain", structured_data)
    # Check that there is a `message` attribute in the structured data
    validate_has_attribute("message", structured_data)
