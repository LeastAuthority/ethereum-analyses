Ethereum Analysis: Gas Economics and Proof of Work
Andrew, Warner, Nathan

Notes go here

* can contracts forge messages to make them look like they came from keys? and vice versa? probably not, contract-ids are hash outputs. miners can also distinguish between externally-delivered (signed) messages and internally-generated (from-contract) messages.
* contracts which use input parameters (argument values) directly as memory keys, or sender-keys as memory keys, might allow collisions (like memory-corruption/buffer-overflow attacks).

  * what is the memory model for persistent storage? integer-offset? key-value pairs? is that a Serpent feature that compiles down? if serpent does the utility/hash function incorrectly, this would admit an attack. e.g. first-come/first-served name assignment contract, tracks one data structure with user-assigned names, a second for internal use, they might collide. Find a contract in the wild that behaves this way, analyze it.
 
 
## goals for 02-Feb-2015

* be comfortable with compiling both go- and cpp-ethereum
* have all ethereum unit tests working and understood
* ethtest working and understood

## goals for 09-Feb-2015

* write a new test case for ethtest, have it work
* understand testing with pythereum
* understand higher-level contract languages and compilers: Serpent? Solidity?
* understand ecosystem: which languages (high and low) are in use, how mature are they, which UI projects are active (mist, in go? web-browser in cpp-client?)

## Brainstorm thoughts from 2015-02-02

Is ``currentcoinBase`` a parameter available to scripts? Can they distinguish which coinbase (or miner) is currently attempting to verify the script?

Scenario: a miner colludes with a contract author, and the contract provides some useful service that has many users/transactions, and the general public doesn't inspect the code for sneakiness, then: the miner can decide whether or not to insert a special coinbase in order to hit an infinite loop, preventing any state transition within the contract, but receiving all of the gas from the sender.  The miner need not actually execute the loop, thereby receiving the gas.

Potential DOS: what if a malicious miner doesn't need to evaluate a very high cost transaction because of a priori knowledge, and sends themselves a transaction but doesn't evaluate it. E.g. a brute-force search for a (short) hash preimage: the attacking miner can recognize the computation and fill in the result very cheaply, but other miners must perform the whole computation. Gas reward is the same, but actual CPU spent is quite different.

This is one particular way for clients to pay miners "under the table" (they could also just send them cash, completely outside the system) for preferential treatment. Miners can be bribed by either giving them more money, or letting their operations be cheaper.


### Mining Economics

Rational miners want to know how much profit they're likely to make. When a transaction arrives, they want to know how much it will cost them to verify, and how much money they'll make from it. Their costs are measured in CPU cycles (which could be put to other uses), storage space, etc, and eventually in the dollars needed to provide these. Their return is measured in ETH or, eventually, dollars.

They need to perform this evaluation quickly and cheaply, because they'll be doing it for every potential transaction that arrives, even the bad ones. This step cannot afford to run the program; it can only look at simple values from the message metadata like "gaslimit" and the program size.

The gas limit bounds these potential values into a rough rectangle like this:

![mining profit diagram](./images/mining-profit-1.png)

The maximum reward is capped by the gaslimit and gas price: all other potential reward pathways (e.g. the transaction might explicitly send more ETH to the coinbase address) require in-depth analysis of the transaction. The reward is bounded from below by the size of the message (since each byte costs gas).

The runtime is unknowable in advance. The Halting Problem tells us that we can't hope to determine the runtime of an arbitrary program (in a Turing-complete language) without actually running it. However, the gas system provides an escape clause: if the program takes too long, the miner is allowed to give up and *keep the gas*. This gives an incentive to clients to set accurate gas limits.

In practice, the likely outcomes look more like these:

![mining profit diagram](./images/mining-profit-2.png)

The top edge consists of programs which forfeit their entire gas budget. The cheapest such program (for the miner) is one that raises an exception on the very first instruction, using very little CPU. Exceptions later in the program consume more CPU time but yield the same rewards. Finally, programs which trigger an Out Of Gas error consume the most CPU.

If the per-opcode gas prices accurately model the real CPU costs, non-erroring programs will live along the middle (blue) diagonal line, and costs will be proportional to rewards. Since unused gas is returned to the sending account, the miner may get very little reward (for a program that finishes quickly, with a successful exit code), even though the gas limit is high.

