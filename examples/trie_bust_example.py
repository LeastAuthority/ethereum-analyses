# The goal of this test file is to see how to incur the worst-case cost for storage operations

triebust_code = """
def init():
   # This fills up the trie in the worst possible way. 
   # The target key is '0'. Consider the path to the target key after initialization.
   # Every node on this path is a "BRANCH", which contains 16 hashes (no patricia compression, 
   # and no inline nodes). Accessing the target index thus incurs the worst-case cost.
   accum = 16*16
   v = sha3('cow')
   self.storage[0] = v
   with i = 0:
      while i < 62:
         with j = 1:
            while j < 16:
               k = accum*j
               self.storage[k] = v
               j += 1
         accum *= 16
         i += 1
         # Fill some nonzero elements at the bottom
      i = 0
      while i < 16*16:
         self.storage[i] = v
         i += 1

def waste_steps(n_):
   with n = n_:
     with i = 0:
       while i < n:
          self.storage[i] = 0  # These steps are cheap
          i += 1
       invalid()               # Revert the state by throwing exception
       return(1)

def waste_steps_outer(n):
   i = 0
   while i < n:
      #pre = tx.gas
      self.waste_steps(16*16,gas=200+16*16*16)   # Call the time_waster in a loop
      #post = tx.gas
      #return([pre,post,a]:arr)
      i += 1
   return(1)
"""

import serpent
from pyethereum import transactions, blocks, processblock, utils, tester, trie

#processblock.print_debug = 1
from pyethereum import slogging
slogging.set_level('eth.tx',"DEBUG")

s = tester.state()
tester.gas_limit = 500000
c = s.abi_contract(triebust_code)
trie.AMLOG_COUNTS['TOUCH_BRANCH_NODE'] = 0
tester.gas_limit = 200000
o1 = c.waste_steps_outer(35)
print o1

print "Expected:", 16*16*35*64
print "Counted:", trie.AMLOG_COUNTS['TOUCH_BRANCH_NODE']

print s.block.to_dict()

