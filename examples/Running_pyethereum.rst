

- poc7 branch of github.com/ethereum/serpent
- develop branch of github.com/ethereum/pyethereum

These can be installed with python setup.py install

- pyethereum test suite has examples that can be patched together to form illustrative examples of contract runs. https://github.com/ethereum/pyethereum/blob/develop/tests/test_contracts.py#L743

debugging can be turned on like: slogging.set_level('eth.tx',"DEBUG")


TODO:
-  the test suite has some simplifying functions, in the "tester" environment. I should probably update my namecoin example to use this instead of transactions.Transaction, etc.
- I don't know how to pass "strings" anymore. The only data type is bignums of some kind. Strings can probably be converted via rlp.encode or something