The opcode prices are a rough estimate of the miner's actual CPU costs. The actual cost is a complex function of the program trace. The hope is that counting the execution of each opcode, and applying a price (in gas) to each, will result in something close enough to reality to allow miners to make good decisions.

If we assume this linear model is accurate, but the actual opcode prices may be wrong, then programs may cost more or less than their gas consumption would indicate. For example, http://gavwood.com/Paper.pdf says a SHA3 operation costs 10 gas, but a basic addition step costs 1. A clever JIT compiler can probably turn that addition into a single machine instruction, whereas the SHA3 will cost hundreds or thousands (depending upon the input size). If we assume that addition is the "correct" baseline, then SHA3 is probably quite underpriced. A program that uses a lot of SHA3 opcodes will take a lot of CPU to run, despite spending relatively little gas. On the other side, supposing the `Gsset` scalar (paid for an SSTORE operation that allocates space), set to 300 gas, is too high. A program with lots of these "overpriced" opcodes will consume more gas (giving more reward to the miner) without actually consuming a lot of CPU resources.

### gas predictability

In Bitcoin, the block chain is an append-only graph of precisely-interlocking transactions. When a client sends a transaction, they know exactly where it ought to fit and what the results will be. If anything has changed since they built the transaction, it won't fit, and they'll need to build a new one with updated ancestors. This is maximally predictable, but imposes constraints on the transactions and the state which they modify, because otherwise it may be hard to keep up. A transaction that says "Alice's balance changes from $25 to $75" cannot be composed with "$25->26" to give Alice $76: the second sender loses and must write a new one that says "$75->76".

Ethereum allows transactions like "Alice += $50", whose results depend upon the order in which the transactions are applied. This establishes a spectrum, with one end where transactions are maximally predictable, and the other in which they're more likely to complete. This is closely related to the CAP theorem (where "predictable" is like Consistent and "likely to apply" is like Available).

In the maximally-predictable end of this spectrum, one way of looking at the gas system is that clients are expected to simulate their proposed transactions before submitting them to miners, to ensure they will succeed, and in doing so they will produce an exact program trace (including which opcodes are run and what storage is needed). Statically-evaluatable information about this trace can be included in the message metadata, which the miner can use when making their profit/loss and prioritization decisions. The client knows precisely what will happen and what state will result, and the miner simply needs to verify that they did their work correctly. Such a system would give the miner the most information, and would let them bound the uncertainty even more precisely: the client could include a hash tree of the program trace (execution steps and evolving state are the leaves, Merkle chains are included inline, and the transaction is identified by the root), and the miner could terminate execution with one leaf/block after the trace diverged from the client's claim.

But that level of predictability comes at a high cost. Either Ethereum clients would need to follow the state of the entire dataset carefully (to make accurate predictions), or tolerate frequent reject/retry cycles, or perform complex analysis to determine which parts of the state might affect their transactions and which can be ignored. Ethereum's current design only requires senders to remember their own nonce and balance, so basic value transfers ("send $50 to Alice") don't require careful coordination. Gas limits are an an intermediate solution.

In addition to race conditions that modify contract state at surprising times, the execution trace (and thus total gas spent) can also be influenced by the miner (the `COINBASE` opcode), and by the program's execution itself (the `GAS` opcode).

### miner profit calculation

Miners are being paid for their time, and for their risk. It would be nice to separate the two.

Ideally, clients would give the following data/claims to miners for each transaction:

* if you publish an EOUTOFGAS proof for this txn, you will get A (ETH)
* if you publish a sucessful run for this txn, you will get B ETH
* I claim it will cost you C ($/CPU/etc) to run this program

From the client's point of view, "A" is their bet

Miners compare A against C to decide whether the worst case (an infinite loop) would still make them a profit, and outright reject any in which A-C is a loss. They might then prioritize remaining transactions in which B is highest, knowing their profit will be at worst B-C and at best B-0 (where the program ran faster than C, which is allowed in this non-rigid model).

![mining profit diagram](./images/mining-profit-3.png)

From the client's point of view, A is what they must pay for the miner's risk, and B-A is paid for the miner's time. A client which can accurately predict its gas usage can afford to offer A=B or even A>B.

Current Ethereum messages do not guarantee a minimum reward: a program which finishes quickly will refund most of its gas to the caller.

### other notes

