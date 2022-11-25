from cfx_account import Account

mnemonic = 'faint also eye industry survey unhappy boil public lemon myself cube sense'
private_key_0 = "0x40d0f137665463584cc57fce2b761572a85d1cbf1601fc93d001c129b2a11c92"

def test_generate_from_mnemonic():
    acct = Account.from_mnemonic(mnemonic)
    assert acct._private_key.hex() == private_key_0
