namecoin_code = """
def register(k, v):
    if !self.storage[k]: # Is the key not yet taken?
        # Then take it!
        self.storage[k] = v
        return(1)
    else:
        return(0) // Otherwise do nothing
"""

### The following is copied from Eth
import rlp
import tempfile
import pyethereum.utils as utils
from pyethereum.db import DB as DB
from pyethereum.config import get_default_config as _get_default_config
__TESTDATADIR = "../tests"

tempdir = tempfile.mktemp()

def new_db():
    return DB(utils.db_path(tempfile.mktemp()))

def new_chainmanager(genesis=None):
    return get_chainmanager(db=new_db(), genesis=None)

def get_chainmanager(db, genesis=None):
    # creates cm with db or new
    import pyethereum.chainmanager as chainmanager
    cm = chainmanager.ChainManager()
    cm.configure(db=db, config=new_config(), genesis=genesis)
    return cm

def new_config(data_dir=None):
    cfg = _get_default_config()
    if not data_dir:
        tempfile.mktemp()
    cfg.set('misc', 'data_dir', data_dir)
    return cfg


### From here is pasted together from earlier version of pyetherem

import serpent
from pyethereum import transactions, blocks, processblock, utils

#processblock.print_debug = 1
from pyethereum import slogging
slogging.set_level('eth.tx',"DEBUG")

code = serpent.compile(namecoin_code)
key = utils.sha3('cow')
addr = utils.privtoaddr(key)
genesis = blocks.genesis(new_db(), { addr: 10**18 })
tx1 = transactions.contract(nonce=0,gasprice=10**12,startgas=10000,endowment=0,code=code).sign(key)
result, contract = processblock.apply_transaction(genesis,tx1)
print genesis.to_dict()
tx2 = transactions.Transaction(nonce=1,gasprice=10**12,startgas=10000,to=contract,value=0,
                               data=serpent.encode_abi(0,1,45)).sign(key)
result, ans = processblock.apply_transaction(genesis,tx2)
serpent.decode_datalist(ans)
#print genesis.to_dict()