Signalling "A" and "B" might be possible within the existing language. To guarantee delivery of "B" (where A==B==gaslimit), miners could reject any program that doesn't have a stereotypical epilogue that sends almost all of the program's remaining gas to a well-known infinite-loop contract (forfeiting the subroutine's gas to the miner), then catches and ignores the EOUTOFGAS return, then exits. For A>B, the epilogue would send some-but-not-all of the remaining gas to the subroutine. However, this would be a retreat from Ethereum's ideal of generalized execution.

Verification economics assume that both mining rewards and verification costs are uniformly distributed among miners. Rewards go to only the winning miner, but all of them pay verification costs. If one miner has an efficiency advantage because of out-of-band information, this may skew rewards towards that miner. It's hard to distinguish between this form of "cheating" and one miner simply being smarter/faster/cheaper at performing the task of verification.

It may be useful to have tools which analyze potential subroutine contracts for dependencies upon unpredictable values like `COINBASE`. Authors who want deterministic results should not use such subroutines.

Miner's probability of success is also influenced by the size of the blocks they create (therefore how long it takes to transmit them outwards, to establish their claim), and the CPU costs to verify those blocks (spent by the other miners when they receive it). If the other miners are single threaded and only verify one block at a time, it doesn't matter, but an overenthusiastic miner might receive an alternate (smaller) block while it is verifying your larger one, and give up on your block in favor of the small one. This is clearly a Schelling question: miners care most about what other miners are going to do. We currently expect proof-of-work time to dwarf verification time, but maybe not (especially of Ethereum uses proof-of-stake instead). The per-block `GasLimit` caps the total verification effort.

Packing transactions (of various sizes) into a block is NP-complete (subset-sum). Choosing which transactions to verify based upon their expected runtime is too (also subset-sum, denominated in CPU cycles rather than bytes).

### other attacks/concerns

Trie structure could be attacked: specific series of storage opcodes that result in a lopsided tree. SSTORE opcodes would not be priced correctly.

SUICIDE opcode in nested calls: implementations might easily get it wrong, and apply it right away (instead of treating it as part of the per-stack-frame state that might get rolled back or merged to the calling frame). If A calls B which calls A which uses SUICIDE, what happens when the enclosing A gets control again? If the nested A changes state (expecting it's about to be deleted), does the outer A see those changes?

I wish the SUICIDE opcode were spelled "DESTRUCT" or something less morbid.

To de-incentivize storage, you pay a lot to allocate a new location, and get a refund for freeing it. You store "0" in a slot to free it (contract storage is sparse). This isn't a good match for the computation costs to manage this storage: the cost of locating the right node (to determine if the cell is present or absent) is independent of the non-CPU cost to retain that data for the future. We'd prefer a more direct bytes*seconds cost metric, although that might be impractical for other reasons (like how to manage maintenance costs).

Proof-Of-Work: we skimmed https://github.com/ethereum/wiki/wiki/Ethash . We haven't studied it in detail yet, but so far we're concerned about:

* the number/variety/complexity of functions involved
* suggestions that parameters will be tuned based upon a Javascript implementation, rather than the most-likely-efficient GPU version
* lack of clarity about target platform: both Javscript *and* GPUs?
* 32MB is still a lot for JS.
* we like the Cuckoo (random-graph-cycle) hasher, I wouldn't mind seeing it here instead

## Notes from 04-Feb-2015

Miners could put the exact gas used in their published txns, verifiers could reject their blocks if it took more or less time than they claimed. The "gasUsed" block property is a sum of these, which is probably good enough. Verifiers should abandon verification when the total cycle count goes above gasUsed, or the individual txn's count goes about its (sender-provided) gasLimit, whichever happens first. Verifiers cost is bounded by gasUsed. The miner has enough flexibility to lie slightly (allocating claimed gas used from one txn to the wrong one), but can't overrun the overall total, which is all the verifier really cares about.

amiller is unconvinced that we need distinct A (payout for completion) and B (payout for EOUTOFGAS). We agreed that some EOUTOFGAS rewards is necessary. It all comes down to the reward-vs-cost rectangle and where the "Line Of Profit" falls.

Some cost is incurred before the miner even gets to look at the transactions: these are uncompensated and we can only hope that they'll be small enough to not matter (basic spamming, network bandwidth, storage/parsing costs before evaluation happens). The Gtransaction fee (500gas) provides a minimum reward for all accepted txns. The miner wants to determine profitability.

Why prioritize txns? At low volumes, the only constraint is a lack of txns to work with, so miners won't prioritize, they'll just want to avoid unprofitable txns. At higher volumes, one of the following constraints or costs will start to matter:

* block size limit (in bytes)
* per-block gasLimit
* time to send the block over the network
* time for other miners to verify the block
* CPU time spent verifying (competing with mining, or costing $)

The miner must choose which txns to evaluate at all, based on expectations of CPU cost and gas reward. They may have some clever static-analysis that allows them to estimate CPU cost before actually running the script. Once run, they'll know the exact reward for that block.

After evaluating the txns, constraints may lead the miner to not include every profitable txn, so they'll want to choose a subset that maximizes their profit. The optimal subset is hard to find: there are O(2^N) possible choices, each txn has a set of attributes (size, reward, network cost, other-miner verification cost), which combine to form some total cost function. The total reward is a simple linear sum, but the other costs may be non-linear.

Some partial solutions are cheaper. For example, if the block size is the main constraint, and all txns are of equal size, then clearly one should choose the most profitable subset (gas reward minus CPU cost). If the txns are all of equal profit, then one should choose the smaller txns (to fit more of them into the size-limited block). If they vary in both aspects, the NP-complete subset-sum problem appears.

Miners with lots of extra CPU may improve profits by reordering txns into sequences that consume more gas (and therefore grant more reward to the miner). Contracts which terminate early (perhaps because their preconditions are not met) are less profitable. One can imagine an enthusiastic miner which tries all O(N!) permutations in search of ways to get contracts to do more work. Clever miners may be able to separate txns into "highly entangled" and "mostly isolated" bins that are more or less worth reordering. They might also keep track of data dependencies during a trial evaluation (a la Software Transactional Memory) to help this analysis.

### to refund or not: the fully-committed case

From the miners point of view, refunding unused gas is a drag. It adds one more uncertainty to the shape of the reward/cost diagram: the reward is variable, and can't be exactly determined without actually running the program (and incurring the CPU cost at least once). However the miner was already uncertain about the CPU cost.

For miners, the ideal situation would be that senders must pre-simulate their transactions and commit to exactly the amount of gas they will use. Txns which use any more (or less!) would forfeit their gas. This would collapse the reward/cost diagram to a small number of mostly-profitable:

* evaluate the txn and it uses the claimed gas: full reward, full cost
* evaluate the txn and it uses less: full reward, reduced cost
* evaluate the txn and it uses one cycle too many: full reward, full cost
* reject the txn: no reward, minimal cost

If the correct-gas case would be profitable, the miner evaluates the txn and gets the full reward. They might make even more profit than expected if the program errors with ELEFTOVERGAS, but wouldn't bank on that.

### fully-committed is a drag

However, to use fully-committed txns, senders would have to precisely pre-simulate their txns, which imposes a heavy burden on them. They must know the full state of every data store which might influence their program's execution. This includes unknowables like COINBASE. It would probably require an evaluation rule like "iff the state vector is still X, then add this txn, otherwise don't bother", which makes it hard to keep up. For low volumes, this might work, but at higher volumes many txns would be rejected just because of failed precondition checks.

So clients don't really want fully-commited txns, which means they can't predict their gas consumption. They'll have to guess. We can either say that excess gas is refunded, or the miner gets a flat rate. A flat rate means more pressure to guess accurately. Unpredictable CPU consumption introduces one axis of uncertainty (cost) for the miner. Refunding excess gas introduces a second axis (reward), but maybe it's not so bad given that we already can't predict the CPU consumption.

(imagine a gas-consumed insurance service: you give them a txn, they know more about the blockchain/state-vector than you, they guarantee that it will cost X gas, if they're wrong then they pay you a fee or some sort).

### other notes, needs expansion

exceptions are literally expensive: they cause all gas to be forfeit

test-and-set operations will want to return "success" (i.e. not throw an exception) even if their test is not met, to avoid forfeiting gas

what patterns will people use to get around limitations on the current design?

how much gas overhead is necessary for cleanup? subcontracts might check the gasRemaining and behave differently if there isn't enough, even though it's not used. Might always wind up with some gas remaining. Analogy to a visited country requiring your passport to be valid for at least 3 months after you leave, just in case.

amiller's serialized-execution/queue gadget: the crank must be turned by someone else, they must provide all the gas for everything that happens, but they hopefully get paid back by the gadget (send ETH to message-sender). Messy. Callback notifications cost gas: how to predict? Who pays for it?

Recommend (oh look! implemented already! not in yellow paper yet) try-catch for all exceptions on contract boundaries, else one contract can't protect its caller's gas against the subcontract.

close relationship between object-capability patterns (esp independence of separate objects) and subcontract patterns. eventual-send helps a lot, how to bring to ethereum? what would Promises look like? where would they live? in some sort of authenticated state vector? Look for analogues of objcap use cases: everything is easy until you get N>=3, grant-matcher, zebracopy.

the fact that contracts can't pay for their own execution is a big limitation, and maybe a big safety belt. it's like a mechanical machine where all the motion must derive from the human (key-based account) pushing the lever, no springs or use of stored energy allowed. Not self-sustaining, no lasers.


## 09-Feb-2015

Raw notes:

```
**** look at trie spec for HMAC-like pw-vs-H(pw) collision concern
***** also RLP
***** concern would be someone stores A (len(A)==32bytes) in the contract
      store, then also stores H(A). Also in the msg-in-block tree.
**** amiller's trie_bust_example
***** given a deliberately unbalanced contract-storage trie, zeroing out
      locations actually takes a lot of traversal time, but costs zero gas
***** one fix: instead of nonzero->zero = (cost=0, refund=100), change it to
      (cost=100, refund=200). Then you couldn't do a bunch of expensive gas=0
      writes followed by exception.
***** storage is still overpriced relative to sha3
****** trie requires a lot of SHA3 operations
***** what if STORE cost is variable? depending upon trie structure at the
      time?
****** probably too hard for clients to simulate
***** crowdfunding example
****** refund costs postage
****** sender should provide that postage
****** maybe sender can specify how much gas should be included in a refund
******* tricky because eth != gas
**** exceptions cause inbound funds to get stuck
***** need to predict exceptions with just as much accuracy as results
**** prediction + test vector + primer gas
***** incentivize the miner to be a queueing service
***** https://etherpad.mozilla.org/HmPuKifu2d
***** test vector as static data, or smaller program with its own gas, or
      analyzed from real program?
***** program does precondition check, then does X or Y based on the results
***** give higher reward to miner if Y happens
***** if miner knows about this, it will wait to apply until precondition is
      good
**** DoS (nathan)
***** imagine popular contracts with network effects: more useful as more
      people use them
***** but with data structures that cost more as they get bigger
***** so gas requirements grow over time
***** will they run into the per-block gaslimit?
****** not if it grows gradually: gaslimit is a moving average
****** although, imagine pathological lottery thing where the payout won't
       happen unless gaslimit>X
**** should we add an explicit BURN(gas) opcode?
***** call to a well-known INVALID() contract is equivalent
***** what about return_and_burn_remaining()
***** or an outer contract
****** args are (inner contract id, msg)
****** calls inner contract, then burns remaining gas, and returns rc
****** wouldn't be as transparent as we'd like
***** or a header flag that says "no gas refunds"
**** sections of the report
***** uncertainties about cost
****** unbalanced pricing (overpaid/underpaid opcodes)
****** leaky abstractions: unbalanced trie
****** shortcuts, precomputation (brute-force preimage search)
****** prefering one miner over another
******* probably not preventable
******* but what incentives will it produce?
***** uncertainties about reward
****** variable gas consumption
****** ways to signal minimum reward
******* burn_and_return() sequence
******* set zero gas and do explicit send to coinbase
******** 1st opcode: send to coinbase (with minimum reward)
******** 2nd opcode: call subcontract with gas=X (all remaining gas)
********* since exceptions do not propogate
******** either send-to-self (so money remains in the same account), or
         explicitly send all money to the subcontract. Or use CALLCODE.
******* intermediate contract
***** composability of subcontracts: somewhat in scope
***** proof-of-work
**** PoW
***** like password-hashing: attacker=miner vs defender=verifier
****** but fast verification is even more important than in password hashing
****** in PH no good guys should have to take a long time to do anything,
       whereas PoW requires miner to take a long time
****** also verification is on the critical path, so if it's slow it will
       increase the network latency, increase probability of orphaned blocks
****** verifier can be DoSed by bad PoWs
***** 32MB cache is a bit large/slow
***** 12s block time sounds crazy
****** miners will probably mine speculatively, while verification runs
****** GHOST: mining on stale blocks doesn't waste all work. partial penalty.
***** build a model: network delay, verification delay, PoW setup delay, mean
      PoW time, stale-block penalty, probability of valid block
****** if blocks are usually valid, mine on new block while verifying
****** but if not usually valid and stale penalty is low, mine on old block
****** maybe not directly actionable, but will help later analysts
***** need to understand the uncle penalty thing
***** large dataset changes once every 1000 blocks
****** just after that would be a good time for selfish mining, games with
       orphan stubs. Oh, but double-buffer seeds are supposed to prevent
       this, you have 1000 blocks of time to prepare your large dataset
***** not-really-BBS (3 instead of 2), weird
****** vitalik's claim: x^3 is injective, x^2 is not
***** "light" verification (just hash, not mix) requires the mix value (of
      H(s+mix)) is included in the block, rather than only being implicit
***** get_seedset() is defined weirdly, leaves out "front vs back" buffer
      selection, should be rewritten in terms of "current" vs "next"
***** overall: too much arithmetic, would feel better about straight hashing.
      verification seems too expensive. Would like Cuckoo PoW.
```

### amiller's check-precondition contracts:

```
// This is a "finicky" contract
contract1:
def check():
    return self.storage[0]
    
def finicky():
    // This function expects to be called with a high amount of gas, more than it will typically use
    if tx.gas < 10000: invalid()
    if self.storage[0] == -99:
        // if conditions are right, send some nice ether to the sender, and reufnd the gas
        send(msg.sender, 100, gas=0)
    else:
        invalid()
contract2:
def conservative():
    // This spends a MINIMUM of 50 "REAL steps" (due to loop optimization)
    // and a MAXIMUM of 100 "REAL steps"
    // It consumes a minimum of 500 gas and a maximum of 1000 gas.
    // Thus it's profitable if the gasprice is 0.1x the market rate. 
    // The user has to send an up-front gas of 10000 of gas in order to placate the 
    // "finicky" contract, even though only 1000 gas will be spent. (The capital cost 
    // of this is mitigated by the 0.1x gas price). 
    
    // Assume this is called with 10000+1000 gas.
    initial = tx.gas
    a = contract1.check()
    if (a != -99):
        // The conditions aren't good! Reward the miner, but don't send anything
        // This gives the miner 500*gasprice, but only uses 1 step due to optimization
        while initial - tx.gas < 500: pass
        return(0)
    else:
        // The conditions are good!
        contract1.finicky(gas=10000)
        // We can count on a 10000 refund. Give the miner 1000
        while initial - tx.gas < 1000: pass
contract crashy:
    def burn():
        invalid()
```


## Vitalik's current concerns:

```
* gas stuff
** price imbalances
** sha3 is stuck now, since the ethsale addresses use it
** gaslimit adjustment: miners could include articifial txns to push up gaslimit
** if we're near the gaslimit, miners don't care about how long it takes to verify, just how lucrative they are
* ghost/uncle-block-chain scorig
* DF adjustment: PoC8 is not ideal, working on better one
* PoW function
** e.g. if RNG only emitted 3 bytes, not 4, then you wouldn't have to store very much data, not memory-hard

* asm.js: 8s init, 100ms/block verify

* goal is to make GPU mining 30x?100x? faster than CPU, but not help ASIC
** make mining more accessible to humans, to botnets
** nice to have CPU mining be enough to send txn

* P2Pool, like a chain letter: you make a block that pays to the previous 100 blocks, expecting people in the future will do the same

* Vitalik: an asic is basically a highly leveraged option to buy bitcoin at some given electricity cost, which can go badly if the price drops
```

## Brian+Nathan 26-Feb

Intrinsic gas: nonzero script bytes cost 5x more than zero script bytes.
Would be more accurate-of-costs to charge by the RLP-compressed output. But,
would that make it impossible to exactly drain an account (unstable
equilibrium between modifying value in txn and the size of the compressed
representation of the txn?).

Why can't one contract read another contract's state? Feels better from an
objcap point-of-view, but the authors of messages get to read that state,
it's not a secret.

Current mechanism for extension functions (SHA256, RIPEMD160) is very manual.
Can it be improved? Miners wouldn't be inventivized to offer shortcuts (if
they earn more from high-gas manual implementations).

Yellowpaper variable-name/symbol choices are hard to read, would like to
annotate it with python-like pseudocode and less greek.
