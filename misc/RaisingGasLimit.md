
## Gas limit adjustment

The amount of gas allowed in a block is limited to some bound, which is a function of the previous blockchain. However, this limit changes over time.

The limit is changed according to an exponential average over a window of previous blocks, of the _actual_ gas used in a block: the maximum amount of gas allowed in a block is `1 + 1/5` of the previous average of blocks.

If miners always use the maximum amount of available gas, then the limit will gradually rise. There are two reasons why honest miners would want to use less than the maximum amount: 1) if the user demand for transactions is met, and there are simply not enough paying transactions circulating in the network to reach the limit, and 2) if more transactions are available, but the profit they offer does not offset the risk of being orphaned (or penalized, in this case of GHOST) due to the extra time necessary for other miners to verify the block.

However, dishonest miners can simply _pad_ their blocks by adding extra transactions that perform useless cycles or exit with an exception. In fact, transactions that consume gas by exiting with an exception do not incur much extra verification cost, so this padding is effectively costless to a miner.

Vitalik suggested the following analysis: if a fixed fraction `A<1`of the miners are honest and agree on a value `F` for the true gas usage of the block, then it reaches a fixpoint when `E = (1-A)*(6/5 E) + A*F`. This is solved when `E = F * (5*A)/(6*A - 1)`. Effectively, a fixed fraction of dishonest miners can only increase the block gas limit by some fixed factor. However, the lack of any strong disincentive against padding means that even ordinary miners may be easily seduced into raising the block limit arbitrarily.

This could potentially be mitigated by altered schemes such as permanently 'burning' some portion of the ether that users pay for their transaction gas, rather than giving the entirety of this ether to the miner. This burn rate should be decoupled from the gas price, as otherwise users could pay miners out-of-band to include transactions with a lower gas price. On the other hand, if there were a fixed hard-coded parameter that relates the number of gas units consumed to a price in ether, then that would imply some fixed prediction of ether price rather than allowing it to float according to a market processs. Thus any effective 'burning' mechanism would seem to need yet another dynamic adjustment mechanism, which would require further incentive analysis.

_Recommendation: further research mechanisms that discourage miners from 'padding' their blocks to raise the gas limit_

### Scenarios where the gas price can be altered

Effectively, the following contract would be an in-band way to bribe miners to increase the block limit.

Suppose the following "finicky" contract is created (but ignore for now the potential motivations for creating such a contract). We'll look just at the incentives of people responding to it.

```python
# Contract: "finicky"
def check():
    return self.storage[0]

def finicky():
    # This function expects to be called with a high
	# amount of gas, more than it will typically use
	if tx.gas < 10000: invalid()
	if self.storage[0] == -99:
	    # if conditions are right, send some nice
		# ether to the sender, and reufnd the gas
    	send(msg.sender, 100, gas=0)
	else:
	    invalid()
```

```python
# Contract "conservative":
def conservative():
    # This spends a MINIMUM of 50 "REAL steps" (due to loop optimization)
    # and a MAXIMUM of 100 "REAL steps"
    # It consumes a minimum of 500 gas and a maximum of 1000 gas.
    # Thus it's profitable if the gasprice is 0.1x the market rate.
    # The user has to send an up-front gas of 10000 of gas in order
	# to placate the "finicky" contract, even though only 1000 gas will
	# be spent. (The capital cost of this is mitigated by the 0.1x gas price).

    # Assume this is called with 10000+1000 gas.
	initial = tx.gas
	a = contract1.check()
	if (a != -99):
    	# The conditions aren't good! Reward the miner, but don't send
		# anything. This gives the miner 500*gasprice, but only uses 1
		# step due to optimization
		while initial - tx.gas < 500: pass
		return(0)
	else:
	    # The conditions are good!
		contract1.finicky(gas=10000)
		# We can count on a 10000 refund. Give the miner 1000
		while initial - tx.gas < 1000: pass
```

```
# Contract "crashy"
def burn():
    invalid()
```

## Code for creating bad storage layout, and abusing deletions

```python
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
	with i = 0:
	  while i < 16*16:
	    self.storage[i] = v
		i += 1
```
