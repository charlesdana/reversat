def read_sat(fname):
    with open(fname, "r") as f:
        lines = f.readlines()
    SAT = [[int(c) for c in line.replace("\n", "").split(" ") if len(c) and int(c)] for line in lines if len(line) > 0 and not line[0] in "pc"]
    return SAT

def reversat(SAT, VARS, show=False):
    if show:
        print(SAT)
    VTH = []
    NUM_CLAUSES = len(SAT)
    m = 1
    while 2**m < NUM_CLAUSES:
        m = m + 1
    for idx in range(len(SAT)):
        clause = SAT[idx]
        for l in clause:
            bnr = "0" * (m - len(bin(idx).replace("0b",""))) + bin(idx).replace("0b", "")
            VTH += [[-l] + [(VARS + k + 1) * [-1,1][int(bnr[k])] for k in range(len(bnr))]]
    idx = len(SAT)
    while idx < 2**m:
        bnr = "0" * (m - len(bin(idx).replace("0b",""))) + bin(idx).replace("0b", "")
        VTH += [[(VARS + k + 1) * [-1,1][int(bnr[k])] for k in range(len(bnr))]]
        idx += 1
    if show:
        print(VTH)
    return VTH

def copy_sat(SAT):
    return [[l for l in clause] for clause in SAT]

from random import choice

def fail(VTH):
    ASSERT = []
    VTH = copy_sat(VTH)
    while len(VTH) > 0 and not [] in VTH:
        VTH = sorted(VTH, key=lambda X: len(X))
        clause = choice(VTH)
        x = -choice(clause)
        if len(VTH[0]) == 1:
            x = -choice(VTH[0])
        ASSERT += [x]
        VTH = [[l for l in clause if not l == -x] for clause in VTH if not x in clause]
    if [] in VTH:
        return sorted(ASSERT, key=lambda x: abs(x))
    return -1

def guess_and_backpropagate(CRT, SAT):
    SAT = copy_sat(SAT)
    CRT = copy_sat(CRT)
    VARS = max((abs(x) for clause in SAT for x in clause))
    VTH = reversat(CRT, VARS)
    VARS = max((abs(x) for clause in SAT for x in clause))
    ret = fail(VTH)
    while ret == -1:
        ret = fail(VTH)
    ASS = [x for x in ret if abs(x) <= VARS]
#    if len(ASS):
#        ASS = [choice(ASS)]
    NEW = [[x] for x in ASS] + [[l for l in clause] for clause in SAT]
    NEW = sorted(NEW, key=lambda X: len(X))
    while len(NEW) and len(NEW[0]) <= 1:
        if len(NEW[0]) == 0:
            return [[]], ASS
        x = NEW[0][0]
        NEW = [[l for l in clause if not l == -x] for clause in NEW if not x in clause]
        NEW = sorted(NEW, key=lambda X: len(X))
        if not x in ASS:
            ASS += [x]
    return NEW, ASS

def run(SAT):
    L = len(SAT)
    NEW = copy_sat(SAT)
    ASS = []
    while len(NEW) and not [] in NEW:
        NEW, ADD = guess_and_backpropagate(NEW, SAT)
        ASS = ASS + [l for l in ADD if not l in ASS]
        ASS = sorted(ASS, key=lambda x: abs(x))
        print(f"LEN[{len(NEW)}/{L}];ASS[{len(ASS)}]", end="             \r")
    print(f"FINAL[{not [] in NEW}]               ")
    if [] in NEW:
        return -1
    return ASS

import sys

if __name__ == "__main__":
    if len(sys.argv) == 1 or not ".cnf" in sys.argv[1]:
        SAT = [[-1, 2], [2, -3], [-2, -3]]
    else:
        SAT = read_sat(sys.argv[1])
    print("--BGN--\n" + "\n".join([str(clause) for clause in SAT]) + "\n--END--") 
    ret = run(SAT)
    while ret == -1:
        ret = run(SAT)
    print(f"Solution: {ret}")
