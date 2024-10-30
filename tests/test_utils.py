from hexbytes import HexBytes

def assert_hex_equal(a, b):
    assert HexBytes(a) == HexBytes(b), f"{HexBytes(a).hex()} != {HexBytes(b).hex()}"
