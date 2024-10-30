# changelog

## 1.1.0

* feat: enable dynamic fee transaction signing
* deps: loosen eth-account dependency to < 0.13.0 (corresponding to web3.py 6.x)
* chore: deprecate python3.7 add python 3.12 and 3.13 support

## 1.0.4

* fix: restrict `eth-account` version

## 1.0.3

* fix: `encode_structured_data` not checking `chainId` existence in `CIP23Domain`

## 1.0.2

* fix: wrong testcase for `encode_structured_data`
* doc: add and improve docstrings of cfx_account.account and cfx_account.signers.local

## 1.0.1

* fix: wrong object class returned by from_mnemonic
* feat: support `create_with_mnemonic`
* feat: `create` support `network_id` parameter

## 1.0.0

* stable release

## 0.1.0-beta.12

* feature: add type hints to `LocalAccount` methods

## 0.1.0-beta.11

* feature: support CIP-23
* feature: support mnemonics, and use `m/44'/503'/0'/0/0` as default derive path
* feature: support keystore encryption and decryption

## 0.1.0-beta.10

* loosen eth-* dependency version

## 0.1.0-beta.9

* compatibility fix to use as EthAccount
  * LocalAccount(...).address is now in checksum format
  * fix `recover_transaction` return address format to checksum format 
  * fix transaction signing address check

## 0.1.0-beta.8

* support python 3.7

## 0.1.0-beta.7

* pylance support and integration
* bumpversion:
  * cfx_utils to 1.0.0b12
  * cfx_address to 1.0.0b14
