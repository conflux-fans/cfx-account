# changelog

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
