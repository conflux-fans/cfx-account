class AddressNotMatch(ValueError):
    pass

class HexAddressNotMatch(AddressNotMatch):
    pass

class Base32AddressNotMatch(AddressNotMatch):
    pass
