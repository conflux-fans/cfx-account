from cfx_account import Account

mnemonic = 'faint also eye industry survey unhappy boil public lemon myself cube sense'
private_key_0 = "0x40d0f137665463584cc57fce2b761572a85d1cbf1601fc93d001c129b2a11c92"

def test_generate_from_mnemonic():
    acct = Account.from_mnemonic(mnemonic, network_id=1)
    assert acct.key.hex() == private_key_0
    assert acct.address == 'cfxtest:aargrnff46pmuy2g1mmrntctkhr5mzamh6nmg361n0'
    
def test_account_restore():
    a1, mnemonic = Account.create_with_mnemonic(num_words=24, passphrase="TESTING", network_id=1)
    a2 = Account.from_mnemonic(mnemonic, passphrase="TESTING")
    assert a1.address.hex_address == a2.address # type: ignore
    
