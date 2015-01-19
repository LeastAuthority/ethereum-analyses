# An illustration of why the crowdfund example is broken
# https://github.com/ethereum/serpent/blob/develop/examples/crowdfund.se#L32 

dummy_code = """
invalid()
"""
test_code = """
def test(x):
    a = send(x, 0) // Send 0 value to recipient
    return(55) // a crashes and uses all the gas, so this transaction fails
"""
import serpent
from pyethereum import transactions, blocks, processblock, utils, tester, trie, slogging
slogging.set_level('eth.tx',"DEBUG")
tester.gas_limit = 400000

s = tester.state()
c = s.abi_contract(test_code)

c1 = s.contract(dummy_code)

o1 = c.test(c1)
print o1
