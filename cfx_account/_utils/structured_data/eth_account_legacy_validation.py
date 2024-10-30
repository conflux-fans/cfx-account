# The MIT License (MIT)

# Copyright (c) 2019-2023 The Ethereum Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

from eth_utils.exceptions import (
    ValidationError,
)

# Regexes
IDENTIFIER_REGEX = r"^[a-zA-Z_$][a-zA-Z_$0-9]*$"
TYPE_REGEX = r"^[a-zA-Z_$][a-zA-Z_$0-9]*(\[([1-9]\d*\b)*\])*$"


def validate_has_attribute(attr_name, dict_data):
    if attr_name not in dict_data:
        raise ValidationError(f"Attribute `{attr_name}` not found in the JSON string")


def validate_types_attribute(structured_data):
    # Check that the data has `types` attribute
    validate_has_attribute("types", structured_data)

    # Check if all the `name` and the `type` attributes in each field of all the
    # `types` attribute are valid (Regex Check)
    for struct_name in structured_data["types"]:
        # Check that `struct_name` is of the type string
        if not isinstance(struct_name, str):
            raise ValidationError(
                "Struct Name of `types` attribute should be a string, "
                f"but got type `{type(struct_name)}`"
            )
        for field in structured_data["types"][struct_name]:
            # Check that `field["name"]` is of the type string
            if not isinstance(field["name"], str):
                raise ValidationError(
                    f"Field Name `{field['name']}` of struct `{struct_name}` "
                    f"should be a string, but got type `{type(field['name'])}`"
                )
            # Check that `field["type"]` is of the type string
            if not isinstance(field["type"], str):
                raise ValidationError(
                    f"Field Type `{field['type']}` of struct `{struct_name}` "
                    f"should be a string, but got type `{type(field['name'])}`"
                )
            # Check that field["name"] matches with IDENTIFIER_REGEX
            if not re.match(IDENTIFIER_REGEX, field["name"]):
                raise ValidationError(
                    f"Invalid Identifier `{field['name']}` in `{struct_name}`"
                )
            # Check that field["type"] matches with TYPE_REGEX
            if not re.match(TYPE_REGEX, field["type"]):
                raise ValidationError(
                    f"Invalid Type `{field['type']}` in `{struct_name}`"
                )


def validate_field_declared_only_once_in_struct(field_name, struct_data, struct_name):
    if len([field for field in struct_data if field["name"] == field_name]) != 1:
        raise ValidationError(
            f"Attribute `{field_name}` not declared or declared more "
            f"than once in {struct_name}"
        )


EIP712_DOMAIN_FIELDS = [
    "name",
    "version",
    "chainId",
    "verifyingContract",
]


def used_header_fields(EIP712Domain_data):
    return [
        field["name"]
        for field in EIP712Domain_data
        if field["name"] in EIP712_DOMAIN_FIELDS
    ]


def validate_EIP712Domain_schema(structured_data):
    # Check that the `types` attribute contains `EIP712Domain` schema declaration
    if "EIP712Domain" not in structured_data["types"]:
        raise ValidationError("`EIP712Domain struct` not found in types attribute")
    # Check that the names and types in `EIP712Domain` are what are mentioned in the
    #  EIP-712 and they are declared only once (if defined at all)
    EIP712Domain_data = structured_data["types"]["EIP712Domain"]
    header_fields = used_header_fields(EIP712Domain_data)
    if len(header_fields) == 0:
        raise ValidationError(
            f"One of {EIP712_DOMAIN_FIELDS} must be defined in {structured_data}"
        )
    for field in header_fields:
        validate_field_declared_only_once_in_struct(
            field, EIP712Domain_data, "EIP712Domain"
        )


def validate_primaryType_attribute(structured_data):
    # Check that `primaryType` attribute is present
    if "primaryType" not in structured_data:
        raise ValidationError(
            "The Structured Data needs to have a `primaryType` attribute"
        )
    # Check that `primaryType` value is a string
    if not isinstance(structured_data["primaryType"], str):
        raise ValidationError(
            "Value of attribute `primaryType` should be `string`, "
            f"but got type `{type(structured_data['primaryType'])}`"
        )
    # Check that the value of `primaryType` is present in the `types` attribute
    if not structured_data["primaryType"] in structured_data["types"]:
        raise ValidationError(
            f"The Primary Type `{structured_data['primaryType']}` is not "
            "present in the `types` attribute"
        )

