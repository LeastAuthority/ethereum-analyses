import graphviz
from pyethereum import trie, tester, utils

s = tester.state()
t = trie.Trie(s.db)

def zpad(s): return '\x00'*(32-len(s))+s
def zpadr(s): return s+'\x00'*(32-len(s))

def bad(n=21):
    # Build n levels
    t = trie.Trie(s.db)
    accum = ''
    for i in range(n):
        for j in range(1,16):
            k = accum + '%X'%j
            if len(k) % 2 != 0: k += '0'
            k = zpadr(k.decode('hex'))
            print k.encode('hex')
            t.update(k,utils.sha3('cow'))
        accum += '%X'%0
    k = zpadr(accum.decode('hex'))
    t.update(k,utils.sha3('cow'))
    return t

for i in range(20):

    v = str(i)
    #k = zpadr(str(i))
    k = zpad(str(i))
    #k = str(i)
    #k = utils.sha3(str(i))
    t.update(k,v)

def traverse(t):
    def _traverse(node, accum):
        if t._get_node_type(node) == trie.NODE_TYPE_BRANCH:
            print 'BRANCH', node
            for i,k in enumerate(node[:16]):
                if k == trie.BLANK_NODE: continue
                if isinstance(k, list): print 'plain'
                else: print 'hash'
                _traverse(t._decode_to_node(k), accum+[i])
        elif t._get_node_type(node) == trie.NODE_TYPE_EXTENSION:
            print 'EXTENSION', node
            assert isinstance(node, list)
            _traverse(t._decode_to_node(node[1]), accum+trie.unpack_to_nibbles(node[0]))
        elif t._get_node_type(node) == trie.NODE_TYPE_LEAF:
            #print accum, node[0]
            k = trie.nibbles_to_bin(accum+trie.without_terminator(trie.unpack_to_nibbles(node[0])))
            v = node[1]
            print 'LEAF', k.encode('hex'),v
    _traverse(t.root_node, [])

def hexnibbles(nibbles): return ''.join(chr(_).encode('hex') for _ in nibbles)

def trie_to_dot(t):
    dot = graphviz.Digraph(format='png')
    i = 0
    def _traverse(node, accum):
        global i
        if t._get_node_type(node) == trie.NODE_TYPE_BRANCH:
            mynode = str(i); i += 1
            dot.node(mynode,'B')
            print 'B', mynode
            for j,k in enumerate(node[:16]):
                if k == trie.BLANK_NODE: continue
                child = _traverse(t._decode_to_node(k), accum+[j])
                if isinstance(k, list): 
                    dot.edge(mynode,child,'%X'%j,style='dashed')
                else:
                    dot.edge(mynode,child,'%X'%j)
            return mynode
        elif t._get_node_type(node) == trie.NODE_TYPE_EXTENSION:
            mynode = str(i); i += 1
            print 'EXT', mynode
            dot.node(mynode,'EXT')
            assert isinstance(node, list)
            child = _traverse(t._decode_to_node(node[1]), accum+trie.unpack_to_nibbles(node[0]))
            dot.edge(mynode,child, hexnibbles(trie.without_terminator(trie.unpack_to_nibbles(node[0]))))
            return mynode
        elif t._get_node_type(node) == trie.NODE_TYPE_LEAF:
            mynode = str(i); i += 1
            print 'L', mynode
            k = trie.nibbles_to_bin(accum+trie.without_terminator(trie.unpack_to_nibbles(node[0])))
            v = node[1]
            #dot.node(mynode,k.encode('hex'))
            dot.node(mynode,'')
            print 'LEAF', k.encode('hex'),v
            return mynode
    _traverse(t.root_node, [])
    return dot
