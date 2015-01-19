# Appendix

## Summary of mitigations made in response to our recommendations

<!-- 1. Ethash parameters. -->
<!--     30000 blocks per epoch, 2**23 bytes of growth per epoch. This is still 730 MB per year. 2GB graphics cards will be unusable in around 16 months from launch. -->

<!-- https://github.com/ethereum/ethash/blob/b5e1bd68065b97213f8b5f884cf1b24e2d4357cd/src/libethash/ethash.h#L31 -->

1. In case of an exceptional halt, we recommended reverting the value transfer, so that the caller keeps the value rather than the callee.

  The recommendation was accepted. It is fixed in the pyethereum code simply by taking a ‘snapshot’ at an earlier line, before applying the value transfer to the state.
	https://github.com/ethereum/pyethereum/tree/d6211f7825ed9379a598e1863e17a5fbc700bacc/ethereum/processblock.py#L219
  It is fixed in the yellow paper by reverting the state to `sigma` instead of `sigma_1` as it was previously, where `sigma` is the state preceeding the value transfer and `sigma_1` is the state immediately after value transfer.

2. We observed that the contract storage trie can be manipulated to incur worst case costs. The simplest proposed fix was accepted, which is to store values by the hash of the key rather than the key directly. This means that attempting to induce a worst-case layout would require finding partial hash collisions.

    In Pyethereum this is fixed by adding a wrapper SecureTrie around the existing Trie, which maps `k` to `H(k)` before storing a value in the underlying trie.
	https://github.com/ethereum/pyethereum/tree/d6211f7825ed9379a598e1863e17a5fbc700bacc/ethereum/securetrie.py

3. We recommended increasing the gas cost for storage operations, and changing the "clear storage" operation to have the same base cost as "modify storage" but with a larger gas refund.
 
   The gas schedule for storage operations overall was increased by a factor of 10. For example, the cost of modifying a storage value is 5000, up 10x from 500. Setting to zero now also costs 5000, but there is a refund of 15000, so the same relative "net" costs are the same as before.
https://github.com/ethereum/pyethereum/blob/d6211f7825ed9379a598e1863e17a5fbc700bacc/ethereum/opcodes.py#L84

4. We pointed out that although the gas limit per block is intended to update based on utilized gas, if miners wished to "inflate" the gas value they could do so through contriving transactions that consume lots of gas but actually do not take much time to execute.

   The gas limit update rules have been modified so that "inflating" the gas value can be done explicitly, without needing to contrive transactions. This is achieved by allowing each miner to choose his gas limit within a range determined by the previous block's gas limit. By default, honest clients choose a limit that matches exactly the gas they use.
https://github.com/ethereum/pyethereum/blob/d6211f7825ed9379a598e1863e17a5fbc700bacc/ethereum/blocks.py#L559
     
    We note that the range expression remains slightly biased. For example, the next block can increase by a factor of up to `1.0009765625`, but it can decrease by a factor of `1.0009775171065494` (they differ in the 10th decimal place). This is mitigated however because the difference is small, the absolute value of the change is restricted to the "floor" of this ratio, and there is a hardcoded floor limit.

<!-- ## Concerns not addressed -->

<!--  1. Miner bomb. -->
<!--   (TODO: How mnuch did we agree the storage could increase by?) -->
   
<!--  2. An opcode for inspecting the stack. -->
<!--    However the workaround we provide is effective enough. -->

<!--  3. Changes to the yellowpaper? -->
<!--   (TODO: We either need to make a more specific recommendation about the yellowpaper or tone down our complaints about it) -->
