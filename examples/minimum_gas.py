mingas_code = """
def doWork(a,b):
   # Do some silly irrelevant work
   i = a
   j = 1
   while i <= b:
      j *= i
      self.storage[a] = j
      i += 1
   return([j,tx.gas]:arr)

// A transaction that calls "main" is guaranteed to produce at least mingas for the miner
def main(mingas):
    // Store the original input gas
    gaslimit = tx.gas

    // Do the real 'work' by creating a new message (to the same contract)
    a = self.doWork(10, 15, gas=tx.gas-50, outitems=2)

    // If not, busy loop until we spend at least mingas
    while (gaslimit - tx.gas < mingas):
       continue

    return([a[0],a[1],tx.gas]:arr)
"""

import serpent
from pyethereum import tester, slogging, processblock
reload(tester)
from pyethereum import slogging

slogging.set_level('eth.tx',"INFO")

s = tester.state()
c = s.abi_contract(mingas_code)

slogging.set_level('eth.tx',"DEBUG")
tester.gas_limit = 10000
# Make a transaction that *SELF-EVIDENTLY* spends *AT LEAST* 5000 gas and at most 10000
o1 = c.main(5000)
print o1

print s.block.to_dict()
