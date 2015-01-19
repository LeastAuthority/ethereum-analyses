sha3_code = """
def test():
   i = 0
   x = 'cow'
   while tx.gas > 100:
      x = sha3(x)
      i += 1
   return([i,x]:arr)
"""
import serpent
from pyethereum import transactions, blocks, processblock, utils, tester, trie, slogging
slogging.set_level('eth.tx',"DEBUG")
tester.gas_limit = 400000

s = tester.state()
c = s.abi_contract(sha3_code)

o1 = c.test()
print o1


