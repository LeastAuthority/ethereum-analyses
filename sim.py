# Illustration of the effectiveness of storing a fixed fraction of the Dataset
#
# Suppose we can only fit P <= 1 of the Dataset on the GPU.
# Consider the following family of strategies, indexed by a parameter S < ACCESSES:
#
#  attempt(puz, nonce):
#    mix = hash(puz, nonce)
#    ind = mix % len(dataset)
#    for i = 1 to S:
#       if ind is in the set stored on the GPU:
#           mix = hash(mix, dataset[ind])
#       otherwise: 
#           return None # try again!
#
#    for i = S to ACCESSES:
#       ind := next_index()
#       if ind is in the set stored on the GPU:
#           mix = hash(mix, dataset[ind])
#       else:
#           mix = hash(mix, compute_dag_element(cache, ind))
#           # Almost done, so stick it out! Compute the hard way!
# 

ACCESSES = 64
DAG_PARENTS = 1024
C1 = 1024.
C2 = 1.

"""
pi = probability of being in state i

p2 = P * p1
p3 = P * p2
...
pS = P * pS-1
pS1 = pS
pS2 = pS
pS3 = ....
pA = pS

pS = P^(S-1) * p1
p1 = (1-P) * (p1 + p2 + p3 ... pS) + pS
p1 = (1-P) * (1 - (A-S)*pS) + pS

Solve:
  pS = -(P^(S+1) - P^S) / ( (P^(S+1) - P^S) * S - A * P^(S+1) + (A-1) P^S + P )

Average Cost:
  C1 * (A-S) + (C2*P + C1*(1-P)) * S
Effective cost:
  cost * 1 / pS
"""

def cost_of_strategy(P, S):
    A = float(ACCESSES)
    pS = -(P**(S+1) - P**S) / ( (P**(S+1) - P**S) * S - A * P**(S+1) + (A-1) * P**S + P )
    cost = C2 * (1 - (A-S)*pS) + (C2*P + C1*(1-P)) * (A-S)*pS
    return cost / pS
    
def best_strategy(P):
    best = -1
    best_s = float('inf')
    for i in range(1,65):
        s = cost_of_strategy(P,i)
        if s < best_s:
            best = i
            best_s = s
    return best

def do_plots():
    global ps, bests
    ps = np.arange(0,1,0.01)
    bests = np.array([best_strategy(p) for p in ps])
    figure(1); clf()
    plot(ps, bests, 'k-')
    title('Optimal hybrid mining strategy')
    xlabel('P (probability of Dataset hit)')
    ylabel('S (hashimoto iteration of no-return)')
    figure(2); clf()
    costs = [64./cost_of_strategy(p,best) for (p,best) in zip(ps,bests)]
    plot(ps, costs, 'k-')
    title('Efficiency of optimal mining strategy')
    xlabel('P (probability of Dataset hit)')
    ylabel('Mining efficiency')
